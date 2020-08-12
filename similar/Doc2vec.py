#coding:utf-8
#Team:BuaaNlp
#Author: Sui Guobin
#Date: 2019/12/26
#Tool: PyCharm
from numpy import dot
import logging
import os
import gensim
import numpy as np
from gensim import utils, matutils
from gensim.models.doc2vec import Doc2Vec, LabeledSentence
import jieba
import time
TaggededDocument = gensim.models.doc2vec.TaggedDocument

current_path = os.path.dirname(os.path.abspath(__file__))

def get_datasest(path:str):
    with open(path, 'r', encoding="utf-8") as cf:
        docs = cf.readlines()
        print(len(docs))
    x_train = []
    # y = np.concatenate(np.ones(len(docs)))
    for i, text in enumerate(docs):
        word_list = text.split(' ')
        l = len(word_list)
        word_list[l - 1] = word_list[l - 1].strip()
        document = TaggededDocument(word_list, tags=[i])
        x_train.append(document)

    return x_train


def getVecs(model, corpus, size):
    vecs = [np.array(model.docvecs[z.tags[0]].reshape(1, size)) for z in corpus]
    return np.concatenate(vecs)


def train(x_train, epoch_num=30):
    # 打印日志信息
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    model_dm = Doc2Vec(x_train, min_count=5)
    model_dm.train(x_train, total_examples=model_dm.corpus_count, epochs=epoch_num)
    model_dm.save('./doc2vec/doc2vec.model')
    return model_dm

class DocVec():
    def __init__(self):
        self.model_dm = Doc2Vec.load(os.path.join(current_path, "doc2vec", "doc2vec.model"))

    def cal_similar(self, s1, s2, use_jieba=False):
        if use_jieba:
            s1_tokens = list(jieba.cut(s1))
            s2_tokens = list(jieba.cut(s2))
        else:
            s1_tokens = s1.split(" ")
            s2_tokens = s2.split(" ")
        t1 = time.time()
        inferred_s1 = self.model_dm.infer_vector(s1_tokens)
        inferred_s2 = self.model_dm.infer_vector(s2_tokens)
        print("inferred_s1:", inferred_s1.shape)
        t2 = time.time()
        print("time1:", t2 - t1)
        sims = dot(matutils.unitvec(inferred_s1), matutils.unitvec(inferred_s2))
        t3 = time.time()
        print("time2:", t3 - t2)
        return sims

    def cal_similar_batch(self, sent1_lis, sent2_lis):
        s1_tokens = [list(jieba.cut(s1)) for s1 in sent1_lis]
        s2_tokens = [list(jieba.cut(s2)) for s2 in sent2_lis]
        inferred_s1 = self.model_dm.infer_vector(s1_tokens)                                      
        inferred_s2 = self.model_dm.infer_vector(s2_tokens)                                      
        sims = dot(matutils.unitvec(inferred_s1), matutils.unitvec(inferred_s2))
        print(sims)
        return sims
    
if __name__ == '__main__':
    # x_train = get_datasest('./dataset/corpus.txt')
    # model_dm = train(x_train)
    start_time = time.time()
    docvec = DocVec()
    # s1 = ["推动大数据基础平台建设".replace(" ", ""), "推动大数据基础平台建设".replace(" ", "")]
    # s2 = ["发展大数据人工智能".replace(" ", ""), "发展大数据人工智能".replace(" ", "")]
    # score = docvec.cal_similar_batch(s1, s2)
    # print(score)

    for i in range(10000):
        s1 = "推动大数据基础平台建设"
        s2 = "发展大数据人工智能"
        score = docvec.cal_similar(s1, s2, use_jieba=True)
        # print("score:", score)

    end_time = time.time()
    print("time:", (end_time - start_time))
