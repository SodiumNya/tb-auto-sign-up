import random
import re
import time


import requests
import yagmail
from bs4 import BeautifulSoup

myCookies = {

    "Cookie": "###" #将###替换为你的cookie
}




def run():
    current_page = 1
    success = 0
    fail_dict = {}

    while True:
        tb_name_list, page_num = get_mylike_list(current_page)
        count, fail_dict = sign(tb_name_list)
        success += count
        fail_dict.update(fail_dict)

        current_page += 1
        if current_page > page_num:
            break
        time.sleep(random.randint(5, 10))

    # 发送报告
    send_sign_up_report_email(success, fail_dict)


def get_mylike_list(current_page: int):
    """
    获取关注的贴吧名
    :param current_page: 当前页
    :return: res 签到列表, page_num 总页数
    """
    url = f'https://tieba.baidu.com/f/like/mylike?&pn={current_page}'
    mylike_header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/102.0.0.0"
                      "Safari/537.36",
    }
    req = requests.get(url, headers=mylike_header, cookies=myCookies)
    html = req.text

    # 解析html
    soup = BeautifulSoup(html, 'html.parser')

    # 读取每一行
    rows = soup.find_all('tr')
    res = []
    # 遍历每一行，获取贴吧名
    for row in rows:
        cells = row.find_all('td')
        if cells:
            ba_name = cells[0].find('a').text.strip()
            res.append(ba_name)

    page_num = get_page_num(soup)
    return res, page_num


def get_page_num(html: BeautifulSoup):
    """
    计算关注的吧有多少页
    :param html: 请求返回的html页
    :return: 如果大于一页，返回相应的页数，否则返回0， 表示不足一页
    """
    last_page_link = html.find('a', text='尾页')
    if last_page_link:
        last_page = last_page_link.get('href').split('=')[-1]
        return int(last_page)
    else:
        return 0


def sign(t_name_list: list):
    """
    执行签到
    :param t_name_list: 要签到的贴吧列表
    :return: sign_success_num 签到成功数量, sign_fail_list dict保存了签到失败的贴吧及其失败原因
    """
    url = 'https://tieba.baidu.com/sign/add'
    sign_headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest"
    }
    sign_success_num = 0
    sign_fail_list = {}
    for tb_name in t_name_list:
        tbs = get_tbs(tb_name)
        if tbs is None:
            continue
        data = {
            "ie": "utf-8",
            "kw": tb_name,
            "tbs": tbs
        }
        req = requests.post(url, data=data, headers=sign_headers, cookies=myCookies)
        resp_json = req.json()
        if resp_json['no'] == 1101 or resp_json['no'] == 0:
            sign_success_num += 1
        else:
            sign_fail_list.update({tb_name + "吧", resp_json['error']})

        # print(f'{tb_name}吧->', resp_json)

    return sign_success_num, sign_fail_list


def get_tbs(tb_name):
    """
    获取tb_name对应的tbs
    :param tb_name: 贴吧名
    :return: tbs 一串神秘数字
    """
    url = f'https://tieba.baidu.com/f?kw={tb_name}'
    tbs_header = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Accept': '*/*',
        'Host': 'tieba.baidu.com',
        'Connection': 'keep-alive',
        'Cookie': 'BAIDUID=C7389BA9CD301A1433833B517CD373A9:FG=1'
    }

    # 发送请求
    req = requests.get(url, headers=tbs_header, cookies=myCookies)
    text = req.text
    # 使用正则表达式匹配 tbs 值
    match = re.search(r"PageData\s*=\s*{\s*'tbs': \"([^\"]+)\"", text)

    if match:
        return match.group(1)
    return None


def send_sign_up_report_email(success_count, fail_dict):
    """
    发送签到报告
    :param success_count: 签到成功数量
    :param fail_dict: 签到失败的dict， 包含贴吧名以及对应的签到失败原因
    :return: void
    """
    # 连接服务器
    # 用户名、授权码、服务器地址
    # 请将 'your email', 'SMTP authorization code','your email host' 替换为你的真实用户名、授权码、服务器地址
    yag_server = yagmail.SMTP(user='your email', password='SMTP authorization code', host='your email host')

    # 发送对象列表, 将报告发送到如下 邮箱， 请将your email 替换为你想要收到报告的邮箱
    email_to = ['your email']
    email_title = '贴吧自动签到报告'

    email_content = f"""
        本次签到成功{success_count}个, 失败{len(fail_dict)}个。
    """
    if len(fail_dict) > 0:
        email_content += create_sign_up_fail_list(fail_dict)
    else:
        email_content += "\n今天没有签到失败的，tql！"

    email_content += "\n\n祝心明眼亮！(｡･ω･｡)ﾉ♡"
    # 发送邮件
    yag_server.send(email_to, email_title, email_content)


# <tr><th>吧名</th><th>失败原因</th></tr>
def create_sign_up_fail_list(fail_dict: dict):
    title = "<h3>签到失败清单:</h3>"
    html_table = "<table style='border-collapse: collapse; border: 1px solid #ddd; text-align: left;'>"
    html_table += ("<tr><th style='border: 1px solid #ddd; padding: 8px;'>吧名</th><th style='border: 1px solid #ddd; "
                   "padding: 8px;'>失败原因</th></tr>")

    for bar_name, reason in fail_dict.items():
        html_table += (f"<tr><td style='border: 1px solid #ddd; padding: 8px;'>{bar_name}</td><td style='border: 1px "
                       f"solid #ddd; padding: 8px;'>{reason}</td></tr>")
    html_table += "</table>"
    return title + html_table
