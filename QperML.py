# -*- coding:utf-8 -*-
"""
    输入问题解析模块（机器学习版）
"""
import spacy
from spacy_lookup import Entity
# import numpy as np
from sentence_transformers import SentenceTransformer, util
import torch
# from termcolor import colored
import itertools
from information import entity_dict, relation_dict_query, special_type

class QueryParse:
    def __init__(self, nlp, entity_keys):
        """
        语义解析初始化
        :param question: 待解析问句
        """
        self.__topk = 6
        try:
            self.__bc = SentenceTransformer('/home/gerald/.cache/torch/sentence_transformers/distilbert-base-nli-mean-tokens')
        except:
            self.__bc = SentenceTransformer('distilbert-base-nli-mean-tokens')
        # self.__ynlp = spacy.load('en_core_web_sm')
        self.__nlp = nlp

        self.__entity_keys = list(entity_keys)  # 可以提问的实体空间
        for idx,_ in enumerate(self.__entity_keys):
            if _ == "prop":
                self.__entity_keys.pop(idx)
        # for key, values in entity_relation_dict.items():
        #     entity = Entity(keywords_list=values, label=key)
        #     self.__nlp.add_pipe(entity, name=key)
        # 换词表如下
        '''
            entity1 = Entity(keywords_list=['gone with the wind','movie','what movie'],label='MOV')
            self.__nlp.add_pipe(entity1, name='MOV')
            entity2 = Entity(keywords_list=['Marvin','han','qi','fang','who'],label='PERS')
            self.__nlp.add_pipe(entity2, name='PERS')
        '''

        # self.__questions = remodel_dict 
        '''
            换关系模板表如下
            self.__questions=["<p> act <m>","<p> actor <m>","<p> direct <m>",
                              "<p> director <m>","<p> write <m>","<p> writer <m>"]
        '''

        self.__unrelated_entity = []
        self.__stop = ['a', 'the']

    def __strategy__(self, document, segement=True, article=True, un_entity=True, replace=False):

        """
        策略函数
        input:
            document:   nlp实例
            model:      模板（questions列表）
            segement:   True时分割句子/False时保留完整句子
            article:    True时冠词保留/False时冠词移除
            un_entity:  True时其他实体保留/False时移除
            replace:    True时将模板中的<type>替换为实体/False时不替换
        output:
            查询句式
            匹配模板
            实体对位置
        """

        # p_list = []
        # m_list = []
        entity_dict = {}
        entity_dict_b = {}
        entity_dict_store = {}

        count = 0
        token_list = []

        whole_doc = []
        split_doc = []

        new_model = []

        # p_store = []
        # m_store = []

        # p_list_b = []
        # m_list_b = []

        for index, token in enumerate(document):
            if token.text in self.__stop and not article:
                count = count + 1
            elif token.text in self.__unrelated_entity and not un_entity:
                count = count + 1

            elif token.ent_type_ in self.__entity_keys:
                if token.ent_type_ not in entity_dict.keys():
                    entity_dict[token.ent_type_] =[]
                    entity_dict_b[token.ent_type_]=[]
                    entity_dict_store[token.ent_type_] = []
                entity_dict[token.ent_type_].append(index - count)
                entity_dict_b[token.ent_type_].append(index)
                token_list.append(token.text)
            else:
                token_list.append(token.text)

        label = []

        for head in entity_dict.keys():
            for tail in entity_dict.keys():
                if head == tail:
                    continue  ##自连 跳过, actor2actor不要了
                remodel_dict, entity_relation_dict = relation_dict_query(head, tail)
                if len(remodel_dict) == 0:
                    continue  ## 如果两节点不存在关系，跳过

                relation_dict = entity_relation_dict
                for i_index, i in enumerate(entity_dict[head]):
                    for j_index, j in enumerate(entity_dict[tail]):
                        temp = token_list.copy()
                        if not replace:
                            temp[i], temp[j] = '<'+head[0]+'>', '<'+tail[0]+'>'
                            new_model += [remodel_dict]
                        else:
                            temp_s = '//'.join(remodel_dict).replace('<'+head[0]+'>', temp[i]).replace('<'+tail[0]+'>', temp[j])
                            new_model += [temp_s.split('//')]
                            entity_dict_store[head].append(temp[i])
                            entity_dict_store[tail].append(temp[j])
                        whole_doc.append(' '.join(temp))
                        split_doc.append(' '.join(temp[min(i, j):max(i, j) + 1]))
                        # label.append([str(document[p_list_b[i_index]])+'[%i]'%p_list_b[i_index],
                        #              str(document[m_list_b[j_index]])+'[%i]'%m_list_b[j_index]])
                        label.append([entity_dict_b[head][i_index], entity_dict_b[tail][j_index]])

        if segement:
            return split_doc, new_model, label, relation_dict
        else:
            return whole_doc, new_model, label, relation_dict

    def __find_top__(self, queries_, questions_):
        """
        输入queries和对应questions的list，为每一个query找出最匹配的question
        """
        best = []
        #print(queries_)
        #print(questions_)

        for index, query in enumerate(queries_):
            question = questions_[index]
            doc_vecs = self.__bc.encode(question, convert_to_tensor=True)
            query_vec = self.__bc.encode(query, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(query_vec, doc_vecs)[0]
            #print(scores)
            best.append(scores)
            #print(float(scores[0]))
            #top_results = torch.topk(scores, k=1)
            #print(int(top_results[1][0]),float(top_results[0][0]))
            # best.append([query, question[int(top_results[1][0])], float(top_results[0][0])])
            #best. append(int(top_results[1][0]))
        return best

    def parse_keyword(self, question):
        """
        投票找出每一对实体最有可能的关系
        """
        doc1 = question
        # doc1 = self.__nlp(doc1)
        
        doc_l = ""
        for i in doc1:
            doc_l = doc_l + i.lemma_ + " "
	
        doc1 = self.__nlp(doc_l)

        ### 关系问题单独处理
        flag = False
        entity_sp = []
        entity_sp_property = []
        sp_relation = []

        for token in doc1:
            if token.ent_type_ in special_type:
                sp_relation.append(token.ent_type_)
                flag = True
                break        
        if flag:
            for token in doc1:
                if token._.is_entity and not(token.ent_type_ in (special_type + ["prop"])):
                    entity_sp.append(token.ent_type_)
                    entity_sp_property.append(token.text)
            return [entity_sp[0]],[entity_sp_property[0]],[entity_sp[1]],[entity_sp_property[1]],sp_relation
        else:
            entnum = 0
            for token in doc1:
                if token._.is_entity and not(token.ent_type_ in (special_type + ["prop"])):
                    entnum = entnum + 1
                    entity_sp.append(token.ent_type_)
                    entity_sp_property.append(token.text)
            # print(entity_sp)
            # print(entity_sp_property)
            if entnum == 1:
                return [entity_sp[0]],[entity_sp_property[0]]
        
        ### 三元组匹配
        entity_a = []
        entity_b = []
        entity_relation = []
        entity_a_property = []
        entity_b_property = []

        vote = {}  # 统计投票结果
        ent = {}
        cases = list(itertools.product([True, False], repeat=4))  # 4*4真值列表

        for case in cases:
            #print("-----------------------------------------------------------------")
            # 选择处理句子的策略
            queries, questions, label, relation_dict = self.__strategy__(doc1, segement=case[0],
                                                          article=case[1], un_entity=case[2], replace=case[3])

            #print("queries:    ",queries)
            #print("questions:     ",questions)
            #print("label:     ",label)
            #print("relation_dict:     ",relation_dict)
            # 对每一组pm，投出在所有策略下拥有最高票数的模板
            for index, ele in enumerate(self.__find_top__(queries, questions)):
                #print("******************************")
                #print("ele:     ",ele)
                #v = relation_dict['relate'][ele]
                pair = str(label[index][0]) + '/' + str(label[index][1])
                #print(pair)
                if pair not in vote.keys():
                    vote[pair] = {}
                    ent[pair] = [label[index][0], label[index][1]]
                for i,v in enumerate(relation_dict['relate']):
                    if v not in vote[pair]:
                        vote[pair][v] = float(ele[i])
                    else:
                        vote[pair][v] += float(ele[i])
                #print("******************************")
            #print("-----------------------------------------------------------------")
        #print(vote)
        for ele in vote.items():
            temp = ent[ele[0]]
            entity_a.append(doc1[temp[0]].ent_type_)
            entity_a_property.append(doc1[temp[0]].text)
            entity_b.append(doc1[temp[1]].ent_type_)
            entity_b_property.append(doc1[temp[1]].text)
            entity_relation.append(sorted(ele[1].items(), key=lambda item: item[1])[-1][0])

        return entity_a, entity_a_property, entity_b, entity_b_property, entity_relation

    #def lookdoc(self, doc1):
    #    for token in doc1:
    #        print(token.text, token._.is_entity, token.ent_type_)
    #    print()


if __name__ == "__main__":
    #question = "Who acted the movie directed by steven levine?"
    # question = "Who is the director and writer of Pierre et Jean?"
    # question = "What movie did steven levine direct"
    # question = "What movies are acted by Leonardo DiCaprio and Kate Winslet?"
    # question = "What company produce Titanic?"
    question = "what movies is acting by P1"
    print(question)

    print("===============Model initialize=================")
    print("Prepare entity dictionary")
    nlp = spacy.load('en_core_web_sm')
    nlp.remove_pipe('ner')
    entity_keys = entity_dict.keys()  # 可以提问的实体空间
    for key, values in entity_dict.items():
        entity = Entity(keywords_list=values, label=key)
        nlp.add_pipe(entity, name=key)   # 添加确定识别的NER列表


    test = QueryParse(nlp, entity_keys)
    question = nlp(question)
    #print(type(question))
    triplet = test.parse_keyword(question)
    print(triplet)
    # test.lookdoc()
    # a, a_p, b, b_p, r = test.parse_keyword(question)
    # print(a)
    # print(a_p)
    # print(b)
    # print(b_p)
    # print(r)
