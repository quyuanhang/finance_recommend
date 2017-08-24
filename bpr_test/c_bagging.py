# -*- coding: utf-8 -*-
# 內建库
import sys
import json
import random
# 第三方库\
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from sklearn import linear_model

view_train_file = 'input/view_tag/train_815.csv'
view_pre_file = 'output/tag_click_pre.json'
click_train_file = 'input/tag_click/train_815.csv'
click_pre_file = 'output/view_tag_pre.json'

with open(view_pre_file, encoding='utf8') as file:
    view_dict = json.load(file)

with open(click_pre_file, encoding='utf8') as file:
    click_dict = json.load(file)

view_user_set, view_tag_set, view_pos_set = set(), set(), set()
data = []
view_train_frame = pd.read_csv(view_train_file).drop_duplicates()
for i, row in view_train_frame.iterrows():
    user, tag = row
    user = str(user)    
    try:
        s1 = view_dict[user][tag]
        s2 = click_dict[user][tag]
        data.append([s1, s2, 1])
    except:
        continue
    view_user_set.add(user)
    view_tag_set.add(tag)
    view_pos_set.add((user, tag))
view_frame = pd.DataFrame(data)

click_user_set, click_tag_set, click_pos_set = set(), set(), set()
data = []
click_train_frame = pd.read_csv(click_train_file).drop_duplicates()
for i, row in click_train_frame.iterrows():
    user, tag = row
    user = str(user)
    try:
        s1 = view_dict[user][tag]
        s2 = click_dict[user][tag]
        data.append([s1, s2, 2])
    except:
        continue
    click_user_set.add(user)
    click_tag_set.add(tag)
    click_pos_set.add((user, tag))      
click_frame = pd.DataFrame(data)

user_set = view_user_set & click_user_set
tag_set = view_tag_set & click_tag_set
pos_set = view_pos_set | click_pos_set

frame = pd.concat([view_frame, click_frame])
x = frame.values[:, 0]
y = frame.values[:, 1]
c = frame.values[:, 2]

p = len(pos_set) / (len(user_set) * len(tag_set))

neg_list = list()
for user in user_set:
    for tag in tag_set:
        if (random.random() < p) and ((user, tag) not in pos_set):
            s1 = view_dict[user][tag]
            s2 = click_dict[user][tag]
            neg_list.append([s1, s2, 0])
neg_frame = pd.DataFrame(neg_list)
pos_neg_frame = pd.concat([frame, neg_frame])
x = pos_neg_frame.values[:, 0]
y = pos_neg_frame.values[:, 1]
c = pos_neg_frame.values[:, 2]

reg = linear_model.LinearRegression()
reg.fit(pos_neg_frame.values[:, :2], pos_neg_frame.values[:, 2])

color_dict = {0:'gray', 1:'b', 2:'r'}
color = [color_dict[i] for i in c]
plt.scatter(x, y, c=color, s=2, alpha=0.4)
plt.show()
print(reg.coef_, reg.intercept_)

baging_prediction = dict()
for user in user_set:
    for tag in tag_set:
        if user not in baging_prediction:
            baging_prediction[user] = dict()
        baging_prediction[user][tag] = reg.predict([[view_dict[user][tag], click_dict[user][tag]]])[0]

# 测试评价
train_file = 'input/view_tag/train_815.csv'
test_file = 'input/view_tag/test_815.csv'
training_data = pd.read_csv(train_file).values
testing_data = pd.read_csv(test_file).values

def data_to_dict(training_data):
    train_dict = dict()
    for row in training_data:
        user, item = row
        user = str(user)
        if user not in train_dict:
            train_dict[user] = dict()
        train_dict[user][item] = 1
    return train_dict

train_dict = data_to_dict(training_data)
test_dict = data_to_dict(testing_data)

def evaluate(recommend_dict, lable_dict, train_dict, top=1000, mode='base'):
    tp, fp, fn = 0, 0, 0
    precision_recall_list = list()
    for exp, job_rank_dict in recommend_dict.items():
        if exp in lable_dict:
            job_rank = sorted(job_rank_dict.items(),
                              key=lambda x: x[1], reverse=True)
            rec = [j_r[0] for j_r in job_rank[:top]]
            rec_set = set(rec)
            positive_set = set(lable_dict[exp].keys())
            tp += len(rec_set & positive_set)
            fp += len(rec_set - positive_set)
            fn += len(positive_set - rec_set)
            if mode == 'max':
                precision = 1 if rec_set & positive_set else 0
                recall = 1 if rec_set & positive_set else 0
            else:
                precision = len(rec_set & positive_set) / len(rec_set)
                recall = len(rec_set & positive_set) / len(positive_set)
            precision_recall_list.append([precision, recall])
    if (mode == 'base') or (mode == 'max'):
        df = pd.DataFrame(precision_recall_list, columns=[
                          'precision', 'recall'])
        return pd.DataFrame([df.mean(), df.std()], index=['mean', 'std'])
    elif mode == 'sum':
        return ('precision, recall \n %f, %f' % ((tp / (tp + fp)), (tp / (tp + fn))))

precision_list, recall_list = [], []
for k in range(1, 100, 5):
    precision, recall = evaluate(baging_prediction, test_dict, train_dict, top=k, mode='base').values[0]
    precision_list.append(precision)
    recall_list.append(recall)

plt.scatter(precision_list, recall_list)

def evaluate(recommend_dict, lable_dict, train_dict, top=1000, mode='base'):
    tp, fp, fn = 0, 0, 0
    precision_recall_list = list()
    for exp, job_rank_dict in recommend_dict.items():
        if exp in set(lable_dict.keys()) & set(train_dict.keys()):
            job_rank = sorted(job_rank_dict.items(),
                              key=lambda x: x[1], reverse=True)
            rec = [j_r[0] for j_r in job_rank if j_r[0] not in train_dict[exp]][:top]
            rec_set = set(rec)
            positive_set = set(lable_dict[exp].keys()) - set(train_dict[exp].keys())
            tp += len(rec_set & positive_set)
            fp += len(rec_set - positive_set)
            fn += len(positive_set - rec_set)
            if len(positive_set) > 0:
                if mode == 'max':
                    precision = 1 if rec_set & positive_set else 0
                    recall = 1 if rec_set & positive_set else 0
                else:
                    precision = len(rec_set & positive_set) / len(rec_set)
                    recall = len(rec_set & positive_set) / len(positive_set)
                precision_recall_list.append([precision, recall])
    if (mode == 'base') or (mode == 'max'):
        df = pd.DataFrame(precision_recall_list, columns=[
                          'precision', 'recall'])
        return pd.DataFrame([df.mean(), df.std()], index=['mean', 'std'])
    elif mode == 'sum':
        return ('precision, recall \n %f, %f' % ((tp / (tp + fp)), (tp / (tp + fn))))

precision_list, recall_list = [], []
for k in range(1, 100, 5):
    precision, recall = evaluate(baging_prediction, test_dict, train_dict, top=k, mode='base').values[0]
    precision_list.append(precision)
    recall_list.append(recall)

plt.scatter(precision_list, recall_list)

prob_num_dict = dict()
test_frame = pd.read_csv(test_file).drop_duplicates()
test_frame['distinct_id'] = test_frame['distinct_id'].map(str)
test_user_set = set(test_frame.values[:, 0])
user_set = user_set & test_user_set
test_tag_set = set(test_frame.values[:, 1])
tag_set = tag_set & test_tag_set
test_pos_set = set(zip(list(test_frame.values[:, 0]), list(test_frame.values[:, 1])))
pos_set = test_pos_set | pos_set
for user in user_set:
    for tag in tag_set:
        user = str(user)
        score = baging_prediction[user][tag]
        if score not in prob_num_dict:
            prob_num_dict[score] = {'pos': 0, 'neg': 0}
            if (user, tag) in test_pos_set:
                prob_num_dict[score]['pos'] += 1
            elif (user, tag) not in pos_set:
                prob_num_dict[score]['neg'] += 1
df_for_auc = pd.DataFrame(prob_num_dict).T
df_for_auc.to_csv('output/auc_data.csv')

# avg auc
# for user in baging_prediction:
#     auc_for_user = 0.0
#     n = 0
#     predictions = baging_prediction[user]
#     pos_items = set
