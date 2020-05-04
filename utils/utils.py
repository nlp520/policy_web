import os
import numpy as np
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO

def sentence_tokenize(doc:str= None) -> list:
    '''
    基于pyltp进行分句
    :param doc:
    :return:
    '''
    doc = doc.replace("\t", "")#.replace("\n", "")
    import re
    doc = re.sub('([。；！？\?])([^”’])', r"\1\n\2", doc)  # 单字符断句符
    doc = re.sub('(\.{6})([^”’])', r"\1\n\2", doc)  # 英文省略号
    doc = re.sub('(\…{2})([^”’])', r"\1\n\2", doc)  # 中文省略号
    doc = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', doc)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    doc = doc.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return doc.split("\n")

common_used_numerals_tmp ={'零':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '日':7, '八':8, '九':9, '十':10}
common_used_numerals = {}
for key in common_used_numerals_tmp:
  common_used_numerals[key] = common_used_numerals_tmp[key]
def chinese2digits(uchars_chinese):
  total = 0
  r = 1
  for i in range(len(uchars_chinese) - 1, -1, -1):
    val = common_used_numerals.get(uchars_chinese[i])
    if val >= 10 and i == 0:  #应对 十三 十四 十*之类
      if val > r:
        r = val
        total = total + val
      else:
        r = r * val
        #total =total + r * x
    elif val >= 10:
      if val > r:
        r = val
      else:
        r = r * val
    else:
      total = total + r * val
  return total


def create_uuid():
    import uuid
    return str(uuid.uuid1())


def readPDF(pdfFile):
    '''
    读取pdf
    :param pdfFile:
    :return:
    '''
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)

    process_pdf(rsrcmgr, device, open(pdfFile, "rb"))
    device.close()

    content = retstr.getvalue()
    retstr.close()
    return content


if __name__ == '__main__':
    # content = '''
    # 为深入贯彻落实《国务院关于促进云计算创新发展培育信息产业新业态的意见》(国发〔2015〕5号)《国务院关于印发促进大数据发展行动纲要的通知》(国发〔2015〕50号)《国务院办公厅关于运用大数据加强对市场主体服务和监管的若干意见》(国办发〔2015〕51号)等文件精神，全面推进本市大数据和云计算发展，特制定本行动计划。'''
    # content = content.strip()
    # results = sentence_tokenize(content)
    # print(results)
    # generate_dataset()
    print(chinese2digits("六十八"))
    pass