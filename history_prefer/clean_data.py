# -*- coding: utf-8 -*-
import sys
import random
import itertools
from collections import Iterable
# 第三方包
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split

def fast_sample(posi_frame, _len=1):
    user_array = posi_frame.iloc[:, 0].values
    item_array = posi_frame.iloc[:, 1].values
    positive_samples = set(zip(user_array, item_array))
    print(len(positive_samples))
    target_len = round(_len * len(positive_samples))
    negative_samples = np.array([[0, 0]])
    while len(negative_samples) < target_len:
        print('*')
        negative_users = user_array[np.random.randint(len(user_array), size=(1 * (target_len - len(negative_samples))))]
        negative_items = item_array[np.random.randint(len(user_array), size=(1 * (target_len - len(negative_samples))))]
        negative_set = set(zip(negative_users, negative_items)) - positive_samples
        negative_samples_tmp = np.array(list(negative_set))[:(target_len - len(negative_samples))]
        negative_samples = np.r_[negative_samples, negative_samples_tmp]
    df_negative_sample = pd.DataFrame(negative_samples[1:, :], columns=['id', 'cid'])
    df_negative_sample['num'] = 0
    return df_negative_sample

def calcurate_compatibility(P_x, U_y):
    attrs = U_y.keys()
    # print attrs
    scores = []
    for a in attrs:
        v_a = U_y[a]
        p_x_a = P_x[a][v_a]
        # print P_x[a]
        n = sum(P_x[a].values())
        s_a = float(p_x_a) / float(n)
        if s_a == 0:
            compatibility = 0#一项为0 总分为0
            return compatibility
        else:
            scores.append(s_a)
    compatibility = np.average(scores)
    return compatibility


company_file = 'data/company.csv'
view_file = 'data/view_com_820.csv'

company_frame = pd.read_csv(company_file).set_index('attach_cid').drop(['id'], axis=1)
def age_norm(num):
    fl = np.floor(num / 10) * 10
    return (fl, fl + 10)
company_frame['age_month'] = company_frame['age_month'].map(age_norm)

company_dict = company_frame.T.to_dict()

view_frame = pd.read_csv(view_file)
# neg_frame = fast_sample(view_frame[['id', 'cid']], 1)
# view_frame = pd.concat([view_frame, neg_frame])
train, test = train_test_split(view_frame)

history_prefer = dict()
history_view = dict()
for i, row in train.iterrows():
    uid, cid, num = row
    if cid in company_dict:
        if uid not in history_prefer:
            history_prefer[uid] = dict()
            history_view[uid] = dict()
        for attr, value in company_dict[cid].items():
            if attr not in history_prefer[uid]:
                history_prefer[uid][attr] = dict()
            if value not in history_prefer[uid][attr]:
                history_prefer[uid][attr][value] = 0
            history_prefer[uid][attr][value] += num
        history_view[uid][cid] = num

test_company = dict()
test_view = dict()
for i, row in test.iterrows():
    uid, cid, num = row
    if cid in company_dict:
        if uid not in test_view:
            test_view[uid] = dict()
        test_view[uid][cid] = num
        test_company[cid] = company_dict[cid]


def recon(item_profile, user_preference, communication_history): 
    def findPreference(x):
        P_x = user_preference[x]
        return P_x

    def calcurate_compatibility(P_x, y):
        U_y = item_profile[y]
        attrs = U_y.keys()
        # print attrs
        scores = []
        for a in attrs:
            v_a = U_y[a]
            if v_a not in P_x[a]:
                p_x_a = 0
            else:
                p_x_a = P_x[a][v_a]
            # print P_x[a]
            n = sum(P_x[a].values())
            s_a = float(p_x_a) / float(n)
            if s_a == 0:
                compatibility = 0#一项为0 总分为0
                return compatibility
            else:
                scores.append(s_a)
        compatibility = np.average(scores)
        return compatibility

    def reciprocalRecommender(x, N=0):#x is user id
        P_x = findPreference(x)#dict of user profrence
        # print P_x
        # print 'AllUsersNotMessagedBy',R
        S = []
        R = list(item_profile.keys())
        for y in R:
            s_y = calcurate_compatibility(P_x, y)
            S.append(s_y)
        sorted_indices = [ i[0] for i in sorted(enumerate(S), key=lambda x:-x[1]) ]
        newR = []
        newS = []
        if N == 0:
            N = len(sorted_indices)
        for idx in sorted_indices[0:N]:
            newR.append(R[idx])
            newS.append(S[idx])
        # print newR,newS
        return newR,newS

    recommend = dict()
    users = sorted(user_preference.keys())
    for u in users:
        R,S = reciprocalRecommender(u, N=0)
        recommend[u]=dict()
        # print ('recommend for user',u)
        for i, y in enumerate(R):
            recommend[u][y]=S[i]
        sys.stderr.write('\rrecomend for user %d' % u)
        sys.stderr.flush()
    sys.stderr.write("\n")
    sys.stderr.flush()

    return recommend

recommend = recon(test_company, history_prefer, history_view)

def auc_test(prediction_mat, train_data, test_data, test_items, s=0.3):
    test_users = set(test_data.keys())
    train_users = set(train_data.keys())
    auc_values = []
    z = 0
    user_array = np.array(list(test_users & train_users))
    user_sample = user_array[np.random.randint(len(user_array), size=round(s * len(user_array)))]
# =============================================================================
#     user_sample = user_array
# =============================================================================
    for user in user_sample:
        auc_for_user = 0.0
        n = 0
        predictions = prediction_mat[user]
        pos_items = set(test_data[user]) - set(train_data[user])
        neg_items = test_items - pos_items
        for posi in pos_items:
            for neg in neg_items:
                n += 1
                if predictions[posi] > predictions[neg]:
                    auc_for_user += 1
                elif predictions[posi] == predictions[neg]:
                    auc_for_user += 0.5
        if n > 0:
            auc_for_user /= n
            auc_values.append(auc_for_user)
        z += 1
        if z % 10 == 0 and len(auc_values) > 0:
            sys.stderr.write("\rCurrent AUC mean (%s samples): %0.3f" % (str(z), np.mean(auc_values)))
            sys.stderr.flush()
    sys.stderr.write("\n")
    sys.stderr.flush()
    return np.mean(auc_values)

test_items = set(test_company.keys())
auc = auc_test(recommend, history_view, test_view, test_items)