# -*- coding: utf-8 -*-
# 內建库
import sys
import json
import random
# 第三方库\
import sklearn
import numpy as np
import pandas as pd
import matplotlib.pylab as plt

view_train_file = 'input/view_tag/train.csv'
view_pre_file = 'output/tag_click_pre.json'
click_train_file = 'input/tag_click/train.csv'
click_pre_file = 'output/view_tag_pre.json'

with open(view_pre_file, encoding='utf8') as file:
	view_dict = json.load(file)

with open(click_pre_file, encoding='utf8') as file:
	click_dict = json.load(file)

user_set, tag_set, pos_set = set(), set(), set()
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
	user_set.add(user)
	tag_set.add(tag)
	pos_set.add((user, tag))
view_frame = pd.DataFrame(data)

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
	user_set.add(user)
	tag_set.add(tag)
	pos_set.add((user, tag))		
click_frame = pd.DataFrame(data)

frame = pd.concat([view_frame, click_frame])
x = frame.values[:, 0]
y = frame.values[:, 1]
c = frame.values[:, 2]

p = len(pos_set) / (len(user_set) * len(tag_set))

neg_list = list()
for user in user_set:
	for tag in tag_set:
		if random.random() < p and (user, tag) not in pos_set:
			s1 = view_dict[user][tag]
			s2 = click_dict[user][tag]
			neg_list.append([s1, s2, 0])
neg_frame = pd.DataFrame(neg_list)
pos_neg_frame = pd.concat([frame, neg_frame])
x = pos_neg_frame.values[:, 0]
y = pos_neg_frame.values[:, 1]
c = pos_neg_frame.values[:, 2]

linear_model = sklearn.linear_model
reg = linear_model.LinearRegression()
reg.fit(pos_neg_frame.values[:, :2], pos_neg_frame.values[:, 2])

color_dict = {0:'gray', 1:'b', 2:'r'}
color = [color_dict[i] for i in c]
plt.scatter(x, y, c=color, s=2, alpha=0.4)
print(reg)