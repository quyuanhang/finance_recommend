# -*- coding: utf-8 -*-
import sys
import random
import itertools
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

class industryLab(object):
    """docstring for industryLab"""
    def __init__(self, tag_industry_frame):
        self.tag_dict = dict(zip(tag_industry_frame.iloc[:, 0], tag_industry_frame.iloc[:, 1]))
        self.filter_tag = {'媒体报道', '36氪报道'}
        self.miss_tag = set()
    def tag_normalize(self, tag):
        industry = 0
        if tag not in self.tag_dict:
            # print('%s not in db' % tag)
            self.miss_tag.add(tag)
            return industry
        if tag not in self.filter_tag:
            industry = self.tag_dict[tag]
        return industry






# 用户特征处理
investor_frame = pd.read_csv(investor_file).drop_duplicates(subset='user_id')
investor_frame = prefer_phases(investor_frame)
# investor_frame = prefer_industry(investor_frame, 'prefer_industry')
# investor_frame = investor_frame.fillna(0).astype('int')

# 公司特征处理
company_frame = pd.read_csv(company_file).drop_duplicates(subset='attach_cid')
# company_frame = prefer_industry(company_frame, 'industry1')
# company_frame = company_frame.fillna(0).astype('int')
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

def phases_cal(p_list):
    phase_in = lambda x: 1 if (x[0] <= x[2]) and (x[2] <= x[1]) else 0
    phase_in_list = map(phase_in, p_list)
    return list(phase_in_list)

combine_frame['phase_in'] = phases_cal(zip(combine_frame['min_phase'], combine_frame['max_phase'], combine_frame['finance_phase']))

def industry(org_com_industry):
    def _industry(pair):
        if (pair[0] != pair[0]) or (pair[1] != pair[1]):
            return 0
        org_ind = eval(pair[0]) if type(pair[0]) == str else pair[0]
        com_ind = pair[1]
        rank = 0
        if isinstance(org_ind, Iterable):
            org_ind = set(org_ind)
            if com_ind in org_ind:
                rank = 1
        else:
            if org_ind == com_ind:
                rank = 1
        return rank
    return list(map(_industry, org_com_industry))

combine_frame['industry_in'] = industry(zip(combine_frame['prefer_industry'], combine_frame['industry1']))

ilab = industryLab(pd.read_csv('data/tag_industry.csv'))
with open('data/user_crm_tag.csv', encoding='utf8') as file:
    user_follow_tag_dict = dict()
    for row in itertools.islice(file, 1, None):
        user, tag = eval(row)
        user = int(user)
        industry = ilab.tag_normalize(tag)
        if user not in user_follow_tag_dict:
            user_follow_tag_dict[user] = dict()
        if industry not in user_follow_tag_dict[user]:
            user_follow_tag_dict[user][industry] = 0
        user_follow_tag_dict[user][industry] += 1
user_follow_tag_frame = pd.DataFrame(user_follow_tag_dict).T
user_follow_tag_frame = user_follow_tag_frame.reindex(index=combine_frame['user_id'], columns=range(1, 27))
# user_follow_tag_frame.columns = map(lambda x: 'user_follow_tag_industry_' + str(x), user_follow_tag_frame.columns)

with open('data/company_tag.csv', encoding='utf8') as file:
    company_tag_dict = dict()
    for row in itertools.islice(file, 1, None):
        cid, attach_cid, tag = eval(row)
        attach_cid = int(attach_cid)
        industry = ilab.tag_normalize(tag)
        if attach_cid not in company_tag_dict:
            company_tag_dict[attach_cid] = dict()
        if industry not in company_tag_dict[attach_cid]:
            company_tag_dict[attach_cid][industry] = 0
        company_tag_dict[attach_cid][industry] += 1
company_tag_frame = pd.DataFrame(company_tag_dict).T
company_tag_frame = company_tag_frame.reindex(index=combine_frame['cid'], columns=range(1, 27))
# company_tag_frame.columns = map(lambda x: 'com_tag_industry_' + str(x), company_tag_frame.columns)

user_view_com_on_tag = user_follow_tag_frame.values * company_tag_frame.values
user_view_com_on_tag[np.isnan(user_view_com_on_tag)] = 0
for col in range(1, 27):
    combine_frame['match_follow_industry_' + str(col)] = user_view_com_on_tag[:, col-1]
combine_frame['have_match_tag_industry'] = user_view_com_on_tag.sum(axis=1)

data = combine_frame.drop(['id_x', 'cid', 'num', 'id_y', 'user_id', 'org_id', 'id.1', 'org_id.1', 'address1_x', 'address1_y', 'id', 'attach_cid', 'prefer_industry'], axis=1)
data = data.astype(int)
# data['y'] = combine_frame['num'].map(lambda x: 2 if x >= 2 else x).values
data['y'] = combine_frame['num'].map(lambda x: 1 if x >= 1 else x).values

data.to_csv('data/data.csv', index=False)

statistic = pd.DataFrame([data[data['y']==1].mean(), data[data['y']==0].mean()]).T
statistic['devise'] = statistic[0] / statistic[1]

