#encoding:utf-8
from BLEU.bleu import Bleu
from classify.classify import BertClassify, CnnClassify
from classify.keyword_classify import BertKeywordClassify, CnnKeywordClassify
from parser.syntactic_parsing import HanlpParser
from utils.utils import sentence_tokenize, convert_date
from similar.Doc2vec import DocVec
import time
import jieba
class Association():
    def __init__(self):
        self.bertClassify = CnnClassify()
        self.bertKeywordClassify = CnnKeywordClassify()
        self.hanlpParser = HanlpParser()
        self.doc2vec = DocVec()
        self.batch_size = 30
        self.bleu = Bleu(1)

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
            result = "政策1输属于" + policy1.get("category", "") + "，政策2属于"+policy2.get("category", "")+",两个政策属于不同领域，无法进行比较。"
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

        results, policy1_similar_dic, policy2_similar_dic = self.analyze_realtion(policy1_lis, policy2_lis, level_label)

        return {
            "result": results,
            "policy1": dic_policy1,
            "policy2": dic_policy2,
            'policy1_similar_dic': policy1_similar_dic,
            'policy2_similar_dic': policy2_similar_dic
        }

    def analyze_realtion(self, policy1_lis, policy2_lis, level_label):
        '''
        两个政策文本的关联分析
        :param policy1_lis:
        :param policy2_lis:
        :param level_label:
        :return:
        '''
        policy1_dic = {}
        policy2_dic = {}
        index = 1
        for lis in policy1_lis:
            if lis[2] not in policy1_dic:
                policy1_dic[lis[2]] = [[lis[0], lis[1], index]]
            else:
                policy1_dic[lis[2]].append([lis[0], lis[1], index])
            index += 1
        index = 1
        for lis in policy2_lis:
            if lis[2] not in policy2_dic:
                policy2_dic[lis[2]] = [[lis[0], lis[1], index]]
            else:
                policy2_dic[lis[2]].append([lis[0], lis[1], index])
            index += 1
        print(policy2_dic.keys())
        #计算相同关键词的句子的相似度
        relation1_dic = {}
        relation2_dic = {}
        number = 0
        start_time = time.time()

        for key, value in policy1_dic.items():
            if key != "[UNK]" and key in policy2_dic:
                print(len(value) * len(policy2_dic[key]))

        # 统计相似的句子
        policy1_similar_dic = {}
        policy2_similar_dic = {}

        for key, value1_lis in policy1_dic.items():
            if key != "[UNK]" and key in policy2_dic:
                value2_lis = policy2_dic[key]
                for sent1_lis in value1_lis:
                    for sent2_lis in value2_lis:
                        #计算相似度
                        number += 1
                        if self.cal_similar(sent1_lis[0], sent2_lis[0]):
                            if sent1_lis[1] not in relation1_dic:
                                relation1_dic[sent1_lis[1]] = 1
                            else:
                                relation1_dic[sent1_lis[1]] += 1
                            if sent2_lis[1] not in relation2_dic:
                                relation2_dic[sent2_lis[1]] = 1
                            else:
                                relation2_dic[sent2_lis[1]] += 1

                            if sent1_lis[2] not in policy1_similar_dic:
                                policy1_similar_dic[sent1_lis[2]] = [sent2_lis[2]]
                            else:
                                policy1_similar_dic[sent1_lis[2]].append(sent2_lis[2])

                            if sent2_lis[2] not in policy2_similar_dic:
                                policy2_similar_dic[sent2_lis[2]] = [sent1_lis[2]]
                            else:
                                policy2_similar_dic[sent2_lis[2]].append(sent1_lis[2])

        end_time = time.time()
        print("耗时：", (end_time - start_time)/60)
        print("相似度计算次数：", number)
        if not level_label:
            results = "政策1是上级政策，政策2是下级政策，"
            relation1 = sorted(relation1_dic.items(), key=lambda x: x[1], reverse=True)
            relation2 = sorted(relation2_dic.items(), key=lambda x: x[1], reverse=True)
            result_relation1 = ""
            result_relation2 = ""
            for relation in relation1:
                if relation[0] == "[UNK]" or relation[0] == "体系培育" or relation[0] == "支撑服务":
                    continue
                result_relation1 = relation[0]
                break

            for relation in relation2:
                if relation[0] == "[UNK]" or relation[0] == "理论指导":
                    continue
                result_relation2 = relation[0]
                break
            results = results + "从整体上看，政策1对政策2起到" + result_relation1 +"的作用，政策2对政策1起到" + result_relation2 + "的作用。"
        else:
            results = "政策2是上级政策，政策1是下级政策，"
            relation1 = sorted(relation1_dic.items(), key=lambda x: x[1], reverse=True)
            relation2 = sorted(relation2_dic.items(), key=lambda x: x[1], reverse=True)
            result_relation1 = ""
            result_relation2 = ""
            for relation in relation1:
                if relation[0] == "" or relation[0] == "理论指导":
                    continue
                result_relation1 = relation[0]
                break

            for relation in relation2:
                if relation[0] == "" or relation[0] == "体系培育" or relation[0] == "支撑服务":
                    continue
                result_relation2 = relation[0]
                break
            results = results + "从整体上看，政策1对政策2起到" + result_relation1 + "的作用，政策2对政策1起到" + result_relation2 + "的作用。"
        return results, policy1_similar_dic, policy2_similar_dic

    def get_relation(self, policy_lis):
        '''
        返回政策的句子属性
        :param policy_lis:
        :return:
        '''
        dic = {}
        index = 1
        for key in policy_lis:
            dic[index] = [key[0].replace(" ", ""), key[1], key[2]]
            index += 1
        return dic

    def judge_field(self, policy1_field, policy2_field):
        '''
        判断两个政策的领域是否相同
        :param policy1_field:
        :param policy2_field:
        :return:
        '''
        if "#" in policy1_field:
            policy1_field = policy1_field.split("#")
        else:
            policy1_field = [policy1_field]
        if "#" in policy2_field:
            policy2_field = policy2_field.split("#")
        else:
            policy2_field = [policy2_field]
        for policy1 in policy1_field:
            for policy2 in policy2_field:
                if policy1 == policy2:
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
        if province1 == '中央' and province2 != '中央':
            return False
        elif province1 != '中央' and province2 == '中央':
            return True

        if org1 in ['国务院', '中央', '财政部'] and org2 in ['国务院', '中央', '财政部']:
            return self.judge_time(date1, date2)
        elif org1 in ['国务院', '中央', '财政部'] and org2 not in ['国务院', '中央', '财政部']:
            return False
        elif org1 not in ['国务院', '中央', '财政部'] and org2 in ['国务院', '中央', '财政部']:
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
        '''
        对句子集合中的句子进行清洗，去除前后空格
        :param sentences:
        :return:
        '''
        new_sentences = []
        for sentence in sentences:
            sentence = sentence.strip().replace("\u3000", "").replace(" ","").replace("&nbsp;","").strip()
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
                    policy_lis.append([" ".join(list(jieba.cut(sentences[j]))), classify_label[j], keyword_label[j]])
            else:
                keyword_label = self.bertKeywordClassify.predict(sentences)
                for j in range(len(sentences)):
                    policy_lis.append([" ".join(list(jieba.cut(sentences[j]))), keyword_label[j]])
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
        '''
        判断单个句子的相关性
        :param policy1:
        :param policy2:
        :param sentence:
        :param id:
        :return:
        '''
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
        # import random
        # if random.random() > 0.7:
        #     return True
        # else:
        #     return False
        # examples1 = self.hanlpParser.parser(sentence1)
        # examples2 = self.hanlpParser.parser(sentence2)
        # for example1 in examples1:
        #     for example2 in examples2:
        #         if example1["adj"] + example1["noun"] == example2["adj"] + example2["noun"]:
        #             return True
        # score = self.doc2vec.cal_similar(sentence1, sentence2)
        # if score >= 0.5:
        #     return True
        # return False
        self.bleu.add_inst(sentence1, sentence2)
        score = self.bleu.get_score()
        if score > 0.1:
            return True
        else:
            return False