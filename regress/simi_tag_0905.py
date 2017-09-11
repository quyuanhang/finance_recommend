# -*- coding:utf-8 -*-
from __future__ import division
import json, cStringIO
import sys,os,copy,re,math,MySQLdb,heapq
import time,datetime
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))
from common.db_fetcher import DataBaseFetcher

class SimiTags(object):
    def __init__(self):
        self.db_fetcher = DataBaseFetcher()
        self.tag2comlist = self.load_info('select cid,tag from crm.company_tag')
        self.tag_child = self.load_info('select tag,parent_tag from crm.tag_tag_relation')
        self.tag_parent = self.load_info('select parent_tag,tag from crm.tag_tag_relation')
        self.total_num,self.manual_tag_count = self.tag_cid()

    def load_info(self,cmd):
        temp_dict = {}
        db_row = self.db_fetcher.get_sql_result(cmd,'mysql_readall')
        for row in db_row:
            leaf,root = row
            if root not in temp_dict:temp_dict[root] = []
            temp_dict[root].append(leaf)
        return temp_dict 

    def tag_cid(self): 
        db_row = self.db_fetcher.get_sql_result('select count(distinct cid) from crm.company_tag','mysql_readall')
        total_num = db_row[0][0]
        manual_tag_count = {}
        db_row = self.db_fetcher.get_sql_result('select cid,tag from crm.company_tag where type != 5','mysql_readall')
        for row in db_row:
            crm_id,tag = row
            if tag not in manual_tag_count:manual_tag_count[tag] = 0
            manual_tag_count[tag] += 1
        return total_num,manual_tag_count

    def get_correlation(self):
        similarity_tag = {}
        tag_corre_dict = {}
        f = 0
        for tag1 in self.tag2comlist:
            tag_corre_dict = {}
            if tag1.lower() != '人工智能':continue
            if tag1 not in self.manual_tag_count:continue
            manual_num_x = self.manual_tag_count[tag1]
            if manual_num_x < 30:continue
            l1 = self.tag2comlist[tag1]
            sum_x = len(l1)
            if sum_x < 100 :continue
            for tag2 in self.tag2comlist:
                if tag1 == tag2:continue
                if tag2 not in self.tag2comlist or tag2 not in self.manual_tag_count:continue
                manual_num = self.manual_tag_count[tag2]
                if manual_num < 2:continue
                l2 = self.tag2comlist[tag2]
                sum_y = len(l2)
                if sum_y > sum_x * 1.5 :continue
                xy = len(set(l1) & set(l2))
                if xy < 5:continue
                pf = xy * 1.0 / sum_x 
                if pf > 0.6:continue
                pc = xy * 1.0 / sum_y
                pnc = (sum_x - xy + 1) * 1.0 / (self.total_num - sum_y)
                if pc < 0.01:continue
                if pnc != 0:
                    value = pc / pnc
                if value < 1:continue
                correlation = math.pow(xy,0.2) * math.pow(value,0.8)
                tag_corre_dict[tag2] = correlation
                
            tag_items = tag_corre_dict.items()
            tag_heap = heapq.nlargest(len(tag_items),tag_items,key=lambda x:x[-1])
            tag_heap = tag_heap[:40]
            if len(tag_heap) == 0:continue
            re = map(lambda x:x[0],tag_heap)
            if len(re) == 0 :continue
            similarity_tag[tag1] = re
            print tag1,'\t',"%s" % json.dumps(re, ensure_ascii=False).encode('utf8')
        return similarity_tag

    def rm_sub(self,tag_heap):
        abandon_l = []
        for i in range(0,len(tag_heap)):
            tag1,weight = tag_heap[i]
            if tag1 not in self.tag2comlist:continue
            l1 = self.tag2comlist[tag1]
            sum_x = len(l1)
            tag1_p,tag1_c = [],[]
            if tag1 in self.tag_child:tag1_c = self.tag_child[tag1]
            if tag1 in self.tag_parent:tag1_p = self.tag_parent[tag1]
            for j in range(i+1,len(tag_heap)-1):
                tag2,weight = tag_heap[j]
                if tag2 in tag1_p or tag2 in tag1_c:
                    abandon_l.append(j)
                    continue
                if tag1.find(tag2) != -1 or tag2.find(tag1) != -1:
                    abandon_l.append(j)
                    continue
                l2 = self.tag2comlist[tag2]
                sum_y = len(l2)
                xy = len(set(l1) & set(l2))
                if (xy * 1.0 / sum_y) > 0.8:abandon_l.append(j)
                if (xy * 1.0 / sum_x) > 0.6:abandon_l.append(j)
        re_l = []
        for i in range(0,len(tag_heap)-1):
            if i in abandon_l:continue
            else:re_l.append(tag_heap[i][0])
        return re_l

if __name__=='__main__':
    simi_tags = SimiTags()
    simi_tags.get_correlation()
