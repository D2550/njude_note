import requests
import json


def auto_study(header, courseId):
    with open('get_class_info.txt', 'r') as f:
        # 读取文件并去除首尾特殊字符
        get_class_info = f.read().strip()
    # 替换courseId
    get_class_info = get_class_info.replace('foo', courseId)
    get_class_info_url = 'https://wsp.njude.com.cn/educationOA/graphql/SimpleResourceTree'
    CreateStudyLog_url = 'https://wsp.njude.com.cn/educationOA/graphql/CreateStudyLog'
    LearnResource_url = 'https://wsp.njude.com.cn/educationOA/graphql/LearnResource'
    study_session = requests.session()
    res = study_session.post(url=get_class_info_url, data=get_class_info, headers=header)
    class_info = json.loads(res.text)
    for i in class_info['data']['tree']['treeList']:
        status = i['resourceStudyStatus'] == 'FINISH'
        if i['resourceType'] == 'VIDEO' and (not status):
            print('[*] 尚未学习完成课程名称：' + i['name'] + '\t\t课程进度：' + str(i['progress']) + '\t\t课程id：' + str(
                i['id']))
            status = False
            while not status:
                with open('CreateStudyLog.txt', 'r') as f:
                    # 读取文件并去除首尾特殊字符
                    CreateStudyLog = f.read().strip()
                CreateStudyLog = CreateStudyLog.replace("foo", courseId)
                CreateStudyLog = CreateStudyLog.replace("bar", str(i['id']))
                study_session.post(url=CreateStudyLog_url, data=CreateStudyLog.encode('UTF-8'), headers=header)
                with open('LearnResource.txt', 'r') as f:
                    # 读取文件并去除首尾特殊字符
                    LearnResource = f.read().strip()
                LearnResource = LearnResource.replace("foo", courseId)
                LearnResource = LearnResource.replace("bar", str(i['id']))
                res = study_session.post(url=LearnResource_url, data=LearnResource, headers=header)
                resourceStudyStatus = json.loads(res.text)['data']['learnResource']['resourceStudyStatus']
                if resourceStudyStatus == 'FINISH':
                    status = True
                    print('[*] 自动学习完成课程名称：' + i['name'] + '\t\t课程id：' + str(i['id']))


if __name__ == "__main__":
    auto_study('a', 'a')
