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
bp_file = 'data/bp_820.csv'
wb_file = 'data/workbench_820.csv'

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

def prefer_industry(frame, key):
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
    pre = pivot(frame[key].values)
    pre.columns = map(lambda x: 'pref_' + str(x), list(pre.columns))
    frame = pd.merge(frame, pre, left_index=True, right_index=True, how='left')
    return frame.drop(key, axis=1)

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

class CidLib(object):
    """docstring for id_converter"""
    def __init__(self, id_cid_frame):
        self.id_cid_dict = dict(zip(id_cid_frame['id'], id_cid_frame['attach_cid']))

    def convert_id_to_cid(self, _id):
        if _id in self.id_cid_dict:
            cid = self.id_cid_dict[_id]
        else:
            cid = 0
        return cid


# 用户特征处理
investor_frame = pd.read_csv(investor_file).drop_duplicates(subset='user_id')
investor_frame = prefer_phases(investor_frame)
investor_frame = prefer_industry(investor_frame, 'prefer_industry')
investor_frame = investor_frame.fillna(0).astype('int')

# 公司特征处理
company_frame = pd.read_csv(company_file).drop_duplicates(subset='attach_cid')
company_frame = prefer_industry(company_frame, 'industry1')
company_frame = company_frame.fillna(0).astype('int')
cid_lib = CidLib(company_frame.iloc[:, :2])

# bp行为
bp_frame = pd.read_csv(bp_file)
bp_frame['cid'] = bp_frame['crm_id'].map(cid_lib.convert_id_to_cid)
bp_frame['cid'] = bp_frame['company_id'].fillna(0) + bp_frame['cid']
bp_frame.drop(['crm_id', 'company_id'], axis=1, inplace=True)
bp_frame = bp_frame.reindex(columns=['id', 'cid', 'num'])

# workbench行为
wb_frame = pd.read_csv(wb_file)
wb_frame['cid'] = wb_frame['ccid'].map(cid_lib.convert_id_to_cid)
wb_frame.drop(['ccid'], axis=1, inplace=True)
wb_frame = wb_frame.reindex(columns=['id', 'cid', 'num'])

view_frame = pd.read_csv(view_file)

posi_combine_frame = pd.merge(view_frame, investor_frame, left_on='id', right_on='user_id')
posi_combine_frame = pd.merge(posi_combine_frame, company_frame, left_on='cid', right_on='attach_cid')
posi_combine_frame['address'] = [1 if i[0] == i[1] else 0 for i in zip(posi_combine_frame['address1_x'], posi_combine_frame['address1_y'])]
posi_combine_frame = posi_combine_frame.fillna(0)

neg_frame = fast_sample(posi_combine_frame[['id_x', 'cid']], 1)
neg_combine_frame = pd.merge(neg_frame, investor_frame, left_on='id', right_on='user_id')
neg_combine_frame = pd.merge(neg_combine_frame, company_frame, left_on='cid', right_on='attach_cid')
neg_combine_frame['address'] = [1 if i[0] == i[1] else 0 for i in zip(neg_combine_frame['address1_x'], neg_combine_frame['address1_y'])]
neg_combine_frame = neg_combine_frame.fillna(0)

combine_frame = pd.concat([posi_combine_frame, neg_combine_frame])


data = combine_frame.drop(['id_x', 'cid', 'num', 'id_y', 'user_id', 'org_id', 'id.1', 'org_id.1', 'address1_x', 'address1_y', 'id', 'attach_cid'], axis=1)
# data['y'] = combine_frame['num'].map(lambda x: 2 if x >= 2 else x).values
data['y'] = combine_frame['num'].map(lambda x: 1 if x >= 1 else x).values

data.to_csv('data/data.csv', index=False)

