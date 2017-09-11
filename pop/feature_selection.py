# -*- coding: utf-8 -*-
import json
import itertools
import collections
# 第三方包
import pandas as pd

# class industryLab(object):
#     """docstring for industryLab"""
#     def __init__(self, tag_industry_frame):
#         self.tag_dict = dict(zip(tag_industry_frame.iloc[:, 0], tag_industry_frame.iloc[:, 1].astype(str)))
#         self.filter_tag = {'媒体报道', '36氪报道'}
#         self.miss_tag = set()
#     def tag_normalize(self, tag):
#         industry = 0
#         if tag not in self.tag_dict:
#             # print('%s not in db' % tag)
#             self.miss_tag.add(tag)
#             return industry
#         if tag not in self.filter_tag:
#             industry = self.tag_dict[tag]
#         return industry

# def combine_dict(d1, d2):
#     d = dict()
#     for key in set(d1.keys()) & set(d2.keys()):
#         d[key] = d1[key] + d2[key]
#     for key in set(d1.keys()) - set(d2.keys()):
#         d[key] = d1[key]
#     for key in set(d2.keys()) - set(d1.keys()):
#         d[key] = d2[key]
#     return d

# def content_similarity(ser_1, ser_2):
#     idx = ser_1.index & ser_2.index
#     product = 0
#     for i in idx:
#         product += ser_1[i] * ser_2[i]
#     cos = \
#         product / ((sum(ser_1.values ** 2.0) *
#                     sum(ser_2.values ** 2.0))**0.5 + 0.01)
#     return cos

# ilab = industryLab(pd.read_csv('data/tag_industry.csv'))

# with open('data/user_crm_tag.csv', encoding='utf8') as file:
#     user_follow_tag_dict = dict()
#     for row in itertools.islice(file, 1, None):
#         user, tag = eval(row)
#         user = int(user)
#         industry = ilab.tag_normalize(tag)
#         if user not in user_follow_tag_dict:
#             user_follow_tag_dict[user] = dict()
#         if industry not in user_follow_tag_dict[user]:
#             user_follow_tag_dict[user][industry] = 0
#         user_follow_tag_dict[user][industry] += 1

# with open('data/company_tag.csv', encoding='utf8') as file:
#     company_tag_dict = dict()
#     for row in itertools.islice(file, 1, None):
#         cid, attach_cid, tag = eval(row)
#         attach_cid = int(attach_cid)
#         industry = ilab.tag_normalize(tag)
#         if attach_cid not in company_tag_dict:
#             company_tag_dict[attach_cid] = dict()
#         if industry not in company_tag_dict[attach_cid]:
#             company_tag_dict[attach_cid][industry] = 0
#         company_tag_dict[attach_cid][industry] += 1


# with open('data/view_com_820.csv', encoding='utf8') as file:
#     user_prefer_dict = dict()
#     for row in itertools.islice(file, 1, None):
#         uid, cid, num = eval(row)
#         if uid in user_follow_tag_dict and cid in company_tag_dict:
#             if uid not in user_prefer_dict:
#                 user_prefer_dict[uid] = company_tag_dict[cid]
#             else:
#                 user_prefer_dict[uid] = combine_dict(user_prefer_dict[uid], company_tag_dict[cid])

# user_prefer_dict = collections.OrderedDict(sorted(user_prefer_dict.items(), key=lambda x: x[0]))
# for k, v in user_prefer_dict.items():
#     user_prefer_dict[k] = collections.OrderedDict(sorted(user_prefer_dict[k].items(), key=lambda x: x[1], reverse=True))
# user_follow_tag_dict = collections.OrderedDict([i for i in sorted(user_follow_tag_dict.items(), key=lambda x: x[0]) if i[0] in user_prefer_dict])

# with open('output/user_follow.json', 'w', encoding='utf8') as file:
#     file.write(json.dumps(user_follow_tag_dict, indent=4, ensure_ascii=False))

# with open('output/user_view.json', 'w', encoding='utf8') as file:
#     file.write(json.dumps(user_prefer_dict, indent=4, ensure_ascii=False))

# with open('data/view_com_820.csv', encoding='utf8') as file:
#     user_sim_dict = dict()
#     for row in itertools.islice(file, 1, None):
#         uid, cid, num = eval(row)
#         if uid in user_follow_tag_dict and cid in company_tag_dict:
#             if uid not in user_sim_dict:
#                 user_sim_dict[uid] = dict()
#             user_sim_dict[uid][cid] = content_similarity(
#                 pd.Series(user_follow_tag_dict[uid]), pd.Series(company_tag_dict[cid]))
# user_sim_dict = collections.OrderedDict(sorted(user_sim_dict.items(), key=lambda x: x[0]))
# for k, v in user_sim_dict.items():
#     user_sim_dict[k] = collections.OrderedDict(sorted(user_sim_dict[k].items(), key=lambda x: x[1], reverse=True))


# with open('output/view_sim.json', 'w') as file:
#     file.write(json.dumps(user_sim_dict, indent=4))


view_frame = pd.read_csv('data/view_com_828.csv').applymap(str)
com_pop = view_frame['cid'].value_counts().astype(float)
view_dict = dict()
for i, row in view_frame.iterrows():
    uid, cid, num = row
    uid = str(uid)
    cid = str(cid)
    if uid not in view_dict:
        view_dict[uid] = dict()
    view_dict[uid][cid] = com_pop[cid]
view_dict = collections.OrderedDict(sorted(view_dict.items(), key=lambda x: x[0]))
for k, v in view_dict.items():
    view_dict[k] = collections.OrderedDict(sorted(view_dict[k].items(), key=lambda x: x[1], reverse=True))
    
with open('output/view_pop.json', 'w') as file:
    file.write(json.dumps(view_dict, indent=4))