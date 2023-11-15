# Question to Triplet 4月13日更新

允许电影不加双引号

## 更新的文件
Q2TReadme.md : 本文档

movie_Zn2En.pkl : 电影中英文名表

questionv3.txt : 本次测试问题列表

-----------------------------可能需要解决冲突的文档-------------------------------

information.py : 增加中英文电影实体列表zmentity_dict、ementity_dict。

infer_main.py : 增加中英文电影实体提取的spacy模型zmnlp、zmnlp，标识字典共用mdict_keys，调用QueryPretreat时加入参数。

----------------------以下更新与其他模块不产生冲突，可直接覆盖----------------------

Chinese2English.pkl,person_pre.txt : 新人名表

QAQ.py : 初始化时加入中英文电影提取模型；
        修改getmovie()函数，如果经双引号提取后没有提取到电影，则通过spacy提取，保持格式和路径均没变。

## 结果示例
```
原句 : What is the average rate of Titanic?
改写 : What is the average rate of M1 ?
拆分 : {'logic': [], 
        'question_set': [What is the average rate of M1 ?], 
        'neg_label': [None]，
        'proplist': [[['M1', 'average rate']]]}
实体三元组 : [(['movie'], ['Titanic'])]
属性三元组 : [[['Titanic', 'averageRating']]]
```
```
原句 : 肖申克的救赎是什么颜色的？
改写 : What color is M1?
拆分 : {'logic': [], 
        'question_set': [What color is M1?], 
        'neg_label': [None]，
        'proplist': [[['M1', 'color']]]}
实体三元组 : [(['movie'], ['肖申克的救赎'])]
属性三元组 : [[['肖申克的救赎', 'Color']]]
```


# Question to Triplet 3月4日更新

增加全句属性解析

## 更新的文件
Q2TReadme3_4.md : 本文档

-----------------------------可能需要解决冲突的文档-------------------------------

information.py : 实体列表entity_dict中增加形容词实体列表'prop'。

infer_main.py : addhead()函数删除了复杂的头部处理，只有what's和who需要拆；
                (Line 68~82)改写了单句列表和属性列表的格式，划分回传时"question_set"只含单句、
                "proplist"含属性二元组且列表最后一项为疑问点（特殊情况值为'No link'/'No what'/'REQU'）。

----------------------以下更新与其他模块不产生冲突，可直接覆盖----------------------

questionv2.txt,questionv1.txt : 本次测试问题列表(v1侧重已有的复杂句式和扩展 & v2侧重覆盖所有属性的提问)。

QAQ.py : 修改atttodict()函数，规则映射属性二元组。

Qsplit.py : splitamod()、findprop()、cut()函数提取每个子句中的属性词组，将疑问点放置在列表最后一项；
            self.__qsy中只放置单句列表，增加self.__a作为属性列表。

QperML.py : 在可提问的实体空间中减去属性实体'prop'

## 接口
总输入：
```
q(问题)
```
过程函数：
```
q_pre.forward_pre() : 输入问题，返回语言、预处理后的问句、电影字典、电影数、其他实体字典、其他实体数
retrive2qa()、addhead() : 输入问句，输出规定格式的改写
q_split.forward_split() : 输入问句，输出拆分子句情况，logic表示逻辑结构，neg_label表示每个句子的肯定/否定情况，
                          question_set表示子句，proplist表示每个子句里的属性二元组列表。
parse_blk.parse_keyword() : 输入单句，输出模板匹配的三元组结果
q_pre.backname() : 输入三元组，输出代换原词的三元组
q_pre.atttodict() : 输入单句的属性列表，输出属性二元组表
```
总输出：
```
lang：语种
query_splited["logic"]：拆分子句的逻辑结构
query_splited["neg_label"]：每个子句的肯定/否定标记
triplet_set：每个子句内的三元组关系,问关系的句子仍然会特判处理（以'REQU'表示），同时也支持全句只有一个单实体
attlist_set：每个子句中实体附带的属性，以[实体,属性类别]展示，列表最后一项为疑问点（特殊情况值为'No link'/'No what'/'REQU'）。
```

## 结果示例
```
原句 : What is the average rate of "Titanic"?
改写 : What is the average rate of M1 ?
拆分 : {'logic': [], 
        'question_set': [What is the average rate of M1 ?], 
        'neg_label': [None]，
        'proplist': [[['M1', 'average rate']]]}
实体三元组 : [(['movie'], ['Titanic'])]
属性三元组 : [[['Titanic', 'averageRating']]]
```
```
原句 : "肖申克的救赎"是什么颜色的？
改写 : What color is M1?
拆分 : {'logic': [], 
        'question_set': [What color is M1?], 
        'neg_label': [None]，
        'proplist': [[['M1', 'color']]]}
实体三元组 : [(['movie'], ['肖申克的救赎'])]
属性三元组 : [[['肖申克的救赎', 'Color']]]
```


# Question to Triplet 2月8日更新

增加对属性提问功能

## 更新的文件
Q2TReadme.md : 本文档

questionv2.txt,questionv1.txt : 本次更新的测试问题列表(专门测属性提问的&带有复杂句式和句内属性的)

re_att_dict.json : 属性名映射表

-----------------------------可能需要解决冲突的文档-------------------------------

companies_pre.txt,companies.txt,movie.txt,person.txt : 实体列表更新，不需要专门找出what开头的词组作为实体

information.py : 实体列表entity_dict中的"event"实体更新，也不需要what开头的词组实体；
                 增加属性预设词表val_dict，结构为{属性类别：属性值列表}；
                 增加属性名映射词表re_att_dict。

infer_main.py : 增加了addhead()函数，预处理问句后对问句头改写，使之变成"what is the 属性类型 of 实体"的形式；
                增加attlist_set列表变量，处理实体属性三元组(Line 73~86)。

----------------------以下更新与其他模块不产生冲突，可直接覆盖----------------------

QAQ.py : 增加了atttodict()函数，输入实体属性抽取列表和电影及其他实体映射表，输出规则的属性三元组；
         在backname()函数中增加了单实体情况的处理。

Qsplit.py : splitamod()函数提取每个子句中的属性词组

QperML.py : parse_keyword()增加了单实体的返回情况

## 接口
总输入：
```
q(问题)
```
过程函数：
```
q_pre.forward_pre() : 输入问题，返回语言、预处理后的问句、电影字典、电影数、其他实体字典、其他实体数
retrive2qa()、addhead() : 输入问句，输出规定格式的改写
q_split.forward_split() : 输入问句，输出拆分子句情况，logic表示逻辑结构，neg_label表示每个句子的肯定/否定情况，
                          question_set表示子句，每个子句列表最后一项是不含属性的单句，前几项都是提到的属性词组。
parse_blk.parse_keyword() : 输入单句，输出模板匹配的三元组结果
q_pre.backname() : 输入三元组，输出代换原词的三元组
q_pre.atttodict() : 输入单句的属性词组表，输出属性三元组表
```
总输出：
```
lang：语种
query_splited["logic"]：拆分子句的逻辑结构
query_splited["neg_label"]：每个子句的肯定/否定标记
triplet_set：每个子句内的三元组关系,问关系的句子仍然会特判处理（以'REQU'表示），同时也支持全句只有一个单实体
attlist_set：每个子句中实体附带的属性，以[实体,属性类别,属性值]展示，没有提到属性的实体不出现在列表中，
             提取到多个属性的实体将出现多次，会有一个属性三元组的属性值是what，即问题的目标。
```

## 结果示例
```
原句 : What is the average rate of "Titanic"?
改写 : What is the average rate of M1 ?
拆分 : {'logic': [], 
        'question_set': [[what/average rate/M1, M1 ?]], 
        'neg_label': [None]}
实体三元组 : [(['movie'], ['Titanic'])]
属性三元组 : [[['Titanic', 'averageRating', 'what']]]
```
```
原句 : "肖申克的救赎"是什么颜色的？
改写 : what is the color of M1?
拆分 : {'logic': [], 
        'question_set': [[what/color/M1, M1 ?]], 
        'neg_label': [None]}
实体三元组 : [(['movie'], ['肖申克的救赎'])]
属性三元组 : [[['肖申克的救赎', 'Color', 'what']]]
```