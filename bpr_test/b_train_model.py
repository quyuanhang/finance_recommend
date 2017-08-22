# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 19:29:08 2017

@author: QYH
"""

# 內建库
import sys
sys.path.append('theano_bpr/')
# 第三方库
import matplotlib.pylab as plt
import pandas as pd
# 本地库
import utils
import bpr

train_file = 'input/train.csv'
test_file = 'input/test.csv'

with open(train_file, errors='ignore') as file:
    train_data = pd.read_csv(file, header=None).values
with open(test_file, errors='ignore') as file:
    test_data = pd.read_csv(file, header=None).values

training_data, users_to_index, items_to_index = utils.load_data_from_array(
    train_data)
testing_data, users_to_index, items_to_index = utils.load_data_from_array(
    test_data, users_to_index, items_to_index)

bpr = bpr.BPR(rank=20, n_users=len(users_to_index),
              n_items=len(items_to_index), match_weight=2)

bpr.train(training_data, epochs=2000)

prediction = bpr.prediction_to_dict()

def data_to_dict(training_data, min_rate):
    train_dict = dict()
    for row in training_data:
        user, item, rate = row
        if rate >= min_rate:
            if user not in train_dict:
                train_dict[user] = dict()
            train_dict[user][item] = 1
    return train_dict

train_dict = data_to_dict(training_data, 1)
test_dict = data_to_dict(testing_data, 1)

def evaluate(recommend_dict, lable_dict, train_dict, top=1000, mode='base'):
    tp, fp, fn = 0, 0, 0
    precision_recall_list = list()
    for exp, job_rank_dict in recommend_dict.items():
        if exp in set(lable_dict.keys()) & set(train_dict.keys()) :
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
    precision, recall = evaluate(prediction, test_dict, train_dict, top=k, mode='base').values[0]
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
    precision, recall = evaluate(prediction, test_dict, train_dict, top=k, mode='base').values[0]
    precision_list.append(precision)
    recall_list.append(recall)

plt.scatter(precision_list, recall_list)

bpr.test(testing_data)
