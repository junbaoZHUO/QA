import spacy
from spacy_lookup import Entity
import numpy as np
import re
from information import trans_dict,trans_list,replace_dict,re_att_dict
from information import eentity_dict, zentity_dict, ementity_dict, zmentity_dict

import requests
import random
import json
from hashlib import md5
import time


class QueryPretreat:
    def __init__(self,emnlp,zmnlp,enlp,znlp,mdict_keys,edict_keys,zdict_keys):
        self.__emnlp = emnlp
        self.__zmnlp = zmnlp
        self.__enlp = enlp
        self.__znlp = znlp
        self.__mdict_keys = mdict_keys
        self.__edict_keys = edict_keys
        self.__zdict_keys = zdict_keys
        # self.__enlp = spacy.load('en_core_web_sm')  # 替换词表的spacy模型
        # self.__enlp.remove_pipe('ner')
        # self.__edict_keys = eentity_dict.keys()
        # for key, values in eentity_dict.items():
        #     entity = Entity(keywords_list=values, label=key)
        #     self.__enlp.add_pipe(entity, name=key)

        # self.__znlp = spacy.load('zh_core_web_sm')  # 替换词表的spacy模型
        # self.__znlp.remove_pipe('ner')
        # self.__zdict_keys = zentity_dict.keys()
        # for key, values in zentity_dict.items():
        #     entity = Entity(keywords_list=values, label=key)
        #     self.__znlp.add_pipe(entity, name=key)
        # entity = Entity(keywords_list=trans_list, label="relation")
        # self.__znlp.add_pipe(entity, name="relation")
        
        # self.__renlp = spacy.load('zh_core_web_sm')
        # self.__renlp.remove_pipe('ner')
        # print(trans_list)
        # entity = Entity(keywords_list=trans_list, label="relation")
        # self.__renlp.add_pipe(entity, name="relation")
    

    def enorzh_question(self, question):
        self.__doc = question
        ch = question[0]
        if ('A'<=ch and ch<='Z')or('a'<=ch and ch<='z'):
            self.__isenglish = True
        else:
            self.__isenglish = False
        if self.__isenglish:
            return 'en'
        else:
            return 'zh'
    
    def getmovie(self,question):
        mnum = 0
        ml = {}
        qstr = question
        if self.__isenglish:
            #temp = qstr.split("\"")
            temp = re.split(r'\"',qstr)
        else:
            #temp = qstr.split("(“|”)")
            temp = re.split(r'[“”\"]',qstr)
        ansq = ""
        for i,ch in enumerate(temp):
            if i % 2 == 1:
                mnum +=1
                m = 'M' + str(mnum)
                ansq = ansq + m
                ml[m] = ch
            else:
                ansq = ansq + ch  
        if mnum == 0:
            if self.__isenglish:
                qstr = self.__emnlp(ansq)
                ansq = ""
                for token in qstr:
                    if not(ansq == ""):
                        if token.text!=')' and qstr[token.i - 1].text != '(':
                            ansq = ansq + " "
                    if token.ent_type_ in self.__mdict_keys:
                        mnum +=1
                        m = 'M' + str(mnum)
                        ansq = ansq + m
                        ml[m] = token.text
                    else:
                        ansq = ansq + token.text
            else:
                qstr = self.__zmnlp(ansq)
                ansq = ""
                for token in qstr:
                    if token.ent_type_ in self.__mdict_keys:
                        mnum +=1
                        m = 'M' + str(mnum)
                        ansq = ansq + m
                        ml[m] = token.text
                    else:
                        ansq = ansq + token.text

        # print()
        # print(ansq, ml, mnum)
        # print()
        return ansq, ml, mnum

    def getentity(self,question):
        if self.__isenglish:
            entnum = {}
            for key in self.__edict_keys:
                entnum[key] = 0
            entl = {}
            doc = self.__enlp(question)       
            ansq = ""
            for token in doc:
                if not (ansq == ""):
                    ansq = ansq + " "               
                if token.ent_type_ in self.__edict_keys:
                    entnum[token.ent_type_] += 1
                    retext = str.upper(token.ent_type_[0]) + str(entnum[token.ent_type_])
                    ansq = ansq + retext
                    entl[retext] = token.text
                else:
                    ansq = ansq + token.text
        else:
            entnum = {}
            for key in self.__zdict_keys:
                entnum[key] = 0
            entl = {}
            doc = self.__znlp(question)       
            ansq = ""
            for token in doc: 
                #print(token.text, token._.is_entity, token.ent_type_)          
                if token.ent_type_ in self.__zdict_keys:
                    entnum[token.ent_type_] += 1
                    retext = str.upper(token.ent_type_[0]) + str(entnum[token.ent_type_])
                    ansq = ansq + retext
                    entl[retext] = token.text
                elif token.ent_type_ == "relation":
                    if len(ansq)>0:
                        ch = ansq[-1]
                    else:
                        ch = 'a'
                    if ('0'<=ch and ch<='9'):
                        ansq = ansq + " "
                    ansq = ansq + trans_dict[token.text]
                else:
                    ansq = ansq + token.text
                
        return ansq, entl, entnum

    def backname(self, triple_set, movielist, entlist):
        t = triple_set
        m = movielist
        e = entlist
        if len(t)<5:
            for i,name in enumerate(t[1]):
                if name in m.keys():
                    t[1][i] = m[name]
                elif name in e.keys():
                    t[1][i] = e[name]
            return t
        for i,name in enumerate(t[1]):
            if name in m.keys():
                t[1][i] = m[name]
            elif name in e.keys():
                t[1][i] = e[name]
        for i,name in enumerate(t[3]):
            if name in m.keys():
                t[3][i] = m[name]
            elif name in e.keys():
                t[3][i] = e[name]
        return t
    
    def atttodict(self, attlist, movielist, entlist,la):
        # print("*****************************************")
        a = attlist
        # print(a)
        m = movielist
        e = entlist
        ad = []
        for l in a:
            if l[0] in ['No link','No what','REQU']:
                ad.append(l)
                continue
            flag = 'n'
            if l[0] in m.keys():
                k = m[l[0]]
                flag = 'm'
            elif l[0] in e.keys():
                k = e[l[0]]
                if (l[0][0]=='p')or(l[0][0]=='P'): flag = 'p'
            else:
                k = l[0]
                if ('person' in l[0]): flag = 'p'
                elif ('movie' in l[0]): flag = 'm'
            if l[1] == 'name':
                if flag == 'p': l[1] = 'pname'
                elif flag == 'm':
                    if la == 'en': l[1] = 'mnamee'
                    else: l[1] = 'mnamez'
            if l[1] in re_att_dict.keys():
                l[1] = re_att_dict[l[1]]
            ad.append([k,l[1]])
        # print(ad)
        # print("*****************************************")
        return ad

    # def relatrans(self,question):
    #     print("====================================================")
    #     print(question)
    #     doc = self.__renlp(question)       
    #     ans = ""
    #     for token in doc:
    #         print(token.text,token.ent_type_)
    #         if token.ent_type_=="relation":
    #             ans = ans + trans_dict[token.text]
    #         else:
    #             ans = ans + token.text
    #     print(ans)
    #     print("====================================================")
    #     return ans

    def make_md5(self, s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    def bdtrans(self,question):
        # Set your own appid/appkey.
        appid = '20210812000914833'
        appkey = 'cm3Sj9cJ6Z2nh3M9rVfR'
        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        from_lang = 'zh'
        to_lang =  'en'
        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path
        query = question
        print(query)
        # Generate salt and sign
        salt = random.randint(32768, 65536)
        sign = self.make_md5(appid + query + str(salt) + appkey)
        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
        # Send request
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()
        # Show response
        #print(json.dumps(result, indent=4, ensure_ascii=False))
        '''if ('error_code' in result.keys()):
                a=result['error_code']
                if (a == '54003'):
                    访问频繁了'''
        ans = result['trans_result'][0]['dst']
        #print(ans)
        for key in replace_dict.keys():
            ans = ans.replace(key,replace_dict[key])
        # ans = ans.replace(",", " and")
        # ans = ans.replace("prize", "award")
        # ans = ans.replace("film","movie")
        time.sleep(1)
        return ans
    
    def forward_pre(self, question):
        '''
            前向主调函数
            输入：问题字符串
            返回：语言、预处理后的问句、电影字典、电影数、其他实体字典、其他实体数
        '''

        lang = self.enorzh_question(question)
        newq, movielist, movienum = self.getmovie(question)
        newq, entlist, entnum = self.getentity(newq)
        if not(self.__isenglish):
            #newq = self.relatrans(newq)
            newq = self.bdtrans(newq)
        
        return lang, newq, movielist, movienum, entlist, entnum

if __name__=="__main__":

    print("Prepare english entity dictionary")
    enlp = spacy.load('en_core_web_sm')  # 替换词表的spacy模型
    enlp.remove_pipe('ner')
    edict_keys = eentity_dict.keys()
    for key, values in eentity_dict.items():
        entity = Entity(keywords_list=values, label=key)
        enlp.add_pipe(entity, name=key)

    print("Prepare chinese entity dictionary")
    znlp = spacy.load('zh_core_web_sm')  # 替换词表的spacy模型
    znlp.remove_pipe('ner')
    zdict_keys = zentity_dict.keys()
    for key, values in zentity_dict.items():
        entity = Entity(keywords_list=values, label=key)
        znlp.add_pipe(entity, name=key)
    
    print("Prepare english movie dictionary")
    emnlp = spacy.load('en_core_web_sm')  # 替换词表的spacy模型
    emnlp.remove_pipe('ner')
    mdict_keys = set(ementity_dict.keys())
    for key, values in ementity_dict.items():
        entity = Entity(keywords_list=values, label=key)
        emnlp.add_pipe(entity, name=key)

    print("Prepare chinese movie dictionary")
    zmnlp = spacy.load('zh_core_web_sm')  # 替换词表的spacy模型
    zmnlp.remove_pipe('ner')
    mdict_keys.update(set(zmentity_dict.keys()))
    for key, values in zmentity_dict.items():
        entity = Entity(keywords_list=values, label=key)
        zmnlp.add_pipe(entity, name=key)
    
    # questions = ['Who is actor of "Who is" and director of "The actor" and writer of "She"?'
    #                 ,'What movies is acted by Leonardo DiCaprio and Kate Winslet?'
    #                 ,'What movie is distributed by Tamjeed Elahi Khan Cinema or TC Entertainment (2018) (Japan) (Blu-ray)?']
    # questions = ['戚小波和韩哲参演了什么电影？'
    #                 ,'谁是"谁是"的演员和"演员"的导演以及"她"的编剧？'
    #                 ,'什么电影是刘氏财团或者敬亭文化有限公司发行的？']
    questions = ['谁出演了霸王别姬?']
    q_pre = QueryPretreat(emnlp,zmnlp,enlp,znlp,mdict_keys,edict_keys,zdict_keys)

    for q in questions:
        print("----------------------------------------------------------------------")
        print(q)
        lang, question, movielist, movienum, entlist, entnum = q_pre.forward_pre(q)
        print(lang)
        print(question)
        print(movielist)
        print(entlist)
        print()
        triplet_set = ([],['M1','P2','C1'],[],['P1','M2','C2'],[])
        triplet_new = q_pre.backname(triplet_set, movielist, entlist)
        print(triplet_new)
        print("----------------------------------------------------------------------")
