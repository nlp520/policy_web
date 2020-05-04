# -*- coding: utf-8 -*-
import os
import jieba
import jieba.posseg as psg
import pickle
from .tfidfModel import train_idf, TfIdf

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 停用词表加载方法
def get_stopword_list():
    # 停用词表存储路径，每一行为一个词，按行读取进行加载
    # 进行编码转换确保匹配准确率
    stop_word_path = os.path.join(root_path, "dataset", "stoplist.txt")
    stopword_list = [sw.replace('\n', '') for sw in open(stop_word_path,encoding='utf-8').readlines()]
    return stopword_list


# 分词方法，调用结巴接口
def seg_to_list(sentence, pos=False):
    if not pos:
        # 不进行词性标注的分词方法
        seg_list = jieba.cut(sentence)
    else:
        # 进行词性标注的分词方法
        seg_list = psg.cut(sentence)
    return seg_list


# 去除干扰词
def word_filter(seg_list, pos=False):
    stopword_list = get_stopword_list()
    filter_list = []
    # 根据POS参数选择是否词性过滤
    ## 不进行词性过滤，则将词性都标记为n，表示全部保留
    for seg in seg_list:
        if not pos:
            word = seg
            flag = 'n'
        else:
            word = seg.word
            flag = seg.flag
        if not flag.startswith('n'):
            continue
        # 过滤停用词表中的词，以及长度为<2的词
        if not word in stopword_list and len(word) > 1:
            filter_list.append(word)
    return filter_list


# 数据加载，pos为是否词性标注的参数，corpus_path为数据集路径
def load_data(pos=False, corpus_path=os.path.join(root_path, "dataset", "corpus.txt")):
    # 调用上面方式对数据集进行处理，处理后的每条数据仅保留非干扰词
    doc_list = []
    for line in open(corpus_path, 'r',encoding='utf-8'):
        content = line.strip()
        seg_list = seg_to_list(content, pos)
        filter_list = word_filter(seg_list, pos)
        doc_list.append(filter_list)

    return doc_list

def tfidf_extract(word_list, pos=False, keyword_num=10, idf = True):
    if not idf:
        doc_list = load_data(pos)
        idf_dic, default_idf = train_idf(doc_list)
    else:
        idf_dic = pickle.load(open(os.path.join(root_path, "dataset", "idf_dic.pkl"), "rb"))
        default_idf = idf_dic["default"]
    tfidf_model = TfIdf(idf_dic, default_idf, word_list, keyword_num)
    return tfidf_model.get_tfidf()

def getKeywords(sent, pos=True ,num=10):
    '''
    获取关键词
    :param sent:
    :param pos:
    :param num:
    :return: 关键词按照空格进行区分
    '''
    sent = sent.strip()
    seg_list = seg_to_list(sent, pos)
    filter_list = word_filter(seg_list, pos)
    results = tfidf_extract(filter_list, pos, keyword_num=num)
    return results


if __name__ == '__main__':
    text ='''
    中小微企业公共服务大数据。
      '''
    results = getKeywords(text)
    print(results)

    pass



