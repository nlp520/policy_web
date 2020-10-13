#coding:utf-8
#Team:BuaaNlp
#Author: Sui Guobin
#Date: 2019/12/17
#Tool: PyCharm
import os
from copy import copy
import re
from pyhanlp import *
from utils.utils import sentence_tokenize
from parser.syntactic_parsing import HanlpParser
from parser.analysis_doc import parser_doc_clear
from BLEU import Bleu
current_path = os.path.dirname(os.path.abspath(__file__))
'''
时间类型冲突
数值类型冲突
专有名词定义冲突
'''

class Conflict():
    def __init__(self):

        self.duty_lis = ['负责', "职责单位"]#职责名词
        self.noun_lis = ["是指", "定义为"]#专有名词
        self.pos_words = ["增加", "达到", "培育", "建设", "超过", "打造", "建成"]
        self.neg_words = ["减少", "缩减", '抑制', '减弱', "弱化"]
        pass

    def clear_punctuation(self, text):
        '''
        去除标点符号
        :param text:
        :return:
        '''
        punctuation = ["，", "。",":","：",",", "."]
        for pun in punctuation:
            text = text.replace(pun, "")
        return text

    def bleu_cal(self, sentence, target_sent):
        '''
        bleu值计算
        :param sentence:
        :param target_sent:
        :return:
        '''
        self.bleu = Bleu(1)
        self.bleu.add_inst(cand=sentence, ref=target_sent)
        score = self.bleu.get_score()
        return score

    def process_parser(self, word_lis):
        number = ""#记录数量
        number_ = ""#记录数量后面的修饰
        noun = ""#记录数量后面的名词
        verb = ""#记录前面的动词
        index = 0
        #获取数量
        for i in range(len(word_lis)):
            if word_lis[i][3] == "m":
                number = word_lis[i][1]
                index = i
                break
        if number:
            #获取数量后面的修饰
            if index <len(word_lis) and word_lis[index+1][3] == "q":
                number_ = word_lis[index+1][1]
            #获取数量修饰的名词
            flag = False
            start = None
            end = None
            for i in range(index + 1, len(word_lis)):
                if word_lis[i][1] == "以上":
                    continue
                if word_lis[i][3] not in ["q", "m"] and word_lis[i][7] in ["定中关系", "动宾关系"] and not flag:
                    flag = True
                if flag:
                    noun += word_lis[i][1]
                if word_lis[i][7] == "动宾关系":
                    flag = False
                    break
            verb_index = None
            for i in range(index):
                if word_lis[i][7] == "核心关系":
                    verb_index = i
                    verb = word_lis[i][1]
            # 说明右找没有发现动宾，说明在前面
            if (flag or not noun) and verb_index:
                noun = ""
                for i in range(verb_index):
                    noun += word_lis[i][1]

            return {
                    "verb":verb,
                    "number":number,
                    "number_":number_,
                    "noun":noun
                }
        else:
            return None

    def find_number_words(self, sentence=None):
        '''
        从句子片段中挑选还有数量
        :param sentence:
        :return:
        '''
        sentence = sentence.replace("，", "。")
        sentences = sentence_tokenize(sentence)
        number_lis = []
        for sent in sentences:
            parser_sentence = HanLP.parseDependency(sent)
            word_lis = []
            for word in parser_sentence.iterator():  # 通过dir()可以查看sentence的方法
                # print(word)
                word_lis.append(str(word).split())
            number_dic = self.process_parser(word_lis)
            if number_dic:
                number_lis.append(number_dic)
        return number_lis

    def conflict(self, datax, target_sent):
        '''
        冲突检测
        :param document:
        :param target_sent:
        :return:
        '''
        document = datax.get("context")
        print("input context:%s"%(document))
        similar_sentence, similar_paragraph = self.find_paragraph(document, target_sent)
        if similar_sentence == "不是政策文本格式，不能解析":
            return {
                "result": "不是政策文本格式，不能解析",
                "sentence": ""
            }
        print("similar_sentence:",similar_sentence)
        if not similar_sentence:
            return {
            "result": "不存在冲突，没有相似的句子",
            "sentence": ""
        }
        results = self.judge_conflict(target_sentence=target_sent, similar_sentence=similar_sentence, similar_paragraph=similar_paragraph)

        time_result, number_result, noun_result, duty_result, semantic_result = results
        sentence = similar_sentence
        res_txt = "存在"
        if time_result:
            res_txt+= "时间类型冲突 "
        if number_result:
            res_txt += "数值类型冲突 "
        if noun_result:
            res_txt += "专有名词类型冲突 "
        if duty_result:
            res_txt += "职责类型冲突 "
        if semantic_result:
            res_txt += "语义类型冲突 "
        if res_txt == "存在":
            res_txt = "不存在冲突"
            # sentence = ""
        return {
            "result": res_txt,
            "sentence": sentence
        }

    def find_paragraph(self, document, target_sent):
        '''
        找到最相似的的段落和句子
        :param document:
        :param target_sent:
        :return:
        '''
        content_lis, pre_content_lis = parser_doc_clear(document)
        high_score = 0
        similar_sentence = ""
        similar_paragraph = ""
        if not content_lis:
            return "不是政策文本格式，不能解析", ""
        for i in range(len(content_lis)):
            paragraph = content_lis[i]
            if paragraph:
                sentences = sentence_tokenize(paragraph)
                for sentence in sentences:
                    if sentence:
                        self.bleu = Bleu(1)
                        self.bleu.add_inst(cand=sentence, ref=target_sent)
                        score = self.bleu.get_score()
                        if score > high_score:
                            similar_sentence = sentence
                            similar_paragraph = paragraph
                            high_score = score
        if similar_sentence and similar_paragraph:
            #如果sentence后面有（）,那么继续增加
            print("similar_sentence:", similar_sentence)
            print("similar_paragraph:", similar_paragraph)
            start_index = similar_paragraph.index(similar_sentence)
            end_index = start_index + len(similar_sentence)
            if end_index < len(similar_paragraph):
                word = similar_paragraph[end_index]
                word_dic = {
                    "(":")",
                    "（":"）",
                    "[":"]",
                    "【":"】",
                    "{":"}",
                }
                if word in word_dic.keys():
                    end_index = similar_paragraph.index(word_dic[word], end_index+1) + 1
                similar_sentence = similar_paragraph[start_index:end_index]
            return similar_sentence, similar_paragraph
        else:
            return "", ""

    def judge_conflict(self, target_sentence, similar_sentence=None, similar_paragraph=None, source_att = None, target_att = None):
        '''
        判断是哪种类型的冲突
        :param target_sentence:
        :param similar_sentence:
        :param similar_paragraph:
        :return:
        '''
        time_result = False
        number_result = False
        noun_result = False
        duty_result = False
        semantic_result = False
        target_sent_copy = copy(target_sentence)
        # 时间冲突
        results = re.findall("\d+[年月日\.\-]+", target_sent_copy)
        if results:
            results_ = re.findall("\d+[年月日\.\-]+", similar_sentence)
            if results_:
                # print("time:", results)
                time_result = self.time_conflict(target_sentence, similar_sentence, similar_paragraph, source_att, target_att)
                print("time:", time_result)
                for r in results:
                    target_sent_copy = target_sent_copy.replace(r, "")
        #数值类型冲突
        results = re.findall("\d+|一二三四五六七八九十", target_sent_copy)
        if results:
            results_ = re.findall("\d+|一二三四五六七八九十", similar_sentence)
            if results_:
                print(results)
                number_result = self.number_conflict(target_sentence, similar_sentence, similar_paragraph, source_att, target_att)
                print("number:",number_result)

        #专有名词：
        for noun in self.noun_lis:
            if noun in target_sentence:
                noun_result = self.noun_conflict(target_sentence, similar_sentence, similar_paragraph, source_att, target_att, noun)
                print("noun:", noun_result)
                break
        #职责：
        for duty in self.duty_lis:
            if duty in target_sentence:
                duty_result = self.duty_conflict(target_sentence, similar_sentence, similar_paragraph, source_att, target_att, duty)
                print("duty:", duty_result)
                break

        #语义冲突
        try:
            semantic_result = self.semantic_conflict(target_sentence, similar_sentence, similar_paragraph, source_att, target_att)
            print("semantic:", semantic_result)
        except:
            print("存在semantic_result 解析错误")
            pass

        return (time_result, number_result, noun_result, duty_result, semantic_result)

    def time_conflict(self, target_sentence, similar_sentence, similar_paragraph, source_at, target_at):
        '''
        时间冲突检测(只针对出现一个日期时间的)
        :param target_sentence:
        :param similar_sentence:
        :param similar_paragraph:
        :return: True or False
        '''
        sentence_copy = copy(target_sentence)
        results = re.findall("\d+[年月日\.\-]+", sentence_copy)
        #获取时间
        date = results[0]
        #获取时间位置
        start_pos = target_sentence.index(date) + len(date)
        #获取时间表达的主体
        target = target_sentence[start_pos:]
        target = self.clear_punctuation(target)

        results = re.findall("\d+[年月日\.\-]+", similar_sentence)
        # 获取时间
        source_date = results[0]
        # 获取时间位置
        start_pos = similar_sentence.index(source_date) + len(source_date)
        source_sent = similar_sentence[start_pos:]
        source_sent = self.clear_punctuation(source_sent)
        #判断句子描述是否是相同的事情
        same_flag = False
        if target in source_sent:
            same_flag = True
        #增加句子语义匹配
        if not same_flag:
            similar_sentences = similar_sentence.split("，")
            for sentence in similar_sentences:
                score = self.bleu_cal(target_sentence, sentence)
                if score > 0.5:
                    same_flag = True
                    break

        #判断时间是否是一致的
        time_flag = False
        if date == source_date:
            time_flag = True

        if same_flag:
            if not time_flag:
                return True
            else:
                return False
        else:
            return False

    def number_conflict(self, target_sentence, similar_sentence, similar_paragraph,  source_att, target_att):
        '''
        数值冲突检测
        :param target_sentence:
        :param similar_sentence:
        :param similar_paragraph:
        :return:
        '''
        target_lis = self.find_number_words(target_sentence)
        source_lis = self.find_number_words(similar_sentence)
        for target_dic in target_lis:
            for source_dic in source_lis:
                if target_dic["noun"] == source_dic["noun"]:
                    target_number = target_dic["number"].replace("%", "")

                    source_number = source_dic["number"].replace("%", "")
                    if source_number.isdigit() and target_number.isdigit():
                        source_number = int(source_number)
                        target_number = int(target_number)
                        #都是减少
                        if target_dic["verb"] in self.neg_words and source_dic["verb"] in self.neg_words:
                            if source_number < target_number:
                                return True
                        #都是增加
                        if target_dic["verb"] not in self.neg_words and source_dic["verb"] not in self.neg_words:
                            if source_number > target_number:
                                return True
                        else:
                            return True
        return False

    def noun_conflict(self, target_sentence, similar_sentence, similar_paragraph, source_att=None, target_att=None, noun=None):
        '''
        专有名词冲突检测，
        :param target_sentence:
        :param similar_sentence:
        :param similar_paragraph:
        :return:
        '''
        start = target_sentence.index(noun)
        target_noun = target_sentence[0:start]
        target_explain = target_sentence[start+len(noun):]
        if target_noun in similar_sentence:
            if noun in similar_sentence:
                start = similar_sentence.index(noun) + len(noun)
                sourc_explain = similar_sentence[start:]

                if target_explain in sourc_explain or self.bleu_cal(target_explain, sourc_explain) > 0.9:
                    return False
                else:
                    return True
        return False

    def duty_conflict(self, target_sentence, similar_sentence, similar_paragraph, source_att, target_att, duty):
        '''
        职责冲突检测，
        :return:
        '''
        start = target_sentence.index(duty)
        target_duty = target_sentence[0:start]
        target_explain = target_sentence[start + len(duty):]
        if target_duty in similar_sentence:
            if duty in similar_sentence:
                start = similar_sentence.index(duty) + len(duty)
                sourc_explain = similar_sentence[start:]

                if target_explain in sourc_explain or self.bleu_cal(target_explain, sourc_explain) > 0.9:
                    return False
                else:
                    return True
        return False

    def semantic_conflict(self, target_sentence, similar_sentence, similar_paragraph, source_att, target_att):
        '''
        语义相反，冲突检测
        :param target_sentence:
        :param similar_sentence:
        :param similar_paragraph:
        :return:
        '''
        hanlpParser = HanlpParser()
        target_lis = hanlpParser.parser(target_sentence)
        source_lis = hanlpParser.parser(similar_sentence)
        for target_dic in target_lis:
            for source_dic in source_lis:
                if target_dic["noun"] and source_dic["noun"] and target_dic["noun"] == source_dic["noun"]:
                    if target_dic["verb"] in self.neg_words and source_dic["verb"] not in self.neg_words:
                        return True
                    elif target_dic["verb"] not in self.neg_words and source_dic["verb"] in self.neg_words:
                        return True
        return False
