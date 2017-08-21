# -*- coding: utf-8 -*-

import sys
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def print_schedule(begin, i, s_=None):
    if not s_:
        return 0
    if i % 1000 == 0:
        sum_time = '%0.2f' % (time.time() - begin)
        sys.stderr.write(("\r%s %d sum time %s" % (s_, i, sum_time)))
        sys.stderr.flush()


def complete_schedual():
    sys.stderr.write("\n")
    sys.stderr.flush()


# 数据文件
view_file = 'input/view_tag/train.csv'
click_file = 'input/tag_click/train.csv'
# 初始化全局变量
begin = time.time()


click_data = pd.read_csv(click_file).drop_duplicates().values
view_data = pd.read_csv(view_file).drop_duplicates().values

click_dict = dict()
for uid, cid in click_data:
    if uid not in click_dict:
        click_dict[uid] = dict()
    click_dict[uid][cid] = 2

combine_data = list(np.c_[click_data, [2] * len(click_data)])
for uid, cid in view_data:
    if uid in click_dict:
        if cid not in click_dict[uid]:
            combine_data.append([uid, cid, 1])

train_data, test_data = train_test_split(
    pd.DataFrame(combine_data), test_size=0.2, random_state=0)

train_data.to_csv('input/train.csv', index=False, header=False)
test_data.to_csv('input/test.csv', index=False, header=False)

