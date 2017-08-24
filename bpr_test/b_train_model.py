# -*- coding: utf-8 -*-
# 內建库
import sys
sys.path.append('theano_bpr/')
import json
# 第三方库
import pandas as pd
import matplotlib.pylab as plt
# 自建库
import utils
import bpr

# 数据文件 ==========================
train_file = 'input/view_com/train_815.csv'
test_file = 'input/view_com/test_815.csv'
# 输出文件===========================
prediction_file = 'output/view_com_pre.json'

train_frame = pd.read_csv(train_file)
test_frame = pd.read_csv(test_file)

training_data, users_to_index, items_to_index = utils.load_data_from_array(
        train_frame.values[:, :2])
testing_data, users_to_index, items_to_index = utils.load_data_from_array(
        test_frame.values[:, :2], users_to_index, items_to_index)

bpr = bpr.BPR(10, len(users_to_index.keys()), len(items_to_index.keys()), lambda_all=0.0025)

bpr.train(training_data, epochs=100)

#==============================================================================
# bpr.test(testing_data)
#==============================================================================

prediction = bpr.prediction_to_dict(500)

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

# 存储预测评分
def prediction_convert(index_pre, users_to_index, items_to_index):
    def reverse_dict(_dict):
        reverse = dict()
        for user, u_id in _dict.items():
            reverse[u_id] = user
        return reverse
    index_user = reverse_dict(users_to_index)
    index_item = reverse_dict(items_to_index)
    convert = dict()
    for u_id, i_r_dict in index_pre.items():
        user = str(index_user[u_id])
        convert[user] = dict()
        for item_id, rate in i_r_dict.items():
            item = str(index_item[item_id])
            convert[user][item] = float(rate)
    return convert

def save_dict(obj, file_dir):
    f = open(file_dir, mode='w', encoding='utf8', errors='ignore')
    s = json.dumps(obj, indent=4, ensure_ascii=False)
    f.write(s)
    f.close()

prediction_ = prediction_convert(prediction, users_to_index, items_to_index)
save_dict(prediction_, prediction_file)

