import base64
import json
import requests
from bs4 import BeautifulSoup
import urllib.parse
import auto_study

if __name__ == "__main__":
    # for debug
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }
    print('[*] 南大自动刷课程序')
    # 用户登录部分，系统采用401基础认证,后续可以改为通过input输入
    stu_user_name = ''
    stu_user_password = ''
    Authorization = base64.b64encode(f'{stu_user_name}:{stu_user_password}'.encode()).decode('ascii')
    requests_header = {
        'Authorization': f'Basic {Authorization}'
    }
    # 获取这个学期的课程，当然也可以获取所有的课程
    home_page = 'https://www.njude.com.cn/mstudent'
    session = requests.session()
    resq = session.get(url=home_page, headers=requests_header)
    if resq.status_code == 200:
        print('[*] 登录成功')
        print('[*] 正在尝试解析课程')
        print('------------------------------')
        # 防止报错
        class_link = ''
        class_id = []
        soup = BeautifulSoup(resq.text, 'lxml')
        for class_name in soup.find_all('h4'):
            count = 0
            if 'no-margin' in str(class_name):
                count += 1
                for link in class_name.find_all('a'):
                    class_link = link.get('href')
                class_text = class_name.get_text()
                print(f'[*] {class_text}，课程链接: {class_link}')
                class_id.append(class_link[-4:])
        print('[*] 解析完成')
        print('------------------------------')
        print('[*] 正在尝试登录学习平台')
        # 这个地方存在越权登录
        step1_url = f'https://www.njude.com.cn{class_link}'
        session.get(url=step1_url, headers=requests_header)
        # 这个垃圾系统，Cookie根本没有用，全是基础认证
        Authorization = urllib.parse.unquote(session.cookies['ACCESS%5FTOKEN'])
        get_stu_info_url = 'https://wsp.njude.com.cn/educationOA/learn/v2/my/student_info'
        # 这个地方Basic变成Bearer了，要注意
        requests_header = {
            'Authorization': f'Bearer {Authorization}',
            'Content-Type': 'application/json',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0"

        }
        resq = session.get(url=get_stu_info_url, headers=requests_header, verify=False)
        stu_info = json.loads(resq.text)
        if stu_info['status'] == 'success':
            print('[*] 学习平台登录成功')
            for i in class_id:
                i = i.replace("=", '')
                auto_study.auto_study(requests_header, i)

