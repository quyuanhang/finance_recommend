import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split

data = np.loadtxt('data/data.csv', delimiter=",")
data_x = data[:, :-1]
data_y = data[:, -1]

train_x, test_x, train_y, test_y = train_test_split(data_x, data_y)

from sklearn import linear_model
lr = linear_model.LogisticRegression()
lr.fit(train_x, train_y)
s1 = lr.score(test_x, test_y)
print(s1)

from sklearn.ensemble import GradientBoostingClassifier
gbdt = GradientBoostingClassifier()
gbdt.fit(train_x, train_y)
s2 = gbdt.score(test_x, test_y)
print(s2)

# from sklearn import svm
# clf = svm.SVC()
# clf.fit(train_x, train_y)
# s3 = clf.score(test_x, test_y)
# print(s3)

from sklearn import tree
dt_clf = tree.DecisionTreeClassifier()
dt_clf.fit(train_x, train_y)
s4 = dt_clf.score(test_x, test_y)
print(s4)


def accuracy(mod, test_x, test_y):
	p_array = mod.predict(test_x)
	accuracy = 0
	for i, p in enumerate(p_array):
		y = test_y[i]
		if p == y:
			accuracy += 1
	accuracy /= len(p_array)
	return accuracy

def auc(mod, test_x, test_y):
	p_array = mod.predict_proba(test_x)[:, 1]
	positive_index = [i[0] for i in enumerate(test_y) if i[1] == 1]
	negative_index = [i[0] for i in enumerate(test_y) if i[1] == 0]
	positive_score = p_array[positive_index]
	negative_score = p_array[negative_index]
	auc = 0.0
	for pos_s in positive_score:
		for neg_s in negative_score:
			if pos_s > neg_s:
				auc += 1
			if pos_s == neg_s:
				auc += 0.5
	auc /= (len(positive_score) * len(negative_score))
	return auc

print(accuracy(dt_clf, test_x, test_y), auc(dt_clf, test_x, test_y))




