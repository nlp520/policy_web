#encoding:utf-8
from classify.classify import BertClassify, CnnClassify
from classify.keyword_classify import BertKeywordClassify, CnnKeywordClassify
from parser.syntactic_parsing import HanlpParser
from utils.utils import sentence_tokenize, convert_date
import time
class Association():
    def __init__(self):
        self.bertClassify = CnnClassify()
        self.bertKeywordClassify = CnnKeywordClassify()
        self.hanlpParser = HanlpParser()
        self.batch_size = 30

    def analyzeAll(self, policy1, policy2):
        '''
        :param policy1:{
                            "name":"",#政策名
                            "org":"",#发布机构
                            "date":"",#发布日期
                            "province":"",#省份
                            "category":"",#政策类别
                            "context":""#政策内容
                        }
        :param policy2:
        :return:
        results = {
                "result":"对于政策A来说，政策B是起到理论指导作用",
                "policy1":{
                    "1":["句子", "理论指导"],
                    "2":["句子", "理论指导"],

                 },#第一个政策每句话的分析
                "policy2":{
                    "1":["句子", "理论指导"],
                    "2":["句子", "理论指导"],
                 }#第二个政策每句话的分析
            }
        '''
        #添加判断逻辑， 相同领域的政策，不同级别的政策，具有可比性
        #判断政策上下级：
        field_label = self.judge_field(policy1.get("category", ""), policy2.get("category", ""))
        if not field_label:
            result = "两个政策属于不同领域，无法进行比较。"
            return {
                "result": result
            }

        level_label = self.judge_level(policy1, policy2)
        if isinstance(level_label, str):
            result = "两个政策不存在上下级关系，无法进行比较。"
            return {
                "result": result
            }


        policy1_lis = self.analyzePolicy(policy1.get("context", ""))
        policy2_lis = self.analyzePolicy(policy2.get("context", ""))

        dic_policy1 = self.get_relation(policy1_lis)
        dic_policy2 = self.get_relation(policy2_lis)

        return {
            "results": "政策A对政策B是理论指导作用",
            "policy1": dic_policy1,
            "policy2": dic_policy2
        }

    def get_relation(self, policy_lis):
        dic = {}
        index = 1
        for key in policy_lis:
            dic[index] = [key[0], key[1]]
            index += 1
        return dic

    def judge_field(self, policy1_field, policy2_field):
        '''
        判断两个政策的领域是否相同
        :param policy1_field:
        :param policy2_field:
        :return:
        '''
        if policy1_field == policy2_field:
            return True
        else:
            return False
    def judge_time(self, first_time, second_time):
        '''
        判断哪个时间在前，返回False， 第二个时间要近，返回True,第一个时间近
        :param first_time:
        :param second_time:
        :return:
        '''
        first_time = convert_date(first_time)
        second_time = convert_date(second_time)
        return first_time > second_time


    def judge_level(self, policy1, policy2):
        '''
        返回False, 政策1优先级高，
        :param policy1:
        :param policy2:
        :return:
        '''
        #判断是否是相同级别
        org1 = policy1.get("org")
        org2 = policy2.get("org")

        date1 = policy1.get("date")
        date2 = policy2.get("date")

        province1 = policy1.get("province")
        province2 = policy2.get("province")

        if org1 == "国务院" and org2 == "国务院":
            return self.judge_time(date1, date2)
        elif org1 == "国务院" and org2 != "国务院":
            return False
        elif org1 != "国务院" and org2 == "国务院":
            return True
        else:
            #相同机构，时间发布早的优先级高
            if org1 == org2:
                return self.judge_time(date1, date2)
            else:
                if not province1 or not province2:
                    return "无法比较"
                else:
                    if province1 == province2:
                        if "人民政府" in org1 and "人民政府" not in org2:
                            return False
                        elif "人民政府" not in org1 and "人民政府" in org2:
                            return True
                        else:
                            return self.judge_time(date1, date2)
                    else:
                        return "无法比较"

    def clear_sentences(self, sentences):
        new_sentences = []
        for sentence in sentences:
            sentence = sentence.strip().replace("\u3000", "")
            if not sentence:
                continue
            new_sentences.append(sentence)
        return new_sentences

    def analyzePolicy(self, policy, use_classify=True):
        '''
        政策解析
        :param policy:
        :return:
        '''
        sentences = sentence_tokenize(policy)
        new_sentences = self.clear_sentences(sentences)
        policy_lis = []
        for i in range(0, len(new_sentences), self.batch_size):
            sentences = new_sentences[i: min(len(new_sentences), i+self.batch_size)]
            if use_classify:
                classify_label = self.bertClassify.predicts(sentences)
                keyword_label = self.bertKeywordClassify.predicts(sentences)
                for j in range(len(sentences)):
                    policy_lis.append([sentences[j], classify_label[j], keyword_label[j]])
            else:
                keyword_label = self.bertKeywordClassify.predict(sentences)
                for j in range(len(sentences)):
                    policy_lis.append([sentences[j], keyword_label[j]])
        return policy_lis

    def getKeywordDict(self, policy_lis, use_classify=True):
        '''
        获取具有相同关键词的字典集合
        :param policy_lis:
        :param use_classify:
        :return:
        '''
        keywordDict = {}
        if use_classify:
            index = 2
        else:
            index = 1
        for lis in policy_lis:
            if lis[index] not in keywordDict:
                keywordDict[lis[index]] = [lis[0]]
            else:
                keywordDict[lis[index]].append(lis[0])
        return keywordDict

    #分析单个句子
    def assoSingleAnalyze(self, policy1, policy2, sentence, id):
        results = []
        if id == 1:
            context = policy2.get("context")
            sentences = sentence_tokenize(context)
            sentences = self.clear_sentences(sentences)
            for sent in sentences:
                if self.cal_similar(sentence, sent):
                    results.append([sent, "相关"])
                else:
                    results.append([sent, "不相关"])
        else:
            context = policy1.get("context")
            sentences = sentence_tokenize(context)
            for sent in sentences:
                if self.cal_similar(sentence, sent):
                    results.append([sent, "相关"])
                else:
                    results.append([sent, "不相关"])

        return {
            "policy": results
        }

    def cal_similar(self, sentence1, sentence2):
        import random
        if random.random() > 0.7:
            return True
        else:
            return False





