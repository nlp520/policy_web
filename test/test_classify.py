from classify.keyword_classify import CnnKeywordClassify, BertKeywordClassify
from classify.classify import BertClassify

if __name__ == '__main__':
    classify = BertClassify()
    sentence = "2017年底前形成跨部门数据资源共享共用格局。"
    res = classify.predict(sentence=sentence)
    print(res)







