# -*- coding:utf-8 -*-
"""
    实体、实体关系定义，问题，数据库
"""
import json
import platform
from py2neo import Graph
import requests
import pickle

# 定制换行符
sys_str = platform.system()
if sys_str == "Windows":
    line_break = "\n"
elif sys_str == "Linux":
    line_break = "\r\n"
else:
    print("Other System tasks")

#属性名映射词表
re_att_dict = json.load(open("replace_dicts/re_att_dict.json", encoding='utf-8'))

#翻译替换词表
replace_dict = json.load(open("replace_dicts/replace_dict.json", encoding='utf-8'))

#关系词预翻译表
trans_dict = json.load(open("replace_dicts/trans_dict.json", encoding='utf-8'))
trans_list = []
for values in trans_dict.keys():
    trans_list.append(values)

# 实体预处理表
person1_list = []
for person in open("entity_lists/person_pre.txt", encoding='utf-8').readlines():
    person = person.strip(line_break)
    person1_list.append(person)
# pz_dict = pickle.load(open("Chinese2English.pkl",'rb'))
# person1_list = list(pz_dict.values())
company1_list = []
for company in open("entity_lists/companies_pre.txt", encoding='utf-8').readlines():
    company = company.strip(line_break)
    company1_list.append(company)

eentity_dict = {"person": person1_list,
                "companies": company1_list
               }

# person2_list = []
# for person in open("personz_pre.txt", encoding='utf-8').readlines():
#     person = person.strip(line_break)
#     person2_list.append(person)
pz_dict = pickle.load(open("entity_lists/Chinese2English.pkl",'rb'))
person2_list = list(pz_dict.keys())

company2_list = []
for company in open("entity_lists/companiesz_pre.txt", encoding='utf-8').readlines():
    company = company.strip(line_break)
    company2_list.append(company)

zentity_dict = {"person": person2_list,
                "companies": company2_list
               }


# 电影实体预处理表
m_dict = pickle.load(open("entity_lists/movie_Zn2En.pkl",'rb'))
movie1_list = list(m_dict.values())
ementity_dict = {"movie": movie1_list}
movie2_list = list(m_dict.keys())
zmentity_dict = {"movie": movie2_list}


# 实体列表读取
movie_list = []
for movie in open("entity_lists/movie.txt").readlines():
    movie = movie.strip(line_break)
    movie_list.append(movie)
person_list = []
for person in open("entity_lists/person.txt", encoding='utf-8').readlines():
    person = person.strip(line_break)
    person_list.append(person)
company_list = []
for company in open("entity_lists/companies.txt", encoding='utf-8').readlines():
    company = company.strip(line_break)
    company_list.append(company)

entity_dict = {"movie": movie_list,
               "person": person_list,
               "REQU": ['relation', 'relationship'],
            #    "companies": ['what company', 'what companies'],
               "companies": company_list,
               "prop": ["name", "score", "rate","rating","Douban rating","average rating","average rate","IMDB rate","IMDB rating","cast","trivia",
                        "runtime","running time","length", "release time", "release date","color","colored","pname","profession","height",
                                "birthday","deathday","nickname","wife","husband","trade mark","portrayal","interview","article"],
               "event": ["award", "awards", "reward", "rewards", "event"]
            #    "QUESTION": ['which', 'who', 'what'],
               }

special_type = ["REQU"]

# 子图数据库连接
print("----connecting to local database----")
# graph_local = Graph(
#     "http://localhost:7474",
#     username="neo4j",
#     password="180306"
# )
try:
    ## 使用本地ip
    requests.get("http://" + "192.168.1.5" + ":8201", timeout=3.)
    print("local connection")
    url_local = "http://" + "192.168.1.5" + ":8201"
    # url = "http://" + "910.mivc.top" + ":17474/db/data/transaction/commit"
    url = "http://" + "localhost" + ':20000/base_services/neo4j?query='
except:
    ## 使用远程ip
    print("remote connetion")
    # url_local = "http://10.208.40.3:7474"
    url_local = "bolt://910.mivc.top:18202"
    # url = "http://localhost:7474/db/data/transaction/commit"
    # url = "http://localhost:8005/neo4j?query="
    url = "http://910.mivc.top:20000/base_services/neo4j?query="

graph_local = Graph(
    url_local,
    user="neo4j",
    password="1234"
)
print("local database connected")
# 远程数据库连接
# print("----connecting to remote database----")
# ip = "http://" + "910.mivc.top" + ":17474"
#
# url = "http://localhost:7474/db/data/transaction/commit"
login = "neo4j:123456"

val_dict = {
    'color': ['colored', 'color', 'black and white'],
    'characters': ['the neighbor', 'Reed'],
    'keywords': ['isolation']
 }

entity_query_dict = {
    'movie.primaryTitle': 1,
    'movie.Chinese_title': 1,
    'movie.rating': 1,
    'movie.averageRating': 1,
    'movie.numVotes': 1,
    'movie.casts': 1,
    'movie.runtimeMinutes': 1,
    'person.primaryName': 1,
    'person.Chinese_name': 1,
    'person.birthYear': 1,
    'person.deadYear': 1,
    'person.primaryProfession': 1,
    'companies.name': 1,
    'review.rating': 1,
    'review.text': 1,
    'event.name': 1,
    'event.year': 1,
    'news.content': 1,
    'person.characters': 2,
    'event.award_name': 2,
    'companies.award_name': 2,  # ?
    'movie.episodeNumber': 2,
    'movie.seasonNumber': 2,
    'movie.release_date': 3,
    'movie.keywords': 3,
    'movie.Color': 4,  # 未完
    'person.Height': 4,
    'person.Born': 4,
    'person.Died': 4,
    'person.Nicknames': 4,
    'person.trivia': 5,  # 未完
    'person.trade_mark': 5,
    'person.interviews': 6
}

property_entity_name = {
    'release_date': "release",
    'keywords': 'keywords',
    'film length': 'technicals',
    'Color': 'technicals',
    'runtime': 'technicals',
    'Height': 'nms_bio',
    'Born': 'nms_bio',
    'Died': 'nms_bio',
    'Nicknames': 'nms_bio',
    'trivia': 'nms_bio',
    'spouse': 'nms_bio',
    'trade_mark': 'nms_bio',
    'portrayals': 'nms_publicity',
    'interviews': 'nms_publicity',
    'articles': 'nms_publicity',
}


def relation_dict_query(head, tail):
    """
    在判断问句中的实体类型后搜索备选relation dict和remodel_dict
    :param entity_list: entity label list，eg：['movie', 'person']
    :return:
    remodel_dict = ["<p> act <m>", "<p> direct <m>", "<p> write <m>"]
    entity_relation_dict = {"relate": ["act", "direct", "write"]}
    """
    remodel_dict = []
    val = []
    
    cypher = "MATCH (a:" + head + ")-[r]->(b:" + tail + ")" + line_break + "RETURN DISTINCT type(r)"
    res = graph_local.run(cypher).data()
    for r in res:
        remodel_dict.append("<" + head[0] + "> " + r["type(r)"] + " <" + tail[0] + ">")
        val.append(r["type(r)"])
    entity_relation_dict = {"relate": val}
    return remodel_dict, entity_relation_dict
