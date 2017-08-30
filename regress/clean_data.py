# -*- coding: utf-8 -*-
import sys
import random
from collections import Iterable
# 第三方包
import pandas as pd
import numpy as np

investor_file = 'data/investor.csv'
company_file = 'data/company.csv'
view_file = 'data/view_com_828.csv'

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

def fast_sample(posi_frame, _len=1):
    user_array = posi_frame.iloc[:, 0].values
    item_array = posi_frame.iloc[:, 1].values
    positive_samples = set(zip(user_array, item_array))
    target_len = round(_len * len(positive_samples))
    negative_samples = np.array([[0, 0]])
    while len(negative_samples) < target_len:
        negative_users = user_array[np.random.randint(len(user_array), size=(2 * (target_len - len(negative_samples))))]
        negative_items = item_array[np.random.randint(len(user_array), size=(2 * (target_len - len(negative_samples))))]
        negative_set = set(zip(negative_users, negative_items)) - positive_samples
        negative_samples_tmp = np.array(list(negative_set))[:(target_len - len(negative_samples))]
        negative_samples = np.r_[negative_samples, negative_samples_tmp]
    df_negative_sample = pd.DataFrame(negative_samples[1:, :], columns=['id', 'cid'])
    df_negative_sample['num'] = 0
    return df_negative_sample

combine_frame = pd.merge(view_frame, investor_frame, left_on='id', right_on='user_id')
combine_frame = pd.merge(combine_frame, company_frame, left_on='cid', right_on='attach_cid')
combine_frame['address'] = [1 if i[0] == i[1] else 0 for i in zip(combine_frame['address1_x'], combine_frame['address1_y'])]
combine_frame = combine_frame.fillna(0)

neg_frame = fast_sample(combine_frame[['id_x', 'cid']], 3)
neg_combine_frame = pd.merge(neg_frame, investor_frame, left_on='id', right_on='user_id')
neg_combine_frame = pd.merge(neg_combine_frame, company_frame, left_on='cid', right_on='attach_cid')
neg_combine_frame['address'] = [1 if i[0] == i[1] else 0 for i in zip(neg_combine_frame['address1_x'], neg_combine_frame['address1_y'])]
neg_combine_frame = neg_combine_frame.fillna(0)

combine_frame = pd.concat([combine_frame, neg_combine_frame])


data = combine_frame.drop(['id_x', 'cid', 'num', 'id_y', 'user_id', 'org_id', 'id.1', 'org_id.1', 'address1_x', 'address1_y', 'id', 'attach_cid'], axis=1)
data['y'] = combine_frame['num'].apply(lambda x: 2 if x > 1 else x).values
# data_y = combine_frame['num'].apply(lambda x: 2 if x > 1 else x).values
# data_y = combine_frame['num'].apply(lambda x: 1 if x > 1 else 0).values

# np.savetxt('data/data.csv', np.c_[data_x, data_y], delimiter = ',')

data.to_csv('data/data.csv', index=False)

