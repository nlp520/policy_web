#encoding:utf-8
from conflict.conflict_detect import Conflict

if __name__ == '__main__':
    similar_sent = "工业技术软件化是指工业技术、工艺经验、制造知识和方法通过软件实现显性化、数字化和系统化的过程。"
    target_sent = "工业技术软件化是指工业技术、工艺经验制造知识和方法通过软件实现显性化、数字化和系统化的过程。"
    conflict = Conflict()
    conflict.judge_conflict(target_sentence=target_sent, similar_sentence=similar_sent)
    # conflict.find_paragraph(document=policy_lis[0][6], target_sent=target_sent)
    # conflict.judge_conflict(target_sentence=target_sent, similar_sentence=similar_sent)
    # res = conflict.find_number_words("培育20家以上面向全球的平台型龙头企业")
    # print(res)


