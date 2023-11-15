# -*- coding:utf-8 -*-
"""
    主调模块
"""
from flask import Flask, request, jsonify
import json
from flask_cors import CORS, cross_origin
from infer_main import answer_inference, addition_info_query
import time
import re

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": "*"}})

add_who = set(['actor', 'director', 'photographer', 'writer', 'editor', 'composer', 'designer'])
add_what = set(['movie', 'movies', 'award', 'awards', 'company', 'companies'])
delete_table = ['what ', 'What ', 'is ', 'are ', 'who ', 'Who ', 'did ', 'do ', 'does ', '?']

@app.route('/qa', methods=['GET', 'POST'])
def qa():
    t1 = time.time()
    print(request)
    if request.method == 'GET':
        question = request.args.get("question")
        print(question)
        try:
            answer, cypher = answer_inference(question)
        except:
            answer, cypher = answer_inference(question)

        if len(answer) == 0:
            print('answer cannot be found')
            return app.response_class(
            response=json.dumps({
                "answer": ["answer cannot be found"],
                "cypher": cypher}),
            mimetype='application/json'
        )
        else:
            # q_return = question
            # for i in delete_table:
            #     q_return = q_return.replace(i, '')
            # q_return += ' are'

            add_visual = addition_info_query(cypher)
            for v in answer:
                print(v)
                # q_return = q_return + ' ' + v['text'] + ','
            print(time.time() - t1)
            return app.response_class(
                response=json.dumps({
                    # "q_return": q_return,
                    "answer": answer,
                    "cypher": cypher,
                    "addition": add_visual}),
                mimetype='application/json'
            )
        # except:
        #     print("ERROR, TRY AGAIN")


    return '{}'

# @app.route('/retrieve', methods=['GET', 'POST'])
# def retrieve():
#     print(request)
#     if request.method == 'GET':
#         query = request.args.get("question")
#         target = set(query.split(' '))
#         if len(add_who & target) > 0:
#             question = 'Who ' + query
#         else:
#             question = 'What ' + query
#         print(question)
#         try:
#             answer, cypher = answer_inference(question)

#             if len(answer) == 0:
#                 print('answer cannot be found')
#                 return app.response_class(
#                 response=json.dumps({
#                     "answer": ["answer cannot be found"],
#                     "cypher": cypher}),
#                 mimetype='application/json'
#             )
#             else:
#                 add_visual = addition_info_query(cypher)
#                 answer_list = []
#                 for v in answer.values():
#                     for i in v:
#                         answer_list.append(i)
#                 print(answer_list)
#                 return app.response_class(
#                     response=json.dumps({
#                         "answer": answer_list,
#                         "cypher": cypher,
#                         "addition": add_visual}),
#                     mimetype='application/json'
#                 )
#         except:
#             print("ERROR, TRY AGAIN")


#     return '{}'


app.run(host='0.0.0.0', port=8203, debug=True)
