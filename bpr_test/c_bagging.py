# -*- coding: utf-8 -*-
# 內建库
import sys
import json
# 第三方库
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

frame = pd.DataFrame(data)
x = frame.values[:, 0]
y = frame.values[:, 1]
c = frame.values[:, 2]

plt.scatter(x, y, c=c, s=1, alpha=0.5)
