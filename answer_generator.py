# -*- coding:utf-8 -*-
"""
    答案生成，可视化cypher语句生成模块
"""
import re

from information import url, login, line_break, entity_query_dict, property_entity_name
from post_cypher import QueryCypher


class Query2Answer:
    def __init__(self):
        self.__cypher = ""
        self.cypher = ""

    @staticmethod
    def __conj_based_appender__(match_line_list, where_line_list, return_line_list, logic):
        where_line_appender = []
        if logic == "and":
            match_line_list[0].extend(match_line_list[1])
            return_line_list[0].extend(return_line_list[1])
            where_line_appender = where_line_list[1]
        elif logic == "or":
            where_line_appender = []
            for dict_cnt in range(len(where_line_list[0])):
                k = next(iter(where_line_list[0][dict_cnt].keys()))
                v = next(iter(where_line_list[1][dict_cnt].values()))
                where_line_appender.append({k: v})
            for i in range(len(match_line_list[0])):
                k = next(iter(match_line_list[0][i].keys()))
                if match_line_list[0][i][k] == "":
                    match_line_list[0][i][k] = match_line_list[1][i][k]
                    return_line_list[0][i][k] = return_line_list[1][i][k]

        k = next(iter(where_line_list[0][0].keys()))
        v = next(iter(where_line_list[0][0].values()))
        where_line_list[0][0][k] = "(" + v
        k = next(iter(where_line_list[0][-1].keys()))
        v = next(iter(where_line_list[0][-1].values()))
        where_line_list[0][-1][k] = v + ") " + logic

        k = next(iter(where_line_appender[0].keys()))
        v = next(iter(where_line_appender[0].values()))
        where_line_appender[0][k] = " (" + v
        k = next(iter(where_line_appender[-1].keys()))
        v = next(iter(where_line_appender[-1].values()))
        where_line_appender[-1][k] = v + ")"

        where_line_list[0].extend(where_line_appender)
        return match_line_list[0], where_line_list[0], return_line_list[0]

    @staticmethod
    def __relation_where_plus_conj__(where_line_list, logic):
        """
        逻辑连词组装
        :param where_line_list: 待组装的where
        :param logic: 逻辑连词
        :return: 组装好的where语句
        """
        where_queue = []
        logic_i = len(logic)
        if logic_i > 0:
            for i in range(len(logic), 0, -2):
                logic_i = logic_i - 1
                where_line = ""
                if where_line_list[i] == "" and where_line_list[i - 1] != "":
                    where_line = "(" + where_line_list[i - 1] + ")"
                elif where_line_list[i] != "" and where_line_list[i - 1] == "":
                    where_line = "(" + where_line_list[i] + ")"
                elif where_line_list[i] != "" and where_line_list[i - 1] != "":
                    where_line = "((" + where_line_list[i] + ") " + logic[logic_i] + " (" + where_line_list[
                        i - 1] + "))"
                where_queue.append(where_line)
            if logic_i > 0:
                queue_i = 0
                for i in range(logic_i - 1, 0, -1):
                    where_line = "(" + where_queue[queue_i] + " " + logic[i] + " " + where_queue[queue_i + 1] + ")"
                    where_queue.append(where_line)
                    queue_i = queue_i + 2
                where_line = "(" + where_queue[-2] + " " + logic[0] + " " + where_queue[-1] + ")"
            else:
                where_line = where_queue[0]
        else:
            where_line = ""
            for phrase in where_line_list:
                if phrase != "":
                    where_line = where_line + "AND (" + phrase + ")"
            where_line = where_line[4:]
        return where_line

    def __match_where_plus_conj__(self, match_line_list, where_line_list, return_line_list, logic):
        """
        逻辑连词组装
        :param match_line_list: 待组装的match
        :param where_line_list: 待组装的where
        :param return_line_list: 待组装的return
        :param logic: 逻辑连词
        :return: 组装好的where语句
        """
        match_queue = []
        where_queue = []
        return_queue = []
        match_line = ""
        where_line = ""
        return_line = ""
        logic_i = len(logic)
        if logic_i > 0:
            for i in range(len(logic), 0, -2):
                logic_i = logic_i - 1
                match_phrase, where_phrase, return_phrase = self.__conj_based_appender__([match_line_list[i - 1],
                                                                                          match_line_list[i]],
                                                                                         [where_line_list[i - 1],
                                                                                          where_line_list[i]],
                                                                                         [return_line_list[i - 1],
                                                                                          return_line_list[i]],
                                                                                         logic[logic_i])
                match_queue.append(match_phrase)
                where_queue.append(where_phrase)
                return_queue.append(return_phrase)
            if logic_i > 0:
                queue_i = 0
                for i in range(logic_i - 1, 0, -1):
                    match_phrase, where_phrase, return_phrase = self.__conj_based_appender__([match_queue[queue_i],
                                                                                              match_queue[queue_i + 1]],
                                                                                             [where_queue[queue_i],
                                                                                              where_queue[queue_i + 1]],
                                                                                             [return_queue[queue_i],
                                                                                              return_queue[
                                                                                                  queue_i + 1]],
                                                                                             logic[i])
                    match_queue.append(match_phrase)
                    where_queue.append(where_phrase)
                    return_queue.append(return_phrase)
                    queue_i = queue_i + 2
                match_phrase, where_phrase, return_phrase = self.__conj_based_appender__([match_queue[-2],
                                                                                          match_queue[-1]],
                                                                                         [where_queue[-2],
                                                                                          where_queue[-1]],
                                                                                         [return_queue[-2],
                                                                                          return_queue[-1]],
                                                                                         logic[0])
            else:
                match_phrase = match_queue[0]
                where_phrase = where_queue[0]
                return_phrase = return_queue[0]
            for line in match_phrase:
                a, b, t = next(iter(line.keys())).split(".")
                match_line = match_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
            for line in where_phrase:
                a, b, t = next(iter(line.keys())).split(".")
                where_line = where_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
            for line in return_phrase:
                a, b, t = next(iter(line.keys())).split(".")
                return_line = return_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
        else:
            for i in range(0, len(where_line_list)):
                for line in match_line_list[i]:
                    a, b, t = next(iter(line.keys())).split(".")
                    match_line = match_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
                for line in where_line_list[i]:
                    a, b, t = next(iter(line.keys())).split(".")
                    where_line = where_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
                for line in return_line_list[i]:
                    a, b, t = next(iter(line.keys())).split(".")
                    return_line = return_line + next(iter(line.values())).format(cnt0=t, cnt1=a, cnt2=b)
        return match_line, where_line, return_line

    @staticmethod
    def __query_templates_match__(entity_name, property_type, property_value, neg, loc, attr_idx, info):
        """
        属性查询语句模板匹配
        :param entity_name: 实体类型
        :param property_type: 实体属性类型
        :param property_value: 实体属性值
        :param neg：否定词
        :param loc: 头实体or尾实体
        :return:
            match_phrase: 参与match语句组装
            where_phrase: 非查询对象的限定语句，参与where语句的组装
            where_for_return: 查询对象的限定语句，参与where语句的组装
            return_phrase：参与return语句的组装
            long_type_match： (c)-[r1]-(a)-[r]-(b)-[r2]-(d) or (a)-[r]-(b)
            r_prop_flag：匹配为第二种模板时为True
        """
        type_name = ['a', 'b', 'c' + attr_idx + '{cnt1}', 'b{cnt2}', 'a{cnt1}',
                     'd' + attr_idx + '{cnt2}', 'c' + attr_idx, 'd' + attr_idx]
        entity_name_list = [':{label})-[rr', ':' + entity_name + ')-[rrr', ':' + entity_name + ')', ':{label})']
        cnt_name = ["{cnt1}", "{cnt2}"]
        return_special_prop_phrase = ""
        match_special_prop_phrase = ""
        entity_query_idx = entity_query_dict[entity_name + '.' + property_type]
        if entity_query_idx == 1:
            '''
            where_phrase = {type_name}{cntk}.{property_type}='{property_value}'
            return_phrase = {type_name}{cntk}.{property_type} (for parsing, query stage: id({type_name}{cntk}))
            '''
            if neg is not None:
                where_phrase = "none(x in nodes(p{cnt0}) WHERE x." + property_type + "='" + property_value + "')"
            else:
                where_phrase = type_name[loc] + cnt_name[loc] + "." + property_type + "='" + property_value + "'"
            return_phrase = ",id(" + type_name[loc] + "{idx})"
            return_type = "nodes$" + property_type + "$" + info
            where_for_return = ""
        elif entity_query_idx == 2:
            '''
            where_phrase = r{cntk}.{property_type}='{property_value}'
            return_phrase = r{cntk}.{property_type} (for parsing, query stage: id(r{cntk}))
            '''
            if neg is not None:
                where_phrase = "none(x in relationships(p{cnt0}) WHERE x." + property_type + "='" + property_value + "')"
            else:
                where_phrase = "r" + cnt_name[loc] + "." + property_type + "='" + property_value + "'"
            return_phrase = ",id(r{idx})"
            return_type = "relationships$" + property_type + "$" + info
            where_for_return = ""
        else:
            entity_name_list_sub = entity_name_list
            entity_name_list_sub[0] = entity_name_list_sub[0].format(label=property_entity_name[property_type])
            entity_name_list_sub[3] = entity_name_list_sub[3].format(label=property_entity_name[property_type])
            type_name_sub = type_name[2: 6]
            '''
            match_special_prop_phrase = 
            p{cnt0}_{cntk}=(c{cntk}:{entity_label})-[rr{cnt0}_{cntk}]-(a{cntk}:{entity_name}),
            or 
            p{cnt0}_{cntk}=(b{cntk}:{entity_name})-[rrr{cnt0}_{cntk}]-(d{cntk}:{entity_label}),
            '''
            match_special_prop_phrase = "p{cnt0}_" + cnt_name[loc] + "=(" + type_name_sub[loc] + \
                                        entity_name_list_sub[loc] + "{cnt0}_" + cnt_name[loc] + \
                                        "]-(" + type_name_sub[loc + 2] + entity_name_list_sub[loc + 2] + ","
            return_special_prop_phrase = "p{cnt0}_" + cnt_name[loc] + ","
            if entity_query_idx == 3:
                '''
                where_phrase = {type_name}{cntk}.{property_type}='{property_value}'
                return_phrase = {type_name}{cntk}.{property_type} (for parsing, query stage: id({type_name}{cntk}))
                '''
                if property_type == "release_date":  # TODO，命名缺乏一般规律
                    property_type = "date"
                if neg is not None:
                    where_phrase = "none(x in nodes(p{cnt0}) WHERE x." + property_type + "='" + property_value + "')"
                else:
                    where_phrase = type_name[loc+6] + cnt_name[loc] + "." + property_type + "='" + property_value + "'"
                where_for_return = ""
                return_phrase = ",id(" + type_name[loc + 6] + "{idx})"
                return_type = "nodes$" + property_type + "$" + info
            elif entity_query_idx == 4:
                '''
                where_phrase = {type_name}{cntk}.label='{property_type}' AND {type_name}{cntk}.value='{property_value}'
                where_for_return = {type_name}{cntk}.label='{property_type}'
                return_phrase = {type_name}{cntk}.value (for parsing, query stage: id({type_name}{cntk}))
                '''
                if neg is not None:
                    where_phrase = "none(x in nodes(p{cnt0}) WHERE x.label='" + property_type +\
                                   "' AND x.value='" + property_value + "')"
                    where_for_return = " AND none(x in nodes(p{cnt0}) WHERE x.label='" + property_type + "')"
                else:
                    where_phrase = type_name[loc + 6] + cnt_name[loc] + ".label='" + property_type +\
                                   "' AND " + type_name[loc + 6] + cnt_name[loc] + ".value='" + property_value + "'"
                    where_for_return = " AND " + type_name[loc + 6] + cnt_name[loc] + ".label='" + property_type + "'"
                return_phrase = ",id(" + type_name[loc + 6] + "{idx})"
                return_type = "nodes$1value" + "$" + info
            elif entity_query_idx == 5:
                '''
                where_phrase = {type_name}{cntk}.cate='{property_type}' AND {type_name}{cntk}.value='{property_value}'
                where_for_return = {type_name}{cntk}.cate='{property_type}'
                return_phrase = {type_name}{cntk}.value (for parsing, query stage: id({type_name}{cntk}))
                '''
                if neg is not None:
                    where_phrase = "none(x in nodes(p{cnt0}) WHERE x.cate='" + property_type +\
                                   "' AND x.value='" + property_value + "')"
                    where_for_return = " AND none(x in nodes(p{cnt0}) WHERE x.cate='" + property_type + "')"
                else:
                    where_phrase = type_name[loc + 6] + cnt_name[loc] + ".cate='(" + property_type +\
                                   "' AND " + type_name[loc + 6] + cnt_name[loc] + ".value='" + property_value + "'"
                    where_for_return = " AND " + type_name[loc + 6] + cnt_name[loc] + ".cate='" + property_type + "'"
                return_phrase = ",id(" + type_name[loc + 6] + "{idx})"
                return_type = "nodes$1value" + "$" + info
            elif entity_query_idx == 6:
                '''
                where_for_return = {type_name}{cntk}.cate='{property_type}'
                return_phrase = {type_name}{cntk}.label (for parsing, query stage: id({type_name}{cntk}))
                '''
                where_phrase = ""
                if neg is not None:
                    where_for_return = " AND none(x in nodes(p{cnt0}) WHERE x.cate='" + property_type + "')"
                else:
                    where_for_return = " AND " + type_name[loc + 6] + cnt_name[loc] + ".cate='" + property_type + "'"
                return_phrase = ",id(" + type_name[loc + 6] + "{idx})"
                return_type = "nodes$1label" + "$" + info
        where_phrase = " AND " + where_phrase

        return match_special_prop_phrase, where_phrase, where_for_return, \
               return_phrase, return_type, return_special_prop_phrase

    # TODO：
    def __match_relation__(self, triplet_set, attlist_set, logic, neg, movie_thres):
        """
        查询符合要求的头尾实体关系
        :param triplet_set: 三元组 [ ([entity_a1], [entity_a_property1], [entity_b1], [entity_b_property1], [relation1]),
                                    ([entity_a2], [entity_a_property2], [entity_b2], [entity_b_property2], [relation2]),
                                    ...]
        :param a_property_type: 头实体node property type
        :param b_property_type: 尾实体node property type
        :param logic: 逻辑连接词
        :param neg: 条件否定词
        :return: 查询结果，即头尾实体关系（头指向尾）
        """
        print("----enter relation match section----")
        match_line = "MATCH "
        where_line_list = []
        return_line = "RETURN DISTINCT "
        return_word = ""
        return_cnt = 0
        unwind_word = ""

        match_cmp_list = {0: [], 1: []}
        where_cmp_list = {0: [], 1: []}
        cnt_list = {0: [], 1: []}
        where_list = {0: [], 1: []}

        triplet_key = [0, 2]
        cnt = [0, 0]
        cypher_name = ["a", "b"]
        if len(neg) < len(triplet_set):
            for _ in range(len(neg), len(triplet_set)):
                neg.append(None)
        for i in range(0, len(triplet_set)):
            where_line_i = ""
            for j in range(0, len(triplet_set[0][0])):
                cnt_plus_counter = 0
                t = i * len(triplet_set[0][0]) + j
                match_special_template_j = ""
                for k in range(0, 2):
                    entity_name = triplet_set[i][triplet_key[k]][j]
                    entity_property = triplet_set[i][triplet_key[k] + 1][j]
                    cnt[k] = t
                    for w in range(0, len(attlist_set[t][k])):
                        property_type = attlist_set[t][k][w][1]
                        cmp_str = entity_name + property_type[k] + entity_property
                        match_special_template, where_phrase_template, \
                        _, _, _, _ = self.__query_templates_match__(entity_name, property_type,
                                                                    entity_property, neg[i], k,
                                                                    str(i) + str(w),
                                                                    attlist_set[t][k][w][0])
                        match_special_template_j = match_special_template_j + match_special_template
                        if entity_property != "":
                            if (cmp_str + triplet_set[i][4][j]) in where_cmp_list[k]:
                                where_line_i = where_line_i + where_list[k][where_cmp_list[k].index(cmp_str + triplet_set[i][4][j])]
                            else:
                                where_cmp_list[k].append(cmp_str + triplet_set[i][4][j])
                                if cmp_str not in match_cmp_list[k]:
                                    cnt_list[k].append(cnt[k])
                                    match_cmp_list[k].append(cmp_str)
                                else:
                                    cnt[k] = cnt_list[k][match_cmp_list[k].index(cmp_str)]
                                cnt_plus_counter = cnt_plus_counter + 1
                                where_phrase = where_phrase_template
                                # if neg[i] is not None:
                                #     where_phrase = " AND none(x" + str(cnt[k]) + " in nodes(p" + str(t) + \
                                #                    ") WHERE x" + str(cnt[k]) + "." + property_type[k] + \
                                #                    "='" + entity_property + "')"
                                # else:
                                #     where_phrase = " AND " + cypher_name[k] + str(cnt[k]) + "." + property_type[k] + \
                                #                    "='" + entity_property + "'"
                                if entity_name == "movie":
                                    where_phrase = where_phrase + " AND " + cypher_name[k] + str(
                                        cnt[k]) + ".douban_movie_id<>'nan'"
                                where_list[k].append(where_phrase)
                                where_line_i = where_line_i + where_phrase
                # relation
                if cnt_plus_counter != 0:
                    if triplet_set[i][4][j] != "REQU":  # 不是REQU
                        if neg[i] is not None:
                            where_line_i = where_line_i + " AND none(z" + str(t) + " in relationships(p" + str(t) + \
                                           ") WHERE type(z" + str(t) + ")=~'" + triplet_set[i][4][j] + ".*')"
                        else:
                            where_line_i = where_line_i + " AND type(r" + str(t) + ")=~'" + triplet_set[i][4][j] + ".*'"
                        match_line = match_line + "p" + str(t) + "=(a" + str(cnt[0]) + ":" + triplet_set[i][0][j] + \
                                     ")-[r" + str(t) + "]-(b" + str(cnt[1]) + ":" + triplet_set[i][2][j] + "),"
                    else:
                        match_line = match_line + "p" + str(t) + "=(a" + str(cnt[0]) + ":" + triplet_set[i][0][j] + \
                                     ")-[r" + str(t) + "*{hop}]-(b" + str(cnt[1]) + ":" + triplet_set[i][2][j] + "),"
                        where_line_i = where_line_i + " AND all(x" + str(t) + " in nodes(p" + str(t) + \
                                       ") WHERE none(label" + str(t) + " in labels(x" + str(t) + \
                                       ") WHERE label" + str(t) + " in ['user','keywords','videos', 'imgs']))" + \
                                       " AND all(x" + str(t) + " in relationships(p" + str(t) + \
                                       ") WHERE type(x" + str(t) + ")<>'actor2actor' and type(x" + str(t) + \
                                       ")<>'other' and type(x" + str(t) + ")<>'bothlike')"
                        unwind_word = unwind_word + ",r" + str(t) + " as rr" + str(t)
                        return_word = return_word + ",type(rr" + str(t) + ")"
                        return_cnt = return_cnt + 1
                    return_line = return_line + "p" + str(t) + ","
                    where_line_list.append(where_line_i[5:])
        if len(where_line_list) > 1:
            where_line = "WHERE " + self.__relation_where_plus_conj__(where_line_list, logic)
        else:
            where_line = "WHERE " + where_line_list[0]
        self.__cypher = match_line[:-1] + " " + where_line + " " + \
                        "UNWIND " + unwind_word[1:] + " " + return_line + "{return_w}{limit}"
        ans = []
        for i in range(1, 5):  # TODO: 只考虑一对，多跳条件不支持
            if i == 1:
                cypher = self.__cypher.format(hop=i, return_w=return_word[1:], limit="", cnt1=0, cnt2=0)
            elif i == 2:
                cypher = self.__cypher.format(hop=i, return_w="null", limit=" LIMIT 5", cnt1=0, cnt2=0)
            else:
                cypher = self.__cypher.format(hop=i, return_w="null", limit=" LIMIT 1", cnt1=0, cnt2=0)
            print("----jump = " + str(i))
            print("生成的cypher查询语句：" + line_break + cypher)
            print("Querying Remote Database: It may take some time")
            res = QueryCypher(url, login, cypher)
            ans_list = []
            if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
                if return_cnt > 0:
                    for i in range(-1, -return_cnt - 1, -1):
                        res_type = res["results"][0]["columns"][i]
                        if res_type == "null":
                            ans.append({"text": '多跳关系', "url": None})
                            continue
                        for j in range(0, len(res["results"][0]["data"])):
                            if res["results"][0]["data"][j]["row"][i] not in ans_list:
                                ans.append({"text": res["results"][0]["data"][j]["row"][i], "url": None})
                                ans_list.append(res["results"][0]["data"][j]["row"][i])
                break
        return ans, res

    def __match_node__(self, triplet_set, attlist_set, logic, neg, movie_thres):
        """
        查询符合要求的实体属性值
        :param triplet_set: 三元组 [ ([entity_a1], [entity_a_property1], [entity_b1], [entity_b_property1], [relation1]),
                                    ([entity_a2], [entity_a_property2], [entity_b2], [entity_b_property2], [relation2]),
                                    ...]
        :param attlist_set: 属性列表 [<逻辑词连接> [<头实体尾实体>[<同实体不同属性>[entity1_name, 1_property_type, 1_property],
                                                                             [entity1_name, 1_property_type, 1_property]
        :param logic: 逻辑连接词
        :param neg: 条件否定词
        :return: 返回查询结果，即尾实体属性值
        """
        print("----enter node match section----")
        match_cmp_list = []
        match_cmp_cnt_list = []
        return_where_list = []
        return_words = []
        return_idx_list = []
        return_property_list = []
        return_cnt = 0

        match_line_list = []
        where_line_list = []
        return_line_list = []

        cmp_list = {0: [], 1: []}
        cnt_list = {0: [], 1: []}
        where_list = {0: [], 1: []}

        triplet_key = [0, 2]
        cnt = [0, 0]
        cypher_name = ["a", "b"]
        for i in range(0, len(triplet_set)):
            where_line_i = []
            match_line_i = []
            return_line_i = []
            len_rel_flag = len(triplet_set[i])
            where_movie_cmp_list = []
            for j in range(0, len(triplet_set[0][0])):
                match_line_j = ""
                match_special_template_j = ""
                where_line_j = ""
                return_line_j = ""
                return_special_j = ""
                t = i * len(triplet_set[0][0]) + j
                k_len = 1 if len_rel_flag < 3 else 2
                match_cmp_str = ""
                key = ""
                for k in range(0, k_len):
                    cnt[k] = t
                    movie_thres_phrase = " AND " + cypher_name[k] + "{cnt" + str(k + 1) + "}.douban_movie_id<>'nan'"
                    entity_name = triplet_set[i][triplet_key[k]][j]
                    entity_property = triplet_set[i][triplet_key[k] + 1][j]
                    for w in range(0, len(attlist_set[t][k])):
                        property_type = attlist_set[t][k][w][1]
                        match_special_template, where_phrase_template,\
                        where_for_return_template, return_word_template,\
                        return_type, return_special = self.__query_templates_match__(entity_name, property_type,
                                                                                     entity_property, neg[i], k,
                                                                                     str(i) + str(w),
                                                                                     attlist_set[t][k][w][0])
                        match_special_template_j = match_special_template_j + match_special_template
                        return_special_j = return_special_j + return_special
                        cmp_str = entity_name + property_type + entity_property
                        if cmp_str in cmp_list[k]:
                            where_line_j = where_line_j + where_list[k][cmp_list[k].index(cmp_str)]
                            cnt[k] = cnt_list[k][cmp_list[k].index(cmp_str)]
                        else:
                            cmp_list[k].append(cmp_str)
                            cnt_list[k].append(cnt[k])
                            # 不是疑问词或空，设置where语句
                            if re.match("^(wh(at|o|ich)|$)", attlist_set[t][k][w][2], re.I) is None:
                                where_phrase = where_phrase_template
                            # 是疑问词，设置return语句
                            elif re.match("^(wh(at|o|ich))", attlist_set[t][k][w][2], re.I):
                                return_word = return_word_template.format(idx=str(cnt[k]))
                                if return_word in return_words:
                                    return_idx_list.append(return_idx_list[return_words.index(return_word)])
                                else:
                                    return_words.append(return_word)
                                    return_idx_list.append(return_cnt)
                                return_property_list.append(return_type)
                                return_cnt = return_cnt + 1
                                where_phrase = where_for_return_template
                            where_list[k].append(where_phrase)
                            where_line_j = where_line_j + where_phrase
                    if movie_thres_phrase + str(cnt[k]) not in where_movie_cmp_list and entity_name == "movie":
                        where_movie_cmp_list.append(movie_thres_phrase + str(cnt[k]))
                        where_line_j = where_line_j + movie_thres_phrase
                    key = key + str(cnt[k]) + "." if k_len == 2 else key + str(cnt[k]) + ".."
                    match_cmp_str = match_cmp_str + cmp_str
                path_format = ['', triplet_set[i][(k_len-1)*4][j], "),",
                               ")-[r{cnt0}]-(b{cnt2}:" + triplet_set[i][k_len][j] + "),"]
                match_cmp_str = match_cmp_str + path_format[k_len - 1]
                if match_cmp_str not in match_cmp_list:
                    return_line_j = "p{cnt0},"
                    return_line_j = return_line_j + return_special_j
                    match_line_j = "p" + str(t) + "=(a{cnt1}:" + triplet_set[i][0][j] +\
                                   path_format[k_len + 1] + match_special_template_j
                    match_cmp_list.append(match_cmp_str)
                    if neg[i] is not None:
                        where_phrase = " AND none(z{cnt0} in relationships(p{cnt0}) WHERE type(z{cnt0})=~'{relation}.*')"
                    else:
                        where_phrase = " AND type(r{cnt0})=~'{relation}.*'"
                    match_cmp_cnt_list.append(t)
                    if len_rel_flag < 5:
                        where_phrase = ""
                    return_where_list.append(where_phrase)
                else:
                    where_phrase = return_where_list[match_cmp_list.index(match_cmp_str)]
                    t = match_cmp_cnt_list[match_cmp_list.index(match_cmp_str)]
                key = key + str(t)
                match_line_i.append({key: match_line_j})
                where_line_i.append({key: where_line_j + where_phrase.format(relation=path_format[k_len - 1], cnt0="{cnt0}")})
                return_line_i.append({key: return_line_j})

            where_line_i[0][next(iter(where_line_i[0].keys()))] = next(iter(where_line_i[0].values()))[5:]
            match_line_list.append(match_line_i)
            where_line_list.append(where_line_i)
            return_line_list.append(return_line_i)

        match_line, \
        where_line, \
        return_line = self.__match_where_plus_conj__(match_line_list, where_line_list, return_line_list, logic)
        self.__cypher = "MATCH " + match_line[:-1] + line_break + \
                        "WHERE " + where_line + line_break + \
                        "RETURN DISTINCT " + return_line + ''.join(return_words)[1:]

        print("----生成的cypher查询语句：" + line_break + self.__cypher)
        print("----Querying Remote Database: It may take some time")
        res = QueryCypher(url, login, self.__cypher)
        ans = self.__node_match_ans_parse__(res, return_cnt, return_idx_list, return_property_list)
        return ans, res

    @staticmethod
    def __node_match_ans_parse__(res, return_cnt, return_idx_list, return_property_list):
        ans = []
        info_dict = {}
        unk_dict = {}
        cnt = 0
        if return_cnt > 0:
            if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
                for i in range(-1, -return_cnt - 1, -1):
                    for j in range(0, len(res["results"][0]["data"])):
                        id = res["results"][0]["data"][j]["row"][return_idx_list[i] - max(return_idx_list) - 1]
                        ans_url = "nan"
                        return_prop = return_property_list[i].split("$")
                        for part in res["results"][0]["data"][j]["graph"][return_prop[0]]:
                            if part["id"] == str(id):
                                if return_prop[1] in ["1label", "1value"]:
                                    text = part["properties"][return_prop[1][1:]]
                                elif return_prop[1] in part["properties"].keys():
                                    text = part["properties"][return_prop[1]]
                                    if "person" in part["labels"] and "website" in part["properties"].keys():
                                        ans_url = part["properties"]["website"]
                                    elif "movie" in part["labels"] and "url" in part["properties"].keys():
                                        ans_url = part["properties"]["url"]
                                else:
                                    continue
                                if ans_url == "nan":
                                    ans_url = "https://www.baidu.com/s?wd=" + text
                                if return_prop[2] != "INFO":
                                    ans.append({"text": text, "url": ans_url})
                                    if return_prop[2] == "UNK":
                                        unk_dict[len(ans) - 1] = j
                                    cnt = cnt + 1
                                else:
                                    info_dict[j] = text + ": "
                for k, v in unk_dict.items():
                    ans[k]["text"] = info_dict[v] + ans[k]["text"]
        ans_list = []
        for i in range(len(ans)):
            if ans[i] not in ans_list:
                ans_list.append(ans[i])

        return ans_list

    @staticmethod
    def __attr__(attlist, tri_type, tri_value, language_flag):
        attr_tri = []
        attr = [tri_value, "primaryName", "cond"]
        if language_flag == 'en':
            if tri_type == "person":
                attr[1] = "primaryName"
            elif tri_type == "movie":
                attr[1] = "primaryTitle"
        elif language_flag == 'zh':
            if tri_type == "person":
                attr[1] = "Chinese_name"
            elif tri_type == "movie":
                attr[1] = "Chinese_title"
        if tri_type in ["companies", "event"]:
            attr[1] = "name"
        if tri_type == tri_value:
            attr[2] = ""
        attr_tri.append(attr)
        flag = False
        for attr in attlist:
            if re.search("( |^)" + tri_value, attr[0], re.I):
                if attr[1] in ["primaryName", "primaryTitle", "Chinese_name", "Chinese_title", "name"]:
                    flag = (attr[2] == "what")
                    attr_tri[0][2] = "what"
                else:
                    if attr[2] == "what" and attr_tri[0][2] == "":
                        attr_tri[0][0] = "INFO"
                        attr_tri[0][2] = "what"
                        attr[0] = "UNK"
                    attr_tri.append(attr)
        return attr_tri, flag

    @staticmethod
    def __attr_adj__(flag, attr1, attr2):
        if flag and attr2[0][2] == "":
            attr1[0][0] = "UNK"
            attr2[0][2] = "what"
            attr2[0][0] = "INFO"

    def __keyword_translator__(self, language_flag, triplet_set, attlist_set):
        new_attlist_set = []
        relate_flag = False
        for i in range(0, len(triplet_set)):
            for j in range(0, len(triplet_set[0][0])):
                att_list = []
                attr, f1 = self.__attr__(attlist_set[i], triplet_set[i][0][j], triplet_set[i][1][j], language_flag)
                att_list.append(attr)
                if len(triplet_set[i]) >= 4:
                    attr, f2 = self.__attr__(attlist_set[i], triplet_set[i][2][j], triplet_set[i][3][j], language_flag)
                    att_list.append(attr)
                    self.__attr_adj__(f1, att_list[0], att_list[1])
                    self.__attr_adj__(f2, att_list[1], att_list[0])
                    # TODO:修改数据库
                    if re.search("( |^)direct", triplet_set[i][4][j], re.I):
                        triplet_set[i][4][j] = "direct"
                    elif re.search("( |^)act", triplet_set[i][4][j], re.I):
                        triplet_set[i][4][j] = "act"
                    elif triplet_set[i][4][j] == "REQU":
                        relate_flag = True
                new_attlist_set.append(att_list)
        return triplet_set, new_attlist_set, relate_flag

    def get_answer(self, lang, triplet_set, attlist_set, logic, neg, movie_thres):
        """
        获得问题的查询结果
        :param lang: 语言类型
        :param triplet_set: 三元组
        :param attlist_set: 属性列表
        :param logic: 逻辑连接词
        :param neg: 条件否定词
        :param movie_thres:
        :return: 返回输入问题的答案
        """

        triplet_set, attlist_set, relate_flag = self.__keyword_translator__(lang, triplet_set, attlist_set)
        if relate_flag:
            ans, visual_ans = self.__match_relation__(triplet_set, attlist_set, logic, neg, movie_thres)
        else:
            ans, visual_ans = self.__match_node__(triplet_set, attlist_set, logic, neg, movie_thres)
        return ans, visual_ans

    @staticmethod
    def get_additional_answer(json_res, limitation):
        # cypher_img = "MATCH (a:movie)-[r]-(b:imgs)" + line_break + \
        #              "WHERE id(a)={id}" + line_break + "RETURN b LIMIT {limitation}"
        cypher_review = "MATCH (a:movie)-[r]-(b:reviews)" + line_break + \
                        "WHERE id(a)={id}" + line_break + "RETURN b LIMIT {limitation}"
        add_visual_ans = []
        movie_id_list = []
        for data in json_res["results"][0]["data"]:
            for node in data["graph"]["nodes"]:
                if "movie" in node["labels"]:
                    movie_id = int(node["id"])
                    if movie_id not in movie_id_list:
                        movie_id_list.append(movie_id)
                        # query_res = QueryCypher(url, login, cypher_img.format(limitation=limitation, id=movie_id))
                        # add_visual_ans.append(query_res)
                        query_res = QueryCypher(url, login, cypher_review.format(limitation=limitation, id=movie_id))
                        add_visual_ans.append(query_res)
        return add_visual_ans
    # relation
    # # head
    # cmp_str = triplet_set[i][0][j] + a_property_type[t] + triplet_set[i][1][j]
    # if triplet_set[i][1][j] != "":  # 不是空
    #     if (cmp_str + triplet_set[i][4][j]) in a_where_cmp_list:
    #         where_line_i = where_line_i + a_where_list[
    #             a_where_cmp_list.index(cmp_str + triplet_set[i][4][j])]
    #     else:
    #         a_where_cmp_list.append(cmp_str + triplet_set[i][4][j])
    #         if cmp_str not in a_match_cmp_list:
    #             a_cnt = a_cnt + 1
    #             a_match_cmp_list.append(cmp_str)
    #         cnt_plus_counter = cnt_plus_counter + 1
    #         if neg[i] is not None:
    #             # where_phrase = " AND none(x" + str(a_cnt) + " in nodes(p" + str(t) + \
    #             #                ") WHERE x" + str(a_cnt) + "." + a_property_type[t] + \
    #             #                "=~'(?i)" + triplet_set[i][1][j] + "')"
    #             where_phrase = " AND none(x" + str(a_cnt) + " in nodes(p" + str(t) + \
    #                            ") WHERE x" + str(a_cnt) + "." + a_property_type[t] + \
    #                            "='" + triplet_set[i][1][j] + "')"
    #         else:
    #             # where_phrase = " AND a" + str(a_cnt) + "." + a_property_type[t] + \
    #             #                "=~'(?i)" + triplet_set[i][1][j] + "'"
    #             where_phrase = " AND a" + str(a_cnt) + "." + a_property_type[t] + \
    #                            "='" + triplet_set[i][1][j] + "'"
    #         if triplet_set[i][0][j] == "movie":
    #             # where_phrase = where_phrase + "AND toINT(a" + str(a_cnt) + ".numVotes)>" + str(movie_thres)
    #             where_phrase = where_phrase + " AND a" + str(a_cnt) + ".douban_movie_id<>'nan'"
    #         a_where_list.append(where_phrase)
    #         where_line_i = where_line_i + where_phrase
    # # tail
    # cmp_str = triplet_set[i][2][j] + b_property_type[t] + triplet_set[i][3][j]
    # if triplet_set[i][3][j] != "":  # 不是空
    #     if (cmp_str + triplet_set[i][4][j]) in b_where_cmp_list:
    #         where_line_i = where_line_i + b_where_list[
    #             b_where_cmp_list.index(cmp_str + triplet_set[i][4][j])]
    #     else:
    #         b_where_cmp_list.append(cmp_str + triplet_set[i][4][j])
    #         if cmp_str not in b_match_cmp_list:
    #             b_cnt = b_cnt + 1
    #             b_match_cmp_list.append(cmp_str)
    #         cnt_plus_counter = cnt_plus_counter + 1
    #         if neg[i] is not None:
    #             # where_phrase = " AND none(y" + str(b_cnt) + " in nodes(p" + str(t) + \
    #             #                ") WHERE y" + str(b_cnt) + "." + b_property_type[t] + \
    #             #                "=~'(?i)" + triplet_set[i][3][j] + "')"
    #             where_phrase = " AND none(y" + str(b_cnt) + " in nodes(p" + str(t) + \
    #                            ") WHERE y" + str(b_cnt) + "." + b_property_type[t] + \
    #                            "='" + triplet_set[i][3][j] + "')"
    #         else:
    #             # where_phrase = " AND b" + str(b_cnt) + "." + b_property_type[t] + \
    #             #                "=~'(?i)" + triplet_set[i][3][j] + "'"
    #
    #             where_phrase = " AND b" + str(b_cnt) + "." + b_property_type[t] + \
    #                            "='" + triplet_set[i][3][j] + "'"
    #         if triplet_set[i][2][j] == "movie":
    #             # where_phrase = where_phrase + "AND toINT(b" + str(b_cnt) + ".numVotes)>" + str(movie_thres)
    #             where_phrase = where_phrase + " AND b" + str(b_cnt) + ".douban_movie_id<>'nan'"
    #         b_where_list.append(where_phrase)
    #         where_line_i = where_line_i + where_phrase

    # node
    # # head
    # cmp_str = triplet_set[i][0][j] + a_property_type[t] + triplet_set[i][1][j]
    # a_cnt = t
    # # 不是疑问词或空，设置where语句
    # if re.match("^(wh(at|o|ich)|$)", triplet_set[i][1][j], re.I) is None:
    #     if cmp_str in a_cmp_list:
    #         where_line_j = where_line_j + a_where_list[a_cmp_list.index(cmp_str)]
    #         a_cnt = a_cnt_list[a_cmp_list.index(cmp_str)]
    #     else:
    #         a_cmp_list.append(cmp_str)
    #         a_cnt_list.append(a_cnt)
    #         if neg[i] is not None:
    #             where_phrase = " AND none(x" + str(a_cnt) + " in nodes(p" + str(t) + \
    #                            ") WHERE x" + str(a_cnt) + "." + a_property_type[t] + \
    #                            "=~'(?i)" + triplet_set[i][1][j] + "')"
    #         else:
    #             where_phrase = " AND a" + str(a_cnt) + "." + a_property_type[t] + \
    #                            "=~'(?i)" + triplet_set[i][1][j] + "'"
    #             if triplet_set[i][0][j] == "movie":
    #                 where_phrase = where_phrase + " AND toINT(a" + str(a_cnt) + ".numVotes)>" + str(movie_thres)
    #         a_where_list.append(where_phrase)
    #         where_line_j = where_line_j + where_phrase
    # # 是疑问词，设置return语句
    # elif re.match("^(wh(at|o|ich))", triplet_set[i][1][j], re.I):
    #     if cmp_str not in a_cmp_list:
    #         a_cnt_list.append(a_cnt)
    #         a_cmp_list.append(cmp_str)
    #         return_word = return_word + ",a" + str(a_cnt) + "." + a_property_type[t]
    #         return_cnt = return_cnt + 1
    #     else:
    #         a_cnt = a_cnt_list[a_cmp_list.index(cmp_str)]
    #     if triplet_set[i][0][j] == "movie":
    #         where_line_j = where_line_j + " AND toINT(a" + str(a_cnt) + ".numVotes)>" + str(movie_thres)
    # # tail
    # match_cmp_str = cmp_str
    # cmp_str = triplet_set[i][2][j] + b_property_type[t] + triplet_set[i][3][j]
    # b_cnt = t
    # # 不是疑问词或空，设置where语句
    # if re.match("^(wh(at|o|ich)|$)", triplet_set[i][3][j], re.I) is None:
    #     if cmp_str in b_cmp_list:
    #         where_line_j = where_line_j + b_where_list[b_cmp_list.index(cmp_str)]
    #         b_cnt = b_cnt_list[b_cmp_list.index(cmp_str)]
    #     else:
    #         b_cnt_list.append(b_cnt)
    #         b_cmp_list.append(cmp_str)
    #         if neg[i] is not None:
    #             where_phrase = " AND none(y" + str(b_cnt) + " in nodes(p" + str(t) + \
    #                            ") WHERE y" + str(b_cnt) + "." + b_property_type[t] + \
    #                            "=~'(?i)" + triplet_set[i][3][j] + "') "
    #         else:
    #             where_phrase = " AND b" + str(b_cnt) + "." + b_property_type[t] + \
    #                            "=~'(?i)" + triplet_set[i][3][j] + "' "
    #             if triplet_set[i][2][j] == "movie":
    #                 where_phrase = where_phrase + " AND toINT(b" + str(b_cnt) + ".numVotes)>" + str(movie_thres)
    #         b_where_list.append(where_phrase)
    #         where_line_j = where_line_j + where_phrase
    # # 是疑问词，设置return语句
    # elif re.match("^(wh(at|o|ich))", triplet_set[i][3][j], re.I):
    #     if cmp_str not in b_cmp_list:
    #         b_cnt_list.append(b_cnt)
    #         b_cmp_list.append(cmp_str)
    #         return_word = return_word + ",b" + str(b_cnt) + "." + b_property_type[t]
    #         return_cnt = return_cnt + 1
    #     else:
    #         b_cnt = b_cnt_list[b_cmp_list.index(cmp_str)]
    #     if triplet_set[i][2][j] == "movie":
    #         where_line_j = where_line_j + " AND toINT(b" + str(b_cnt) + ".numVotes)>" + str(movie_thres)
    # match_cmp_str = match_cmp_str + cmp_str
