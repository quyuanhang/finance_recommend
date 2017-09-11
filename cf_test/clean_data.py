# -*- coding: utf-8 -*-
import sys
import math
import collections
import datetime
import numpy
import pandas as pd

# 数据文件 ==========================
train_file = 'input/view_com/train_815.csv'
test_file = 'input/view_com/test_815.csv'
# 输出文件===========================


def count_degree(frame):
    degree_series = pd.concat([frame.iloc[:, 1], frame.iloc[:, 0]])
    degree_frame = pd.DataFrame(
        degree_series.value_counts(), columns=['degree'])
    user_1 = frame.columns[0]
    # user_2 = frame.columns[1]
    user_degree_frame = pd.merge(frame, degree_frame,
                                    left_on=user_1, right_index=True)
    # user_degree_frame = pd.merge(user_degree_frame, degree_frame,
    #                                 left_on=user_2, right_index=True)
    return user_degree_frame


def frame_to_dict_filter_user(frame, user_set):
    dict_ = dict()
    for i, row in frame.iterrows():
        dis_id, com_id = tuple(row)
        if dis_id in user_set:
            if dis_id not in dict_:
                dict_[dis_id] = dict()
            if com_id not in dict_[dis_id]:
                dict_[dis_id][com_id] = 0
            dict_[dis_id][com_id] += 1
    # items = heapq.nsamllest(len(dict_), dict_.items(), key=lambda x: x[0])
    items = sorted(dict_.items(), key=lambda x: x[0])
    dict_ = collections.OrderedDict(items)
    return dict_



class ItemBasedCF:

    def __init__(self, train_data):
        self.train = train_data

    def item_similarity(self):
        # 建立物品-物品的共现矩阵
        C = dict()  # 物品-物品的共现矩阵
        N = dict()  # 物品被多少个不同用户购买
        for user, items in self.train.items():
            for i in items.keys():
                N.setdefault(i, 0)
                N[i] += 1
                C.setdefault(i, {})
                for j in items.keys():
                    if i == j:
                        continue
                    C[i].setdefault(j, 0)
                    C[i][j] += 1
        # 计算相似度矩阵
        self.W = dict()
        for i, related_items in C.items():
            self.W.setdefault(i, {})
            for j, cij in related_items.items():
                self.W[i][j] = cij / (math.sqrt(N[i] * N[j]))
        # return self.W

    # 给用户user推荐，前K个相关用户
    def recommend_one_user(self, user, K):
        rank = dict()
        action_item = self.train[user]  # 用户user产生过行为的item和评分
        for item, score in action_item.items():
            for j, wj in sorted(self.W[item].items(), key=lambda x: x[1], reverse=True)[0:K]:
                if j in action_item.keys():
                    continue
                rank.setdefault(j, 0)
                rank[j] += score * wj
        return collections.OrderedDict(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:K])

    def recommend_all(self, K):
        rec_dict = dict()
        user_num = 0
        for user in self.train:
            rec_dict[user] = self.recommend_one_user(user, K)
            user_num += 1
            if user_num % 100 == 0:
                sys.stderr.write("\rrecommend users: %0.5f " % (user_num / len(self.train)) )
                sys.stderr.flush()
        print('\n')
        return rec_dict




def evaluate(recommend_dict, lable_dict, train_dict, top=1000, mode='base'):
    tp, fp, fn = 0, 0, 0
    precision_recall_list = list()
    for exp, job_rank_dict in recommend_dict.items():
        if len(recommend_dict[exp]) > 0:
            if exp in lable_dict:
                job_rank = list(job_rank_dict.items())
                rec = [j_r[0] for j_r in job_rank[:top]]
                rec_set = set(rec)
                positive_set = set(lable_dict[exp].keys())
                positive_set = positive_set - set(train_dict[exp].keys())
                tp += len(rec_set & positive_set)
                fp += len(rec_set - positive_set)
                fn += len(positive_set - rec_set)
                if mode == 'max':
                    precision = 1 if rec_set & positive_set else 0
                    recall = 1 if rec_set & positive_set else 0
                else:
                    precision = len(rec_set & positive_set) / (len(rec_set) + 0.1)
                    recall = len(rec_set & positive_set) / (len(positive_set) + 0.1)
                precision_recall_list.append([precision, recall])
    if (mode == 'base') or (mode == 'max'):
        df = pd.DataFrame(precision_recall_list, columns=[
                          'precision', 'recall'])
        return pd.DataFrame([df.mean(), df.std()], index=['mean', 'std'])
    elif mode == 'sum':
        return ('precision, recall \n %f, %f' % ((tp / (tp + fp)), (tp / (tp + fn))))


def auc(train_dict, rank_dict, test_dict):
    train_items = set()
    for user, item_rank in train_dict.items():
        train_items = train_items | set(item_rank.keys())
    auc_values = []
    z = 0
    user_set = set(train_dict.keys()) & set(test_dict.keys())
    for user in user_set:
        predictions = rank_dict[user]
        auc_for_user = 0.0
        n = 0
        pos_items = set(predictions.keys()) & set(test_dict[user].keys())
        neg_items = set(predictions.keys()) - pos_items
        for pos_item in pos_items:
            for neg_item in neg_items:
                n += 1
                if predictions[pos_item] > predictions[neg_item]:
                    auc_for_user += 1
                elif predictions[pos_item] == predictions[neg_item]:
                    auc_for_user += 0.5
            if n > 0:
                auc_for_user /= n
                auc_values.append(auc_for_user)
            z += 1
            if z % 100 == 0 and len(auc_values) > 0:
                sys.stderr.write("\rCurrent AUC mean (%s samples): %0.5f" % (str(z), numpy.mean(auc_values)))
                sys.stderr.flush()
    sys.stderr.write("\n")
    sys.stderr.flush()
    return numpy.mean(auc_values)  


begin = datetime.datetime.now()
# 划分数据====================================================
train_frame = pd.read_csv(train_file)
train_frame = count_degree(train_frame)
train_frame = train_frame[train_frame['degree'] >= 3].iloc[:, :2]
test_frame = pd.read_csv(test_file)
user_set = set(train_frame['distinct_id']) & set(test_frame['distinct_id'])
train_dict = frame_to_dict_filter_user(train_frame, user_set)
test_dict = frame_to_dict_filter_user(test_frame, user_set)
print('划分数据')
print(datetime.datetime.now() - begin)
begin = datetime.datetime.now()


# 开始推荐
item_base_cf = ItemBasedCF(train_dict)
print('初始化类')
print(datetime.datetime.now() - begin)
begin = datetime.datetime.now()

item_base_cf.item_similarity()
print('计算相似')
print(datetime.datetime.now() - begin)
begin = datetime.datetime.now()


prediction = item_base_cf.recommend_all(1000)
print('推荐预测')
print(datetime.datetime.now() - begin)
begin = datetime.datetime.now()

print(auc(train_dict, prediction, test_dict))


#==============================================================================
# print('标准测试')
# print(evaluate(prediction, test_dict, top=5, mode='base'))
# 
# print('覆盖测试')
# print(evaluate(prediction, test_dict, top=5, mode='max'))
#==============================================================================

precision_list, recall_list = [], []
for k in range(1, 100):
    precision, recall = evaluate(prediction, test_dict, train_dict, top=k, mode='base').values[0]
    precision_list.append(precision)
    recall_list.append(recall)

import matplotlib.pylab as plt
plt.scatter(precision_list, recall_list)
