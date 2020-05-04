#conding:utf-8

def classifyCategoriesByName(text: str) -> list:
    '''
    大数据
    软件
    云计算
    信息化
    人工智能
    智能制造
    电子商务
    数字经济
    物联网
    互联网+
    :param text:
    :return:
    '''
    categories = []
    text = text.replace("信息化部", "").replace("软件服务业司", "").replace("信息化委员会", "")
    if "智能制造" in text or "两化" in text or ("工业化" in text and "信息化" in text) or ("制造" in text and "互联网" in text)\
        or "工业互联网" in text or "绿色制造" in text or "中国制造" in text:
        categories.append("智能制造")

    if "大数据" in text or "政府数据" in text or ("政务" in text and "资源" in text):
        categories.append("大数据")

    if "云计算" in text or "云平台" in text:
        categories.append("云计算")
    if "人工智能" in text:
        categories.append("人工智能")
    if "电子商务" in text:
        categories.append("电子商务")
    if "物联网" in text:
        categories.append("物联网")
    if "智能制造" not in categories:
        if "互联网" in text:
            categories.append("互联网+")
        if "云计算" not in categories:
            if "软件" in text or "信息服务业" in text or "战略性新兴产业" in text or "信息化" in text or "信息产业" in text \
                    or "电子政务" in text:
                categories.append("软件")

    if "软件" not in categories:
        if "数字经济" in text or "信息经济" in text or "数字" in text:
            categories.append("数字经济")

    if not categories:
        categories.append(" ")
    return categories

if __name__ == '__main__':

    pass
