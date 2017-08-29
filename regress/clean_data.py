# -*- coding: utf-8 -*-
import sys
import random
from collections import Iterable
# 第三方包
import pandas as pd
import numpy as np

investor_file = 'data/investor.csv'
company_file = 'data/company.csv'
view_file = 'data/view_com_820.csv'

def prefer_phases(frame):
    frame = frame.copy()
    phases_list = list(frame['prefer_phase'])
    min_list, max_list = [], []
    for row in phases_list:
        if type(row) == str and len(row) > 0:
            row = eval(row)
            if isinstance(row, Iterable):
                min_phase = min(row) - 5
                max_phase = max(row) + 5
            else:
                min_phase = row - 5
                max_phase = row + 5
        else:
            min_phase, max_phase = None, None
        min_list.append(min_phase)
        max_list.append(max_phase)
    frame['min_phase'] = min_list
    frame['max_phase'] = max_list
    return frame.drop('prefer_phase', axis=1)

def prefer_industry(frame):
    def pivot(data):
        data_dict = dict()
        for row, line in enumerate(data):
            data_dict[row] = dict()
            if type(line) == str and len(line) > 0:
                line = eval(line)
                if isinstance(line, Iterable):
                    for col in line:
                        data_dict[row][col] = 1
                else:
                    data_dict[row][col] = 1
        df = pd.DataFrame(data_dict).fillna(0)
        return df.T
    pre = pivot(frame['prefer_industry'].values)
    pre.columns = map(lambda x: 'pref_' + str(x), list(pre.columns))
    frame = pd.merge(frame, pre, left_index=True, right_index=True)
    return frame.drop('prefer_industry', axis=1)

investor_frame = pd.read_csv(investor_file)
investor_frame = prefer_phases(investor_frame)
investor_frame = prefer_industry(investor_frame)

company_frame = pd.read_csv(company_file)
view_frame = pd.read_csv(view_file)

def build_negative_smple(df_verge_attr_score, len_=1):
    expect_list = list(df_verge_attr_score.iloc[:, 0])
    job_list = list(df_verge_attr_score.iloc[:, 1])
    positive = set(zip(expect_list, job_list))
    negative = list()
    # 占用内存小的取样方法
    p = len_ * len(positive) / (len(expect_list) * len(job_list) - len(positive))
    i = 0
    for e in expect_list:
        for j in job_list:
            if (e, j) not in positive:
                if random.random() < p:
                    negative.append([e, j, 0])
                    if i % 100 == 0:
                        sys.stderr.write("\rgenerate %d negative (%0.2f %s)" % 
                            (len(negative), (100 * len(negative) / (len_ * len(positive))), '%'))
                        sys.stderr.flush()
                    i += 1
    df_negative_sample = pd.DataFrame(
        negative, columns=['id', 'cid', 'num'])

    # 速度较快的取样方法
    # for e in expect_list:
    #     for j in job_list:
    #         if (e, j) not in positive:
    #             negative.append([e, j, 0])
    # df_negative = pd.DataFrame(
    #     negative, columns=['id', 'cid', 'num'])
    # df_negative_sample = df_negative.sample(len_ * len(positive))

    return df_negative_sample

combine_frame = pd.merge(view_frame, investor_frame, left_on='id', right_on='user_id')
combine_frame = pd.merge(combine_frame, company_frame, left_on='cid', right_on='attach_cid')
combine_frame['address'] = [1 if i[0] == i[1] else 0 for i in zip(combine_frame['address1_x'], combine_frame['address1_y'])]
combine_frame = combine_frame.fillna(0)

# neg_frame = build_negative_smple(combine_frame[['id_x', 'cid']])
# neg_combine_frame = pd.merge(neg_frame, investor_frame, left_on='id', right_on='user_id')
# neg_combine_frame = pd.merge(neg_combine_frame, company_frame, left_on='cid', right_on='id')
# neg_combine_frame['address'] = [1 if i[0] == i[1] else 0 for i in zip(neg_combine_frame['address1_x'], neg_combine_frame['address1_y'])]
# neg_combine_frame = neg_combine_frame.fillna(0)

# combine_frame = pd.concat([combine_frame, neg_combine_frame])


data_x = combine_frame.drop(['id_x', 'cid', 'num', 'id_y', 'user_id', 'org_id', 'id.1', 'org_id.1', 'address1_x', 'address1_y', 'id', 'attach_cid', ], axis=1)
data_y = combine_frame['num'].apply(lambda x: 1 if x > 0 else 0).values
data_y = combine_frame['num'].apply(lambda x: 1 if x > 1 else 0).values

np.savetxt('data/data.csv', np.c_[data_x, data_y], delimiter = ',')

