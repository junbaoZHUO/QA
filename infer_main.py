# -*- coding:utf-8 -*-
"""
    主调模块
"""
import spacy
from spacy_lookup import Entity
from QAQ import QueryPretreat
from Qsplit import QuerySplit
from answer_generator import Query2Answer
from QperML import QueryParse
from functools import lru_cache
from information import line_break, entity_dict, eentity_dict, zentity_dict, ementity_dict, zmentity_dict, trans_list
from QtoMovie import getmovie, backmovie

print("===============Model initialize=================")
add_who = set(['actor', 'director', 'direct', 'photographer', 'writer', 'editor', 'composer', 'designer', 'producer'
               ,'Actor', 'Director', 'Photographer', 'Writer', 'Editor', 'Composer', 'Designer', 'Producer'])
add_what = set(['movie', 'award', 'compan','Movie', 'Award', 'Compan', 'score', 'birthday', 'height', 'Score', 'Birthday', 'Height'])
print("Prepare entity dictionary")
nlp = spacy.load('en_core_web_sm')
nlp.remove_pipe('ner')
entity_keys = entity_dict.keys()  # 可以提问的实体空间
for key, values in entity_dict.items():
    entity = Entity(keywords_list=values, label=key)
    nlp.add_pipe(entity, name=key)  # 添加确定识别的NER列表

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
# entity = Entity(keywords_list=trans_list, label="relation")
# znlp.add_pipe(entity, name="relation")

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

print("Import question pretreatment")
q_pre = QueryPretreat(emnlp,zmnlp,enlp,znlp,mdict_keys,edict_keys,zdict_keys)
print("Import question spliter")
q_split = QuerySplit(nlp, entity_keys)
print("Import question parser")
parse_blk = QueryParse(nlp, entity_keys)
print("Import Answer generator")
q2a_blk = Query2Answer()
print("===============Input quesiton=================")


@lru_cache()
def answer_inference(q):
    lang, q, movielist, movienum, entlist, entnum = q_pre.forward_pre(q)
    # 输入：问题字符串
    # 返回：语言、预处理后的问句、电影字典、电影数、其他实体字典、其他实体数

    q = retrive2qa(q, add_who, add_what)

    q = addhead(q)

    print(q)

    query_splited = q_split.forward_split(q)  # logic, question_set, neg_label, proplist

    triplet_set = []
    attlist_set = []
    for q_sep,prop_sep in zip(query_splited["question_set"],query_splited["proplist"]):
        # print(q_sep)
        triplet = parse_blk.parse_keyword(q_sep) # 每一个子句的三元组解析
        triplet_new = q_pre.backname(triplet, movielist, entlist)
        triplet_set.append(triplet_new)
        if len(prop_sep) == 0:
            attlist_set.append([])
        else:
            attlist = q_pre.atttodict(prop_sep, movielist, entlist, lang)
            attlist_set.append(attlist)
        
    print(triplet_set)
    for x in attlist_set:
        x[-1].append('what')
    print(attlist_set)

    # 输入为triplet_set + 逻辑词集合 + 否定词集合，可以解析带有逻辑形式三元组。
    # 具体逻辑语句组织形式参考Qsplit.py的forward_split函数说明
    ans = []
    visual_ans = ""
    movie_thres = 4000  # Titanic >5000 2, >1000 5
    ans, visual_ans = q2a_blk.get_answer(lang, triplet_set, attlist_set, query_splited["logic"], query_splited["neg_label"], movie_thres)
    return ans, visual_ans


def addition_info_query(res):
    if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
        limitation = 3
        add_visual_ans = q2a_blk.get_additional_answer(res, limitation)
    return add_visual_ans

def addhead(q_in):
    q = q_in
    q = q.replace("What's","What is")
    q = q.replace("what's","what is")
    q = q.replace("Who act", "who is the actor of")
    q = q.replace("director", "direct")
    q = q.replace("When", "What")
    if 'what is' in q or 'What is' in q:
        return q
    
    for item in ['who','Who']:
        if item in q:
            return q.replace(item,'what name of person')
    
    return q_in

def retrive2qa(q_in, add_who, add_what):
    q = q_in

    if 'what' in q or 'who' in q or 'which' in q or 'What' in q or 'Who' in q or 'Which' in q:
        return q_in
    for item in add_who:
        if item in q:
            q = q.strip(item)
            return 'what name of person ' + item.lower() + ' ' + q
    for item in add_what:
        if item in q:
            temp = 'what ' + item.lower()
            q = q.replace(item, temp)
            q_temp = q.split(' ')
            if q_temp[0] == 'what':
                return q.replace(q_temp[1], q_temp[1] + ' is')
            else:
                return q
    return q_in

if __name__ == '__main__':
    # for person in open("person_pre.txt", encoding='utf-8').readlines():
    #     person = person.strip(line_break)
    for question in open("test_questions/questionv2.txt", errors="ignore", encoding='utf-8').readlines():
        question = question.strip(line_break) 
        print("------------------------------------------------------------------------------------")
        print(question)
        answers, visual_answer = answer_inference(question)
        print("**the answer:")
        if len(answers) == 0:
            print("answer cannot be found")
        else:
            for ans in answers:
                print(ans['text'])
        print("------------------------------------------------------------------------------------")
        input("ssss")

    # question = open("question.txt", errors="ignore",encoding='utf-8').readline()
    # question = question.strip(line_break)
    # print(question)
    # answers, visual_answer = answer_inference(question)
    # print("**the answer:")
    # if len(answers) == 0:
    #     print("answer cannot be found")
    # else:
    #     for v in answers:
    #         print(v['text'])

    # input("**json for visualization:")
    # print(visual_answer)

    # add_visual_ans = addition_info_query(visual_answer)
    # print(add_visual_ans)
