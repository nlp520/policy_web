# _*_encoding:UTF-8_*_

import logging
from BLEU.bleu import Bleu
logger = logging.getLogger(__name__)

def find_policy(ref, rs, number):
    '''
    通过政策名相似度检索，从数据库中检索出相似度最高的政策名
    采用bleu1计算相似度，采用倒排索引的方式得到最高的政策
    :param cand:
    :return:
    '''
    logger.info("待查找的政策名：%s " %(ref))
    policy_dic = {}
    for policy_name in rs:
        bleu = Bleu(1)
        bleu.add_inst(policy_name, ref)
        score = bleu.get_score()
        policy_dic[policy_name] = score

    sort_policy_list = sorted([(value, key) for (key, value) in policy_dic.items()], reverse=True)
    for i in range(min(number, len(sort_policy_list))):
        logger.info(sort_policy_list[i])
    mix = min(number, len(sort_policy_list))
    res = [x[1] for x in sort_policy_list[0:mix]]
    return res