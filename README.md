# QA系统

## Install
```
conda create -n qa_transformer python=3.6
conda activate qa_transformer
pip install -r requirements.txt
```

## Pretrained models
```shell
# en_core_web_sm：
pip --default-timeout=10000 install https://github.com.cnpmjs.org/explosion/spacy-models/releases/download/en_core_web_sm-2.3.0/en_core_web_sm-2.3.0.tar.gz

# transformer
# https://sbert.net/models/distilbert-base-nli-mean-tokens_part.zip
# 解压到~/.cache/torch/sentence_transformers/sbert 可能需要新建文件夹sbert.net_models_distilbert-base-nli-mean-tokens
# 如果能够翻墙运行程序会自动下载（～240M）

unzip distilbert-base-nli-mean-tokens.zip -d .cache/torch/sentence_transformers/sbert.net_models_distilbert-base-nli-mean-tokens
```

## Demo
```shell
python infer_main.py
```

## FLASK服务
```shell
python server.py
```
输入请求
```
requests.get('http://${910ip}:18203/qa?question=' + question).json()
requests.get('http://${910ip}:18203/retrieve?question=' + question).json()
```
返回数据结构为json文件
```
{
    "q_return: str， #自然语言形式的答案
    "answer": list, #答案列表list，每个元素为一个字典{'text':xxx, 'url': xxx}. 关系类问题url为None
    "cypher": json, #json文件（字典），用于可视化，所有三元组存放于"graph"键值
    "addition": list of json, #所有涉及电影的n个片花和n条评论（目前n=3）
}
```

## Related Works
```
sentence_transformers
https://github.com/UKPLab/sentence-transformers
```
spacy
