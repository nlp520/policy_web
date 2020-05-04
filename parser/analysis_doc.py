#encoding:utf-8
from pyhanlp import *
import re
import json
import logging
from .syntactic_parsing import HanlpParser
from .provinces import province_dic
from .CategoryClassify import classifyCategoriesByName
from .EntityExtraction import extractPostOrg, normalizeTime, extractPostTime
logger = logging.getLogger(__name__)

current_path = os.path.dirname(os.path.abspath(__file__))

class BasicInfo():

    def __init__(self):
        pro_pattern = "|".join(list(province_dic.keys()))
        for _, values in province_dic.items():
            pro_pattern += "|" + "|".join(values)
        self.pro_pattern = "(" + pro_pattern + ")"

    def extract_name(self, content):
        content = content.split("\n")
        name = content[0]
        name = name.replace("附:", "").replace("附：", "")
        return name

    def extract_province(self, name):
        res = re.findall(self.pro_pattern, name)
        if res:
            return("".join(list(set(res))))
        else:
            return ""

    def extract_org(self, name, prefaces):
        org_pattern = "(人民政府|人民政府办公厅)"
        res = re.findall(org_pattern, name)
        if res:
            return("".join(list(set(res))))
        else:
            post_org = extractPostOrg(prefaces.split("\n"), prefaces, name).replace("\n", "")
            return post_org

    def extract_date(self, prefaces, name):
        post_time = normalizeTime(extractPostTime(prefaces.split("\n"), name))
        return post_time

    def extract_cate(self, name):
        return classifyCategoriesByName(name)

infoextract = BasicInfo()

def parser_doc_clear(content:str, mode=1):
    '''
    对文本内容进行清洗
    :param content:
    :return:
    '''
    content_lis = []
    documents = [para.strip() for para in content.split("\n") if para.strip()]
    prefaces = ""
    prefaces_lis = []
    stop_preface_flag = False
    title_flag = False
    last_content = ""
    # first = Paragraph()
    logger.info("开始解析")
    for para in documents:
        if para:
            res = None
            if mode == 1:
                res = pro_pattern1(para)
            elif mode == 2:
                res = pro_pattern2(para)
            if res:
                if isinstance(res, tuple):
                    if last_content:
                        content_lis.append(last_content)
                        last_content = ""

                    title_flag = True
                    stop_preface_flag = True
                    level = res[0]
                    title = res[1]
                    content = res[2]
                    content_lis.append(title)
                    if content:
                        last_content += content.strip()

                elif isinstance(res, str) and title_flag:
                    last_content += res.strip()

            if not stop_preface_flag:
                prefaces += para.strip() + "\n"
                prefaces_lis.append(para.strip())
    if last_content:
        content_lis.append(last_content)
    return content_lis, prefaces_lis

def clear_txt(content):
    content = content.replace("白鹿智库 查政策，上白鹿(www.bailuzhiku.com)", "")
    return content

#普通文本数据
def pro_pattern1(content):
    content = content.strip()
    content = "".join(content.split())
    results = re.findall("^[一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十]、[a-zA-Z0-9_\u4e00-\u9fa5'‘’“”+\-]+", content)
    if results:
        title = results[0]
        context = content[content.find(title) + len(title): len(content)].strip()
        return ("num1", title, context)

    results = re.findall("^（[一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十]）[a-zA-Z0-9_\u4e00-\u9fa5'‘’“”+\-，]+", content)
    if results:
        title = results[0]
        context = content[content.find(title) + len(title): len(content)].strip()
        if len(title) < 25 and len(title) >=4:#and len(context) > 5
            return ("num2", title, context)

    #以第多少条 形式的二级标题
    results = re.findall("^第[一|二|三|四|五|六|七|八|九|十]+条", content)
    if results:
        title = results[0]
        context = content[content.find(title) + len(title): len(content)].strip()
        return ("num3", title, context)

    results = re.findall("^[0-9]+[.|．|、][a-zA-Z_\u4e00-\u9fa5'‘’“”+\-]+",
                         content)
    if results:
        title = results[0]
        context = content[content.find(title) + len(title): len(content)].strip()
        return ("num4", title, context)

    results = re.findall("^[一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十]是[a-zA-Z0-9_\u4e00-\u9fa5'‘’“”+\-]", content)

    if results:
        title = results[0]#[results[0].find("是") + 1:len(results[0])]
        context = content[content.find(title) + len(title): len(content)].strip()
        return ("num5", title, context)

    #不包含一二三四......的四级标题识别
    results = re.findall("^[a-zA-Z0-9_\u4e00-\u9fa5'‘’“”/\s+\-]+。",
                         content)
    if results:
        title = results[0]  # [results[0].find("是") + 1:len(results[0])]
        context = content[content.find(title) + len(title): len(content)-1].strip()
        title = "".join(title.split())
        if len(title) < 20 and len(title) >=4 and len(context) > 5:
            return ("num6", title, context)

    return content

#章  条  形式的文本
def pro_pattern2(content):
    content = content.strip()
    content = "".join(content.split())
    results = re.findall("^[一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十]、[a-zA-Z0-9_\u4e00-\u9fa5'‘’“”+\-\s]+", content)

    if results:
        title = results[0]
        context = content[content.find(title) + len(title): len(content)].strip()
        return ("一级", title, context)

    results = re.findall("^第[一|二|三|四|五|六|七|八|九|十]+章[a-zA-Z0-9_\u4e00-\u9fa5'‘’“”+\-\s]+",
                         content)
    if results:
        title = results[0]
        context = content[content.find(title) + len(title): len(content)].strip()
        return ("一级", title, context)

    # results = re.findall("^（[一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十]）[a-zA-Z0-9_\u4e00-\u9fa5'‘’“”+\-]+", content)
    # if results:
    #     title = results[0]
    #     context = content[content.find(title) + len(title): len(content)].strip()
    #     return ("二级", title, context)

    #以第多少条 形式的二级标题
    results = re.findall("^第[一|二|三|四|五|六|七|八|九|十]+条", content)
    if results:
        title = results[0]
        context = content[content.find(title) + len(title): len(content)].strip()
        return ("二级", title, context)

    results = re.findall("^[0-9]+[.|．|、][a-zA-Z_\u4e00-\u9fa5'‘’“”+\-]+",
                         content)
    if results:
        title = results[0]
        context = content[content.find(title) + len(title): len(content)].strip()
        return ("三级", title, context)

    results = re.findall("^[一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十]是[a-zA-Z0-9_\u4e00-\u9fa5'‘’“”+\-]", content)

    if results:
        title = results[0]#[results[0].find("是") + 1:len(results[0])]
        context = content[content.find(title) + len(title): len(content)].strip()
        return ("四级", title, context)
    #不包含一二三四......的四级标题识别
    results = re.findall("^[a-zA-Z0-9_\u4e00-\u9fa5'‘’“”/\s+\-]+。",
                         content)
    if results:
        title = results[0]  # [results[0].find("是") + 1:len(results[0])]
        context = content[content.find(title) + len(title): len(content)-1].strip()
        title = "".join(title.split())
        if len(title) < 20:
            return ("四级", title, context)

    return content

def judge_pattern(content):
    if "第一条" in content and "第二条" in content:
        return 2
    else:
         return 1

def generate_lis(dic):
    '''
    dic转化为lis
    :param dic:
    :return:
    '''
    lis = []
    for d in dic:
        value = d["verb"] + d["adj"] + d["noun"]
        lis.append(value)
    return lis

def generate_title(lis, title_dic):
    dic = {}
    number = len(lis)
    level = lis[0][0]
    title = lis[0][1]
    old_id = 1
    if number == 1:
        return {title:title_dic.get(title, [])}
    for i in range(1, number):
        if level == lis[i][0]:
            if old_id == i:
                dic_ = {}
            else:
                dic_ = generate_title(lis[old_id: i], title_dic)
            if not dic_:
                dic_ = title_dic.get(title, [])
            dic.update({title: dic_})
            title = lis[i][1]
            old_id = i + 1
    if level == lis[i][0]:
        dic.update({title: title_dic.get(title, [])})
    if i != number-1:
        dic_ = generate_title(lis[old_id: number], title_dic)
        dic.update({title: dic_})
    return dic

def parser_doc(document):
    '''
    存储：
    对document
    :return:
    '''
    mode = judge_pattern(document)

    prefaces = ""
    prefaces_lis = []
    stop_preface_flag = False
    title_flag = False

    last_content = ""

    data_lis = []
    title_dic = {}
    hanlp = HanlpParser(os.path.join(current_path, "dictionary.txt"))
    logger.info("开始解析")
    documents = document.split("\n")
    new_title = ""

    for para in documents:
        if para:
            res = None
            if mode == 1:
                res = pro_pattern1(para)
            elif mode == 2:
                res = pro_pattern2(para)
            if res:
                if isinstance(res, tuple):
                    last_title = new_title
                    title_flag = True
                    stop_preface_flag = True
                    level = res[0]
                    title = res[1]
                    content = res[2]
                    new_title = title
                    data_lis.append([level, title])

                    if last_content:
                        results = hanlp.parser(last_content)
                        title_dic.update({last_title:generate_lis(results)})
                        last_content = ""

                    if content:
                        last_content += content.strip()

                elif isinstance(res, str) and title_flag:
                    last_content += res.strip()

            if not stop_preface_flag:
                prefaces += para.strip() + "\n"
                prefaces_lis.append(para.strip())
    if last_content:
        last_title = new_title
        results = hanlp.parser(last_content)
        title_dic.update({last_title: generate_lis(results)})
    result_dic = generate_title(data_lis, title_dic)
    return result_dic

def basicInfoExtract(document):
    '''
    基本信息提取
    :return:
    '''
    mode = judge_pattern(document)

    prefaces = ""
    prefaces_lis = []
    stop_preface_flag = False

    logger.info("开始解析")
    documents = document.split("\n")

    for para in documents:
        if para:
            res = None
            if mode == 1:
                res = pro_pattern1(para)
            elif mode == 2:
                res = pro_pattern2(para)
            if res:
                if isinstance(res, tuple):
                    stop_preface_flag = True

            if not stop_preface_flag:
                prefaces += para.strip() + "\n"
                prefaces_lis.append(para.strip())

    #对文本进行提取基本信息
    name = "",  # 政策名 ok
    org ="人民政府",  # 发布机构
    category = "",  # 政策类别  ok
    province = "",  # 发布省份  ok
    date = "",  # 发布时间
    context= document

    prefaces = prefaces.strip()
    name = infoextract.extract_name(prefaces)
    # print(prefaces)
    # print("name:", name)
    if name:
        province = infoextract.extract_province(name)
        # print(province)
        org = infoextract.extract_org(name, prefaces)
        # print("org:", org)
        date = infoextract.extract_date(prefaces, name)
        # print("date:", date)
        category = infoextract.extract_cate(name)
        # print("category:", category)
    results = {
        "name": name,  # 政策名
        "org": org,  # 发布机构
        "category": category,  # 政策类别
        "province": province,  # 发布省份
        "date":date,  # 发布时间
        "context": context  # 政策内容
    }
    return results

if __name__ == '__main__':
    document = ""
    with open("test.txt", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            document += line
    res = basicInfoExtract(document)
    pass