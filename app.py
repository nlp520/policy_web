from flask import Flask
from flask import render_template, redirect, url_for
from flask import request, session, json
from flask import jsonify
from keywords.keywordExtract import getKeywords
from parser.analysis_doc import parser_doc, basicInfoExtract
from conflict.conflict_detect import Conflict
from retrieval.infoRetrieval import find_policy
from association.asso_analyze import Association

app = Flask(__name__)
app.config["SECRET_KEY"] = "123456"

conflict = Conflict()
asso = Association()

@app.route('/')
def hello_world():
    return '欢迎来到政策关联分析系统算法后台！！！'

@app.route('/dataProcess', methods=["POST", "GET"])
def dataProcess():
    '''
    对输入到数据库中的政策进行数据处理，进行信息提取操作。
    :return:
    '''
    if request.method == 'POST':
        datax = request.form.get('text',"")
        if datax:
            '''
            添加数据处理操作
            '''
            results = basicInfoExtract(datax)
            return jsonify({"error_code":0, "reason":"", "data":results})
        else:
            return jsonify({"error_code": 1, "reason": "没有输入政策数据", "data": ""})
    else:
        return jsonify({"error_code":2, "reason":"请求方式错误，应使用post请求", "data":""})


@app.route("/keywords", methods=["POST","GET"])
def keywords():
    '''
    关键词提取
    :return:
    '''
    if request.method == 'POST':
        datax = request.form.get('text',"")
        number = int(request.form.get('number', 3))
        if datax:
            '''
            添加数据处理操作
            '''
            keyword = getKeywords(datax, num= number)
            results = {
                "keywords":keyword,#关键词
            }
            return jsonify({"error_code":0, "reason":"", "data":results})
        else:
            return jsonify({"error_code": 1, "reason": "没有输入政策数据", "data": ""})
    else:
        return jsonify({"error_code":2, "reason":"请求方式错误，应使用post请求", "data":""})


@app.route("/dataAnalyze", methods=["POST","GET"])
def dataAnalyze():
    '''
    政策文本结构化解析
    :return:
    '''
    if request.method == 'POST':
        datax = request.form.get('text',"")
        name = request.form.get('name', "")
        if datax:
            '''
            添加数据处理操作
            '''
            results = parser_doc(datax)
            return jsonify({"error_code":0, "reason":"", "data":results})
        else:
            return jsonify({"error_code": 1, "reason": "没有输入政策数据", "data": ""})
    else:
        return jsonify({"error_code":2, "reason":"请求方式错误，应使用post请求", "data":""})


@app.route("/conflictDetection", methods=["POST", "GET"])
def conflictDetection():
    '''
    政策文本冲突检测
    :return:
    '''
    if request.method == 'POST':
        # datax = request.get_data()
        datax = request.form.get('policy',"")
        test_policy = request.form.get('test_policy', "")
        if datax and test_policy:
            '''
            添加数据处理操作
            '''
            datax = json.loads(datax)
            results = conflict.conflict(datax, target_sent=test_policy)
            # results = {
            #     "result":"存在时间类型的冲突",
            #     "sentence":"到2020年，实现全面建设中国物联网体系平台。"
            # }
            return jsonify({"error_code":0, "reason":"", "data":results})
        else:
            return jsonify({"error_code": 1, "reason": "没有输入政策数据或者是待检测文本", "data": ""})
    else:
        return jsonify({"error_code":2, "reason":"请求方式错误，应使用post请求", "data":""})


@app.route("/assoAnalyze", methods=["POST", "GET"])
def assoAnalyze():
    '''
    两个政策关联分析
    :return:
    '''
    if request.method == 'POST':
        policy1 = request.form.get('policy1',"")
        policy2 = request.form.get('policy2', "")
        if policy1 and policy2:
            '''
            添加数据处理操作
            '''
            policy1 = json.loads(policy1)
            policy2 = json.loads(policy2)
            results = asso.analyzeAll(policy1, policy2)
            # results = {
            #     "result":"对于政策A来说，政策B是起到理论指导作用",
            #     "policy1":{
            #         "1":["句子", "理论指导"],
            #         "2":["句子", "理论指导"],
            #
            #      },#第一个政策每句话的分析
            #     "policy2":{
            #         "1":["句子", "理论指导"],
            #         "2":["句子", "理论指导"],
            #      }#第二个政策每句话的分析
            # }
            return jsonify({"error_code":0, "reason":"", "data": results})
        else:
            return jsonify({"error_code": 1, "reason": "没有输入政策数据", "data": ""})
    else:
        return jsonify({"error_code":2, "reason":"请求方式错误，应使用post请求", "data":""})


@app.route("/assoSingleAnalyze", methods=["POST", "GET"])
def assoSingleAnalyze():
    '''
    两个政策关联分析
    :return:
    '''
    if request.method == 'POST':
        policy1 = request.form.get('policy1',"")
        policy2 = request.form.get('policy2', "")
        sentence = request.form.get('sentence', "")
        id = request.form.get('id', None)
        if policy1 and policy2 and sentence and id is not None:
            id = int(id)
            '''
            添加数据处理操作
            '''
            policy1 = json.loads(policy1)
            policy2 = json.loads(policy2)
            results = asso.assoSingleAnalyze(policy1, policy2, sentence, id)
            # results = {
            #     "policy":{
            #         "1":["句子", "相似"],
            #         "2":["句子", "不相似"],
            #     }
            # }
            return jsonify({"error_code":0, "reason":"", "data":results})
        else:
            return jsonify({"error_code": 1, "reason": "没有输入政策数据或者输入信息不完整", "data": ""})
    else:
        return jsonify({"error_code":2, "reason":"请求方式错误，应使用post请求", "data":""})



@app.route("/policyFind", methods=["POST", "GET"])
def policyFind():
    '''
    政策查找
    :return:
    '''
    if request.method == 'POST':
        policy1 = request.form.get('policy',"")
        policy_lis = request.form.get('policy_lis', "")
        number = int(request.form.get('number', 10))

        if policy1 and policy_lis and number :
            '''
            添加数据处理操作
            '''
            print(policy_lis)
            if not isinstance(policy_lis, list):
                policy_lis = policy_lis.split("#")
            res = find_policy(policy1, policy_lis, int(number))
            print(res)
            results = {
                "result":"#".join(res)#"大数据#互联网#人工智能#物联网"
            }
            return jsonify({"error_code":0, "reason":"", "data":results})
        else:
            return jsonify({"error_code": 1, "reason": "没有输入政策数据或者输入信息不完整", "data": ""})
    else:
        return jsonify({"error_code":2, "reason":"请求方式错误，应使用post请求", "data":""})


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port = 5000, debug=True)
