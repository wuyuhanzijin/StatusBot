#!/usr/bin/env python3
# coding:utf-8


import requests
import json
import datetime
import time
import os


# 获取环境变量
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def status_normal(url: str):
    '''
    检测一个地址是否可以被访问
    如果Get的结果为200则可以被访问
    其余情况均为异常

    : url 待检测的地址,需要协议头
    : status 返回值,是一个字符串,可能是"正常"或者是"异常"加上异常原因
    '''

    # 模拟Edge发送请求，以免网站有反爬虫设置
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    }

    try:
        # 尝试获取状态代码
        r = requests.get(url=url, headers=headers, timeout=20)
        code = r.status_code

        # 判断状态码是否为2开头
        if str(code)[0] == "2":
            status = "正常"
            return status
        else:
            status = "异常，状态码：" + str(code)
            return status
    except Exception as error:
        status = "异常，错误：" + str(error)
        return status
    

def get_params(text: str):
    '''
    取得Webhook的消息JSON
    样式从card_example.json读取
    仅支持发送卡片
    读取修改card->elements->1->text->content

    : text 插入的文本
    : params 返回值,消息JSON
    '''

    # 读取card_example.json
    with open("card_example.json", "r", encoding="utf-8") as f:
        params_example = json.load(f)

    # 修改card->elements->1->text->content
    params_example["card"]["elements"][1]["text"]["content"] = str(text)
    params = params_example

    return params
    


def send(params):
    '''
    用于发送讯息到飞书/Lark

    : params Webhook的消息JSON
    '''

    resp = requests.post(WEBHOOK_URL, json=params)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") and result.get("code") != 0:
        print(f"发送失败：{result['msg']}")
        return
    print("消息发送成功")


def main():
    '''
    主函数
    '''

    kinds = ["services", "links"]

    now = datetime.datetime.now()
    bj_time = now + datetime.timedelta(hours=8)
    text = "检测时间(UTC +8)：{}\n\n".format(bj_time.strftime('%Y-%m-%d %H:%M:%S'))

    # 读取配置
    with open("data.json", "r", encoding="utf-8") as f:
        date = json.load(f)

    # 遍历配置
    for kind in kinds:
        sites = date[kind]
        if kind == "services":
            text += "__=====[ 自有服务 ]=====__\n"
        elif kind == "links":
            text += "__=====[ 友情链接 ]=====__\n"
        for site in sites:
            # 加载各项配置
            name = site["name"]
            url = site["url"]
            # 预留后续开发使用，目前无效
            # method = site["method"]

            print("开始检测：{}".format(name))
            status = status_normal(url)
            print("检测完成，状态{}".format(status))

            if status == "正常":
                info = "__{}__（{}）\n__状态__: <font color=Green>正常</font>\n\n".format(
                    name, url
                )
            else:
                info = "__{}__（{}）\n__状态__: <font color=Red>{}</font>\n\n".format(
                    name, url, status
                )
            # 合成信息
            print("开始拼接")
            text += info
            print("拼接完成\n")
            time.sleep(0.5)

    text += "注：本消息系机器人自动发送\n使用Github Action自动检测"

    # 获取消息JSON
    params = get_params(text)

    # 发送消息
    send(params)


if __name__ == '__main__':
    main()
