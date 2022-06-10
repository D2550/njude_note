import base64
import json

import requests
from bs4 import BeautifulSoup
import urllib.parse

if __name__ == "__main__":
    # for debug
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }
    print('[*] 南大自动刷课程序')
    # 用户登录部分，系统采用401基础认证,后续可以改为通过input输入
    stu_user_name = '22030111344'
    stu_user_password = 'kyjae6mc'
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


            def auto_study(header, courseId):
                get_class_info = '{"operationName":"SimpleResourceTree","variables":{"courseId":' + str(
                    courseId) + '},"query":"query SimpleResourceTree($courseId: BigInt!) {\\n  tree(input: {courseId: ' \
                                '$courseId}) {\\n    treeList {\\n      id\\n      name\\n      isGroup\\n      ' \
                                'progress\\n      resourceType\\n      level\\n      resourceStudyStatus\\n    }\\n   ' \
                                ' __typename\\n  }\\n}"} '
                get_class_info_url = 'https://wsp.njude.com.cn/educationOA/graphql/SimpleResourceTree'
                study_log_url = 'https://wsp.njude.com.cn/educationOA/graphql/CreateStudyLog'
                study_progress_url = 'https://wsp.njude.com.cn/educationOA/graphql/LearnResource'
                new_session = requests.session()
                res = new_session.post(url=get_class_info_url, data=get_class_info, headers=header)
                print(res.text)
                class_info = json.loads(res.text)
                # 貌似只有视频影响总进度，如果不是的话再改改
                for k in class_info['data']['tree']['treeList']:
                    status = k['resourceStudyStatus'] == 'FINISH'
                    if k['resourceType'] == 'VIDEO' and (not status):
                        print('[*] 尚未学习完成课程名称：' + k['name'] + '\t\t课程进度：' + str(k['progress']) + '\t\t课程id：' + str(
                            k['id']))
                        status = False
                        while not status:
                            post_data = (
                                    '''{"operationName":"CreateStudyLog","variables":{"input":{"app":"学习平台-WEB",
                                    "courseId":''' + str(
                                courseId) + ''',"action":"PLAY","resourceId":''' + str(k[
                                                                                           'id']) + ''',"value":1,
                                                                                           "currentTime":59.976358}},
                                                                                           "query":"mutation 
                                                                                           CreateStudyLog($input: 
                                                                                           StudyActionLogInputObject) 
                                                                                           {\\n  createStudyLog(
                                                                                           input: $input) {\\n    
                                                                                           studyLog {\\n      id\\n   
                                                                                              __typename\\n    }\\n   
                                                                                               __typename\\n  
                                                                                               }\\n}"}''').encode(
                                'UTF-8')
                            new_session.post(url=study_log_url, data=post_data, headers=header)
                            post_data = '''{ "operationName": "LearnResource", "variables": { "input": { "courseId":''' + str(
                                courseId) + ''', "resourceId": ''' + str(k[
                                                                             'id']) + '''} }, "query": "query 
                                                                             LearnResource($input: 
                                                                             LearnResourceInput!) {\\n  
                                                                             learnResource(input: $input) {\\n    
                                                                             id\\n    name\\n    resourceType\\n    
                                                                             content\\n    progress\\n    
                                                                             resourceStudyStatus\\n    preResource {
                                                                             \\n      id\\n      name\\n      
                                                                             __typename\\n    }\\n    nextResource {
                                                                             \\n      id\\n      name\\n      
                                                                             __typename\\n    }\\n    
                                                                             ...LiveResource\\n    ...FileResource\\n 
                                                                                ...MediaResource\\n    __typename\\n  
                                                                                }\\n}\\n\\nfragment LiveResource on 
                                                                                Resource {\\n  id\\n  startTime\\n  
                                                                                endTime\\n  relatedSectionId\\n  
                                                                                playbackVideoUrl\\n  canPlayback\\n  
                                                                                picture\\n  url\\n  studyStatus\\n  
                                                                                __typename\\n}\\n\\nfragment 
                                                                                FileResource on Resource {\\n  id\\n  
                                                                                name\\n  format\\n  url\\n  size\\n  
                                                                                downloadQuantity\\n  resourceType\\n  
                                                                                exerciseGroupId\\n  
                                                                                __typename\\n}\\n\\nfragment 
                                                                                MediaResource on Resource {\\n  id\\n 
                                                                                 url\\n  currentTime\\n  
                                                                                 __typename\\n}" } '''
                            res = new_session.post(url=study_progress_url, data=post_data, headers=header)
                            resourceStudyStatus = json.loads(res.text)['data']['learnResource']['resourceStudyStatus']
                            if resourceStudyStatus == 'FINISH':
                                status = True
                        print('[*] 自动学习完成课程名称：' + k['name'] + '\t\t课程id：' + str(
                            k['id']))


            # auto_study(requests_header, 4378)  # 改这个id就行
            for i in class_id:
                auto_study(requests_header, i)
