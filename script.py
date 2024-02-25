import random
import re
import time


import requests
import yagmail
from bs4 import BeautifulSoup

myCookies = {
    "Cookie": "MCITY=-104%3A; BAIDU_WISE_UID=wapp_1702228420445_268; ZD_ENTRY=bing; wise_device=0; USER_JUMP=-1; Hm_lvt_98b9d8c2fd6608d564bf2ac2ae642948=1708459074,1708845964; st_key_id=17; arialoadData=false; BAIDU_SSP_lcr=https://cn.bing.com/; ariawapForceOldFixed=false; IS_NEW_USER=c45bea22c73c12925965d0a5; 5494148441_FRSVideoUploadTip=1; video_bubble5494148441=1; ZFY=wapNp:BlIJcbXTmhuBn:BBakbQYlp0V7SrgKvGx9VyJa4:C; showCardBeforeSign=1; rpln_guide=1; BAIDUID=1B2C41F1CCCE1D3DCCA27A6C4AF69097:FG=1; BAIDUID_BFESS=1B2C41F1CCCE1D3DCCA27A6C4AF69097:FG=1; mo_originid=2; CLIENTWIDTH=375; CLIENTHEIGHT=667; XFI=96d2fd30-d3c2-11ee-a5c4-4f488bd9b7db; st_data=d958b2ed9fe47cfff9cf27cf553a7ae11ae2be97b11a101b21ac2974272b0a4fbeace7bec965c4b0a573fe25812824ce67d911ed2339b1378b4a6c269497148b444604678093320b1a2ea13ff9180c39de744d1f2e63f90bef1cb5849138922b875fb13df4ef09d0554775680f75265bb63fa6ad16feaaf0336bd5fc7bfa5ceb2d65d4613d78fb930b0b19c5e4835d46; st_sign=fde803af; XFCS=1A0991CC60DADC17C41A1F4F39E76E5FEF6414F3AC6B381EC21DD6A8A6868024; XFT=ZLAxPyLX+6HTxDiuxeXSL9m2ouFuLxW2Y90BIBUztPQ=; tb_as_data=9c5197d2dc558c5010005f07a999dc4942a7a201c11c80b6f7a80794d03df7aa63650d25831140c2bbd2f9251610c8dfa6cb06243dd81feab5caebfa2957d1fa780e4db6789c451bead9e50070b9307afca3b975ccb60039785c81fa11994f6ea172be69ffebe154b1d852455bc2b15b; Hm_lpvt_98b9d8c2fd6608d564bf2ac2ae642948=1708855919; ab_sr=1.0.1_ZjI4OTQwYTliOTA1OGUxNGIyM2MzZWNhMGMyNWM1NDg3YTI2Zjc3MWIxZGRkZjU0NmY2YTI5Yzg3M2M3OWQxMmQwYzQyMWZkMzBlNjMxYWY0NWY3ZWQ2YjYzMWRiZGUwM2JkYTEwNWNjNDBlMDRmY2YzMDQ4OWRiMjY4YTc4NDFmYzE1MGNiOGU1Zjc4ZWQ5MWVkZGZmZTdkMTA3Yzk4ZA==; BDUSS=5ucTdVbVRMeVM2SDUtWmdDTEhmfm5SM0RRdVZOTFZkWEZyMTN0TmJPdXhud0ptSVFBQUFBJCQAAAAAAQAAAAEAAABZDXpHwfK0-MHyy-HExQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALES22WxEttlY0; RT=\"z=1&dm=baidu.com&si=16f88d0e-9d9a-4335-9cf9-3b255f15bc89&ss=lt16riqs&sl=m&tt=2ko1&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=61cbp&ul=62pg0&hd=62pg9\"; STOKEN=17e02db3e4ceb34c9f190869c52b18171a075c9b020965d9690acb2ffa8e78cb"
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
    yag_server = yagmail.SMTP(user='wang.qi183@foxmail.com', password='mnjgpclqjxjydedg', host='smtp.qq.com')

    # 发送对象列表
    email_to = ['1835014947@qq.com']
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
