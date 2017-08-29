import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split

data = np.loadtxt('data/data.csv', delimiter=",")
data_x = data[:, :-1]
data_y = data[:, -1]

train_x, test_x, train_y, test_y = train_test_split(data_x, data_y)

# from sklearn import linear_model
# lr = linear_model.LogisticRegression()
# lr.fit(train_x, train_y)
# s1 = lr.score(test_x, test_y)
# print(s1)

# from sklearn.ensemble import GradientBoostingClassifier
# gbdt = GradientBoostingClassifier()
# gbdt.fit(train_x, train_y)
# s2 = gbdt.score(test_x, test_y)
# print(s2)

# from sklearn import svm
# clf = svm.SVC()
# clf.fit(train_x, train_y)
# s3 = clf.score(test_x, test_y)
# print(s3)

from sklearn import tree
dt_clf = tree.DecisionTreeRegressor()
dt_clf.fit(train_x, train_y)
s4 = dt_clf.score(test_x, test_y)
print(s4)


def accuracy(p_array, test_y):
	accuracy = 0
	for i, p in enumerate(p_array):
		y = test_y[i]
		if p == y:
			accuracy += 1
	accuracy /= len(p_array)
	return accuracy

def auc(p_array, test_y, split):
	positive_index = [i[0] for i in enumerate(test_y) if i[1] > split]
	negative_index = [i[0] for i in enumerate(test_y) if i[1] <= split]
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

p_array = dt_clf.predict(test_x)
print(accuracy(p_array, test_y), auc(p_array, test_y, 1))




