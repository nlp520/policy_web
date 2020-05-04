#!/usr/bin/env python
# _*_coding:utf-8 _*_
import re
import os
can_not_find_cnt = 0

'''
normalize time expression to "2015-07-08"
'''
def normalizeTime(time):
    time = time.replace("〇","0").replace("一","1").replace("二","2").replace("三","3").replace("四","4").replace("五", "5").replace("六","6").replace("七","7").replace("八","8").replace("九","9").replace("两","2").replace("十","1")
    time = time.replace("年","-").replace("月","-").replace("日","-")
    pattern = "-[\d]-"
    res = re.findall(pattern,time)
    for x in res:
        time = time.replace(x,x[0] + "0" + x[1:])
    res = re.findall(pattern,time)
    for x in res:
        time = time.replace(x,x[0] + "0" + x[1:])
    if(time[-1] == "-"):
        time = time[0:-1]
    return time
'''
extract infomation from policy
'''
def extract(root,file):
    path = os.path.join(root,file)
    with open(path,"r+",encoding="utf-8") as f:
        lines = f.readlines()
        text = ""
        for line in lines:
            text += line
        text = text.replace("\n", "").replace(" ","")

        policy_name = extractPolicyName(file)
        post_time = normalizeTime(extractPostTime(lines,file))
        post_org = extractPostOrg(lines,text,policy_name).replace("\n","")
        reference_policy = extractReference(text)
        print(post_org)
        print(policy_name)
        print(post_time)
        print(reference_policy)
        print(file)
        print(text)
        print("- - - - - - - - - - - - - - - - -  - -- - - - - - - - - - - -  -- - - - - - ")

'''
extract post time:
high priority
2018年7月14日
2018年7月
二〇一八年七月十四日
二〇一八年七月
2018-07-14
2018-07

low priority
policy_name + [2018]|(2018)|（2018）|〔2018〕
'''
post_time_pattern = "[\d]{4}年[\d]{1,2}月[\d]{1,2}日|[\d]{4}年[\d]{1,2}月|" \
                    "[〇两一二三四五六七八九十]{4}年[〇两一二三四五六七八九十]{1,2}月[〇两一二三四五六七八九十]{1,2}日|" \
                    "[〇两一二三四五六七八九十]{4}年[〇两一二三四五六七八九十]{1,2}月|" \
                    "[\d]{4}-[\d]{1,2}-[\d]{1,2}"

post_year_pattern = "\[[\d]{4}\]|\([\d]{4}\)|（[\d]{4}）|〔[\d]{4}〕|【[\d]{4}】"
def extractPostTime(lines,file):
    text = ""
    for line in lines:
        text += line
        if("发布时间" in line):
            res = re.findall(post_time_pattern,line)
            if(len(res > 0)):
                return res[0]
            res = re.findall(post_year_pattern,line)
            if(len(res) > 0):
                return res[0][1:-1] + "年"
    text = text.replace(" ","").replace("\n","")

    res = re.findall(post_time_pattern,text)
    if(len(res) > 0):
        return res[0]

    res = re.findall(post_year_pattern,file)
    if(len(res) > 0):
        return res[0][1:-1] + "年"

    res = re.findall(post_year_pattern,text)
    if(len(res) > 0):
        return res[0][1:-1] + "年"
    global can_not_find_cnt
    can_not_find_cnt += 1
    return "can not find"

'''
extract policy name
'''
pattern_serial = "[\d]{1,2}-[\d]{1,2}[\D]|[\w]{1,2}-[\d]{1,2}[\D]|[\d]{1,2}[\D]"
pattern_locatin = ".*市-{1,2}|.*省-{1,2}|.*区-{1,2}|.*县-{1,2}"
policy_name_pattern = "《[^》]*》"
pattern_verb = "印发.*的通知|发布.*的通知"
pattern_about = "关于.*的通知"
pattern_noun = ".*计划|.*规划|.*条例|.*办法|.*汇报|.*资料|.*公告|.*方案|.*意见"

def extractPolicyName(file):
    pattern = re.compile(policy_name_pattern)
    file = file.replace(" ", "").replace(".txt", "")
    '''
    remove invalid prefix
    '''
    res = re.match(pattern_serial, file)
    if res != None:
        file = file[res.span()[1] - 1:]
    res = re.match(pattern_locatin, file)
    if res != None:
        file = file[res.span()[1]:]
    '''
    find 《xxx》 from filename
    '''
    res = re.findall(pattern, file)
    if (len(res) > 0):
        return res[0]

    '''
    find other patterns from filename
    '''
    res = re.findall(pattern_verb, file)
    if (len(res) > 0):
        return "《" + res[0][2:-3] + "》"

    res = re.findall(pattern_noun, file)
    if (len(res) > 0):
        return "《" + file + "》"

    res = re.findall(pattern_about, file)
    if (len(res) > 0):
        return "《" + file + "》"
    return "《" + file + "》"

'''
extract reference policy
'''
def extractReference(text):
    res = re.findall(policy_name_pattern,text)
    return res


pattern_org = ".*?[区|厅|会|委|局|组|办公室|兵团|政府]关于.*?[通知|意见]|.*?[区|厅|会|委|局|组|兵团|办公室|政府][制定|发布]"
def extractPostOrg(lines,text,policyName):
    for line in lines:
        if "发文机构" in line:
            idx = line.find("发文机构")
            return line[idx + 5:]
    for line in lines:
        line = line.replace("\n","")
        if line.endswith("委员会") or line.endswith("厅") or line.endswith("政府") or line.endswith("委") or line.endswith("研究院") or line.endswith("所"):
            return line
    res = re.findall(pattern_org,text)
    if(len(res) > 0):
        if "关于" in res[0]:
            return res[0][:res[0].find("关于")]
        elif "制定" in res[0]:
            return res[0][:res[0].find("制定")]
        elif "发布" in res[0]:
            return res[0][:res[0].find("发布")]
    loc_pattern = ".*?[乡|区|县|市|省]"
    res = re.match(loc_pattern,policyName[1:])
    if res != None:
        return policyName[1:][res.span()[0]:res.span()[1]] + "人民政府"
    return ""

def process():
    root = "./dataset/introduction/"
    files = os.listdir(root)
    for file in files:
        extract(root,file)

if __name__ == '__main__':
    process()
    print(can_not_find_cnt)



