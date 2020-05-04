#1.导包
import requests
#2.调用post方法
#请求的URL


def test_dataProcess():
    url = 'http://127.0.0.1:5000/dataProcess'
    # 请求头
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    # 请求的参数

    data = {"text":'''
    
    '''}

    r = requests.post(url, data=data, headers=headers)
    # 3.获取响应对象
    print(r.json())  # json格式



