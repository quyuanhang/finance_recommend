# -*- coding: utf-8 -*-
import sys
sys.path.append('theano_bpr/')
import pandas as pd
import utils
import bpr

# 数据文件 ==========================
train_file = 'input/view_tag/train.csv'
test_file = 'input/view_tag/test.csv'
# 输出文件===========================

train_frame = pd.read_csv(train_file)
test_frame = pd.read_csv(test_file)

training_data, users_to_index, items_to_index = utils.load_data_from_array(
        train_frame.values)
testing_data, users_to_index, items_to_index = utils.load_data_from_array(
        test_frame.values, users_to_index, items_to_index)

bpr = bpr.BPR(10, len(users_to_index.keys()), len(items_to_index.keys()))

bpr.train(training_data, epochs=50)


prediction = bpr.prediction_to_dict()


def data_to_dict(training_data):
    train_dict = dict()
    for row in training_data:
        user, item = row
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
    precision, recall = evaluate(prediction, test_dict, train_dict, top=k, mode='base').values[0]
    precision_list.append(precision)
    recall_list.append(recall)

# import matplotlib.pylab as plt
# plt.scatter(precision_list, recall_list)

bpr.test(testing_data)
