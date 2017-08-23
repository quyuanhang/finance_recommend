#! -*- coding=utf-8 -*-
import pylab as pl


evaluate_result = 'output/auc_data.csv'
db = []  # [score,nonclk,clk]
pos, neg = 0, 0
with open(evaluate_result, 'r') as fs:
    next(fs)
    for line in fs:
        score, nonclk, clk = line.strip().split(',')
        nonclk = int(nonclk)
        clk = int(clk)
        score = float(score)
        db.append([score, nonclk, clk])
        pos += clk
        neg += nonclk


db = sorted(db, key=lambda x: x[0], reverse=True)

# 计算ROC坐标点
auc_data = []
p_r_data = []
tp, fp = 0., 0.
for i in range(len(db)):
    tp += db[i][2]
    fp += db[i][1]
    TPR = tp / pos
    FPR = fp / neg
    prec = tp / (tp + fp)
    recall = tp / pos
    auc_data.append([FPR, TPR])
    p_r_data.append([prec, recall])

# 计算曲线下面积
auc = 0.
prev_x = 0
for x, y in auc_data:
    auc += (x - prev_x) * y
    prev_x = x

print("the auc is %s." % auc)

pl.figure(1)
x = [_v[0] for _v in auc_data]
y = [_v[1] for _v in auc_data]
pl.title("ROC curve of %s (AUC = %.4f)" % ('LogisticRegression', auc))
pl.xlabel("False Positive Rate")
pl.ylabel("True Positive Rate")
pl.plot(x, y)  # use pylab to plot x and y
pl.show()  # show the plot on the screen

pl.figure(2)
x = [_v[0] for _v in p_r_data]
y = [_v[1] for _v in p_r_data]
pl.title("P R curve of %s (AUC = %.4f)" % ('LogisticRegression', auc))
pl.xlabel("precision")
pl.ylabel("recall")
pl.plot(x, y)  # use pylab to plot x and y
pl.show()  # show the plot on the screen
