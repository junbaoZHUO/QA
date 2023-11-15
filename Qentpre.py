# -*- coding:utf-8 -*-
"""
    输入问题解析模块
"""
import spacy
from spacy_lookup import Entity
# from information import entity_dict, entity_relation_dict


class QueryParse:
    def __init__(self, question):
        """
        语义解析初始化
        :param question: 待解析问句
        """
        self.__ynlp = spacy.load('en_core_web_sm')
        self.__nlp = spacy.load('en_core_web_sm')
        self.__nlp2 = spacy.load('en_core_web_sm')
        self.__nlp.remove_pipe('ner')
        self.__nlp2.remove_pipe('ner')

        for key, values in entity_dict.items():
            entity = Entity(keywords_list=values, label=key)
            self.__nlp.add_pipe(entity, name=key)
        for key, values in entity_relation_dict.items():
            entity = Entity(keywords_list=values, label=key)
            self.__nlp2.add_pipe(entity, name=key)

        self.__doc1 = question
        self.__dochh = self.__doc1
        self.__doc1 = self.__nlp(self.__doc1.encode('utf8').decode('utf8'))
        self.__str1 = self.__get_str__(1, 'token.text', self.__doc1, None)
        self.__str2 = self.__get_str__(2, 'token.lemma_', self.__doc1, None)

        self.__doc2 = self.__ynlp(self.__str1)
        self.__doc3 = self.__nlp2(self.__str2)
        self.__str3 = self.__get_str__(3, 'doc0[i].text', self.__doc3, self.__doc2)

        self.__doc4 = self.__ynlp(self.__str3)

        self.__ans = []
        for token in self.__doc4:
            if token.dep_ == u'ROOT':
                if self.__doc1[token.i]._.is_entity or self.__doc3[token.i]._.is_entity:
                    # print(token.i)
                    self.__find1__(token.i)
                else:
                    self.__find3__(token.i)
        # print(self.__ans)

    @staticmethod
    def __get_str__(func_type, add_type, doc, doc0):
        """
        对应原str1,2,3部分
        """
        my_str = ""
        i = 0
        str_add = []
        for token in doc:
            if func_type != 3:
                if i > 0:
                    my_str = my_str + ' '
            else:
                if my_str != "":
                    my_str = my_str + ' '
            exec ('str_add = ' + add_type)
            if token._.is_entity:
                my_str = my_str + token.ent_type_
            else:
                my_str = my_str + str_add
            i = i + 1
            if token.ent_type_ == u'PUNCT':
                i = 0
        return my_str

    def __find2__(self, nowid):
        for child in self.__doc4[nowid].children:
            tid = child.i
            if self.__doc1[tid]._.is_entity or self.__doc3[tid]._.is_entity:
                return tid
            else:
                nid = self.__find2__(tid)
                if nid != tid:
                    return nid
        return nowid

    def __find1__(self, nowid):
        if self.__doc1[nowid]._.is_entity:
            type1 = self.__doc1[nowid].ent_type_
        else:
            type1 = self.__doc3[nowid].ent_type_
        for child in self.__doc4[nowid].children:
            tid = child.i
            if self.__doc1[tid]._.is_entity or self.__doc3[tid]._.is_entity:
                if self.__doc1[tid]._.is_entity:
                    type2 = self.__doc1[tid].ent_type_
                else:
                    type2 = self.__doc3[tid].ent_type_
                if type2 == 'QUESTION':
                    temp = {'id2': nowid, 'ty2': type1, 'id1': tid, 'ty1': type2}
                else:
                    temp = {'id1': nowid, 'ty1': type1, 'id2': tid, 'ty2': type2}
                self.__ans.append(temp)
                # print ('{0}({1})     {2}({3})'.format(doc1[nowid].text,type1,doc1[tid].text,type2))
                self.__find1__(tid)
            else:
                nid = self.__find2__(tid)
                if nid != tid:
                    if self.__doc1[nid]._.is_entity:
                        type2 = self.__doc1[nid].ent_type_
                    else:
                        type2 = self.__doc3[nid].ent_type_
                    if type2 == 'QUESTION':
                        temp = {'id2': nowid, 'ty2': type1, 'id1': nid, 'ty1': type2}
                    else:
                        temp = {'id1': nowid, 'ty1': type1, 'id2': nid, 'ty2': type2}
                    self.__ans.append(temp)
                    # print ('{0}({1})     {2}({3})'.format(doc1[nowid].text,type1,doc1[nid].text,type2))
                    # print(doc1[nowid].text,doc1[nid].text)
                    self.__find1__(nid)
        return nowid

    def __find3__(self, nowid):
        num = 0
        l = []
        for child in self.__doc4[nowid].children:
            tid = child.i
            if self.__doc1[tid]._.is_entity or self.__doc3[tid]._.is_entity:
                # print(num,tid)
                num = num + 1
                l.append(tid)
                # print(doc1[nowid].text,doc1[tid].text)
                # find1(tid)
            else:
                nid = self.__find2__(tid)
                if nid != tid:
                    # print(num,nid)
                    num = num + 1
                    l.append(nid)
                    # print(doc1[nowid].text,doc1[nid].text)
                    # find1(nid)
        # print(num)
        # print(l)
        if num == 1:
            self.__find1__(l[0])
        if num >= 2:
            if self.__doc1[l[0]]._.is_entity:
                type1 = self.__doc1[l[0]].ent_type_
            else:
                type1 = self.__doc3[l[0]].ent_type_
            if self.__doc1[l[1]]._.is_entity:
                type2 = self.__doc1[l[1]].ent_type_
            else:
                type2 = self.__doc3[l[1]].ent_type_
            if type2 == 'QUESTION':
                temp = {'id2': l[0], 'ty2': type1, 'id1': l[1], 'ty1': type2}
            else:
                temp = {'id1': l[0], 'ty1': type1, 'id2': l[1], 'ty2': type2}
            self.__ans.append(temp)
            # print ('{0}({1})     {2}({3})'.format(doc1[l[0]].text,type1,doc1[l[1]].text,type2))
            # print(doc1[l[0]].text,doc1[l[1]].text)
            for k in l:
                self.__find1__(k)
        return nowid

    def parse_keyword(self):
        entity_a = []
        entity_b = []
        entity_relation = []
        entity_a_property = []
        entity_b_property = []
        if self.__ans[0]['ty1'] == 'QUESTION':
            k = 0
        if self.__ans[1]['ty1'] == 'QUESTION':
            k = 1
        if self.__ans[k]['ty2'] != 'relate':
            entity_a = self.__ans[~k]['ty1']
            entity_b = self.__ans[~k]['ty2']
            entity_a_property = self.__doc1[self.__ans[~k]['id1']].text
            entity_b_property = self.__doc1[self.__ans[~k]['id2']].text
            # print('a({0})   r(?)   b({1})'.format(self.entity_a, self.entity_b))
            # print('a.name:{0}'.format(self.entity_a_name))
            # print('b.name:{0}'.format(self.entity_b_name))
        else:
            if (self.__ans[~k]['ty1'] == 'relate'):
                tid = self.__ans[~k]['id2']
                tty = self.__ans[~k]['ty2']
            else:
                tid = self.__ans[~k]['id1']
                tty = self.__ans[~k]['ty1']
            # print(tid,tty)
            entity_a = tty
            entity_relation = self.__doc3[self.__ans[k]['id2']].text
            entity_a_property = self.__doc1[tid].text
            # print('a({0})   r({1})   b(?)'.format(tty, self.entity_relation))
            # print('a.name:{0}'.format(self.entity_a_name))
        return entity_a, entity_a_property, entity_b, entity_b_property, entity_relation

# ynlp = spacy.load('en_core_web_sm')
# nlp = spacy.load('en_core_web_sm')
# nlp2 = spacy.load('en_core_web_sm')
# entity1 = Entity(keywords_list=['gone with the wind', 'harry potter'], label='MOVIE')
# nlp.add_pipe(entity1, name='MOVIE')
# entity2 = Entity(keywords_list=['han', 'qi', 'fang', 'hu', 'liu'], label='PER1')
# nlp.add_pipe(entity2, name='PER1')
# entity3 = Entity(keywords_list=['average rating'], label='ATTRIBUTE')
# nlp.add_pipe(entity3, name='ATTRIBUTE')
# entity5 = Entity(keywords_list=['which', 'who', 'what'], label='QUESTION')
# nlp.add_pipe(entity5, name='QUESTION')


# doc1 = question
# dochh = doc1
# doc1 = nlp(doc1.encode('utf8').decode('utf8'))

# str1 = ""
# i = 0
# for token in doc1:
#     if i > 0:
#         str1 = str1 + ' '
#     i = i + 1
#     if token._.is_entity:
#         str1 = str1 + token.ent_type_
#     else:
#         # if (token.text != '\n'):
#         # str=str+token.lemma_
#         str1 = str1 + token.text
#     if token.ent_type_ == u'PUNCT':
#         i = 0
#
# str2 = ""
# i = 0
# for token in doc1:
#     if i > 0:
#         str2 = str2 + ' '
#     i = i + 1
#     if token._.is_entity:
#         str2 = str2 + token.ent_type_
#     else:
#         # if (token.text != '\n'):
#         str2 = str2 + token.lemma_
#         # str2=str2+token.text
#     if token.ent_type_ == u'PUNCT':
#         i = 0


# doc2 = ynlp(str1)

# entity4 = Entity(keywords_list=['direct', 'director', 'act', 'actor'], label='relate')
# nlp2.add_pipe(entity4, name='relate')

# doc3 = nlp2(str2)

# str3 = ""
# i = 0
# for token in doc3:
#     if str3 != "":
#         str3 = str3 + ' '
#     if token._.is_entity:
#         str3 = str3 + token.ent_type_
#     else:
#         str3 = str3 + doc2[i].text
#         # if (token.text != '\n'):
#         # str=str+token.lemma_
#     # str3=str3+token.text
#     i = i + 1
#     if token.ent_type_ == u'PUNCT':
#         i = 0

# doc4 = ynlp(str3)


# def find2(nowid):
#     for child in doc4[nowid].children:
#         tid = child.i
#         if (doc1[tid]._.is_entity or doc3[tid]._.is_entity):
#             return tid
#         else:
#             nid = find2(tid)
#             if (nid != tid):
#                 return nid
#     return nowid


# def find1(nowid):
#     if (doc1[nowid]._.is_entity):
#         type1 = doc1[nowid].ent_type_
#     else:
#         type1 = doc3[nowid].ent_type_
#     for child in doc4[nowid].children:
#         tid = child.i
#         if (doc1[tid]._.is_entity or doc3[tid]._.is_entity):
#             if (doc1[tid]._.is_entity):
#                 type2 = doc1[tid].ent_type_
#             else:
#                 type2 = doc3[tid].ent_type_
#             if type2 == 'QUESTION':
#                 temp = {'id2': nowid, 'ty2': type1, 'id1': tid, 'ty1': type2}
#             else:
#                 temp = {'id1': nowid, 'ty1': type1, 'id2': tid, 'ty2': type2}
#             ans.append(temp)
#             # print ('{0}({1})     {2}({3})'.format(doc1[nowid].text,type1,doc1[tid].text,type2))
#             find1(tid)
#         else:
#             nid = find2(tid)
#             if (nid != tid):
#                 if (doc1[nid]._.is_entity):
#                     type2 = doc1[nid].ent_type_
#                 else:
#                     type2 = doc3[nid].ent_type_
#                 if type2 == 'QUESTION':
#                     temp = {'id2': nowid, 'ty2': type1, 'id1': nid, 'ty1': type2}
#                 else:
#                     temp = {'id1': nowid, 'ty1': type1, 'id2': nid, 'ty2': type2}
#                 ans.append(temp)
#                 # print ('{0}({1})     {2}({3})'.format(doc1[nowid].text,type1,doc1[nid].text,type2))
#                 # print(doc1[nowid].text,doc1[nid].text)
#                 find1(nid)
#     return nowid


# def find3(nowid):
#     num = 0
#     l = []
#     for child in doc4[nowid].children:
#         tid = child.i
#         if (doc1[tid]._.is_entity or doc3[tid]._.is_entity):
#             # print(num,tid)
#             num = num + 1
#             l.append(tid)
#             # print(doc1[nowid].text,doc1[tid].text)
#             # find1(tid)
#         else:
#             nid = find2(tid)
#             if (nid != tid):
#                 # print(num,nid)
#                 num = num + 1
#                 l.append(nid)
#                 # print(doc1[nowid].text,doc1[nid].text)
#                 # find1(nid)
#     # print(num)
#     # print(l)
#     if num == 1:
#         find1(l[0])
#     if num >= 2:
#         if (doc1[l[0]]._.is_entity):
#             type1 = doc1[l[0]].ent_type_
#         else:
#             type1 = doc3[l[0]].ent_type_
#         if (doc1[l[1]]._.is_entity):
#             type2 = doc1[l[1]].ent_type_
#         else:
#             type2 = doc3[l[1]].ent_type_
#         if type2 == 'QUESTION':
#             temp = {'id2': l[0], 'ty2': type1, 'id1': l[1], 'ty1': type2}
#         else:
#             temp = {'id1': l[0], 'ty1': type1, 'id2': l[1], 'ty2': type2}
#         ans.append(temp)
#         # print ('{0}({1})     {2}({3})'.format(doc1[l[0]].text,type1,doc1[l[1]].text,type2))
#         # print(doc1[l[0]].text,doc1[l[1]].text)
#         for k in l:
#             find1(k)
#     return nowid


# ans = []
# for token in doc4:
#     if (token.dep_ == (u'ROOT')):
#         if (doc1[token.i]._.is_entity or doc3[token.i]._.is_entity):
#             # print(token.i)
#             find1(token.i)
#         else:
#             find3(token.i)
# print(ans)
