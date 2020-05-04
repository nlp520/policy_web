#coding:utf-8
#Team:BuaaNlp
#Author: Sui Guobin
#Date: 2019/12/7
#Tool: PyCharm
from typing import List
from pyhanlp import *
import re
import os
current_path = os.path.dirname(os.path.abspath(__file__))

class HanlpParser():
    def __init__(self,
                 dict_path:str = os.path.join(current_path, "dictionary.txt")):
        if dict_path:
            self.load_dict(dict_path)

    def load_dict(self, path:str):
        '''
        load Dictionary
        :param path:
        :return:
        '''
        CustomDictionary = JClass("com.hankcs.hanlp.dictionary.CustomDictionary")
        with open(path, "r", encoding="utf-8") as fin:
            lines = fin.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    CustomDictionary.add(line)

    def clear(self, sentence):
        results = re.findall(r"(?<=[\(|（])[^[\)|）]+", sentence)
        if results:
            for res in results:
                sentence = sentence.replace("(%s)"%(res), "")
                sentence = sentence.replace("（%s）"%(res), "")
        return sentence

    def parser(self, sentence:str):
        sentences = re.split("(。|；|，)", sentence)
        example_lis = []
        for sentence in sentences:
            sentence = sentence.strip().replace("、", "")
            parser_sentence = HanLP.parseDependency(sentence)
            word_lis = []
            for word in parser_sentence.iterator():  # 通过dir()可以查看sentence的方法
                word_lis.append(str(word).split())
            examples = self.analyze(word_lis)
            example_lis.extend(examples)
        return example_lis

    def analyze(self, word_lis: List[List[str]]):
        examples = []
        for i in range(len(word_lis)):
            if word_lis[i][7] == "动宾关系":
                v_s_index = int(word_lis[i][6]) - 1 #动词开始的坐标
                n_index = i

                #向前查找并列的动词
                v_e_index = v_s_index
                for j in range(v_s_index + 1, n_index):
                    if int(word_lis[j][6]) - 1 == v_s_index and word_lis[j][7] == "并列关系":
                        v_e_index = j  #结束的坐标

                #向后查找并列的名词
                n_e_index = n_index
                for j in range(n_index+1, len(word_lis)):
                    if int(word_lis[j][6]) - 1 == n_index and word_lis[j][7] == "并列关系":
                        n_e_index = j

                verb = "".join([word_lis[k][1] for k in range(v_s_index, v_e_index+1)])
                adj = "".join([word_lis[k][1] for k in range(v_e_index+1, n_index)])
                noun = "".join([word_lis[k][1] for k in range(n_index, n_e_index + 1) ])
                if len(verb) < 2:
                    continue
                if noun in ["之日起"]:
                    continue
                if len(verb) + len(adj) + len(noun) <=4:
                    continue
                example = {
                    "verb":verb,
                    "adj":adj,
                    "noun":noun
                }
                examples.append(example)
        #复合句子结构
        if len(examples) >=2:
            for i in range(len(examples)-1):
                if examples[i]["noun"] == examples[i+1]["verb"]:
                    examples[i]["noun"] = examples[i]["noun"] + examples[i+1]["adj"] + examples[i+1]["noun"]
                    return [examples[i]]
        return examples

if __name__ == '__main__':
    sentence = "广泛推进移动互联网、云计算、大数据、物联网等与家电制造业加速融合".replace("、", "")
    # sentence = "围绕产业链关键环节"

    hanlp = HanlpParser("./dictionary.txt")
    results = hanlp.parser(sentence)
    for r in results:
        print(r)
    pass
