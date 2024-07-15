import requests
import json
import re
import time
from time import sleep
from datetime import datetime, timedelta
import os


def login(username, password):

    # 发送GET请求以获取网站的Cookie
    data={
        'm':'login',
        'ueserLoginId': username,
        'pwd': password,
        'rememberPwd':'on'
        }

    response = requests.post('https://pm.bdo.com.cn/AuditSystem/bdologin.do?m=login',data = data)
    
    # 获取到userID ---------------------------------
    html_content = response.text

    # 使用正则表达式匹配sys_userId的值
    pattern = r'sys_userId\s*=\s*\'(\w+)\''
    match = re.search(pattern, html_content)
    sys_userId = 0
    if match:
        sys_userId = match.group(1)
        print("sys_userId: ", sys_userId)
    else:
        print("未找到sys_userId变量")
    # ----------------------------------------------
    
    # 获取响应中的Cookie
    cookies = response.cookies

    cookie_dict = {cookie.name: cookie.value for cookie in cookies}

    cookie = ""
    for key, value in cookie_dict.items():
        cookie += f"{key}={value}; "
    cookie = cookie.rstrip(', ')

    return cookie, sys_userId

def addMemberTimesReport(cookie,data):

    # 设置目标URL和要发送的数据
    url = 'https://pm.bdo.com.cn/AuditSystem/projectsystem/MemberSchedule.addMemberTimesReport.json'

    headers = {'Cookie': cookie,
               'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"} 

    # POST数据，以字典形式提供
    data = {
        'param1': data['start_date'],
        'param2': data['end_date'],
        'param3': data['start_time'],
        'param4': data['end_time'],
        'param5': data['project_id'],
        'param6': data['work_type'],
        'param7': data['work_content'],
        'param8': data['usrId'],
        'menuId': data['menu_id'],
    }

    # 发送POST请求，并包括Cookie
    response = requests.post(url, data=data, headers=headers)

    # 检查响应
    data = json.loads(response.text)['resultInfo']['statusText']
    if data == None: 
        data = '提交成功'
    
    print("提交结果：", data)  # 显示错误信息

def last_project(cookie, usrId):

    # 设置目标URL和要发送的数据
    url = 'https://pm.bdo.com.cn/AuditSystem/projectsystem/Combo.findProjectByUser2Years.json'  # 

    headers = {'Cookie': cookie,
               'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"} 

    data = {
        '_dc': 1697276108491,
        'blank': 0,
        'param1': usrId,
        'page': 1,
        'start': 0,
        'limit': 1000
    }
    # 发送Get请求，并包括Cookie
    response = requests.get(url,data=data, headers=headers)

    data = json.loads(response.text)
    print("最新的项目：",data['data'][-1])
    return data['data'][-1]['value']

def last_project_name(cookie, usrId):

    # 设置目标URL和要发送的数据
    url = 'https://pm.bdo.com.cn/AuditSystem/projectsystem/Combo.findProjectByUser2Years.json'  # 

    headers = {'Cookie': cookie,
               'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"} 

    data = {
        '_dc': 1697276108491,
        'blank': 0,
        'param1': usrId,
        'page': 1,
        'start': 0,
        'limit': 1000
    }
    # 发送Get请求，并包括Cookie
    response = requests.get(url, data=data, headers=headers)

    data = json.loads(response.text)
    print("最新的项目：",data['data'][-1])
    return data['data'][-1]['label']

def independence_submit(cookie, usrId, project_Id):

    headers = {'Cookie': cookie,
               'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"} 

    findIndependence_url = 'https://pm.bdo.com.cn/AuditSystem/projectsystem/Independence.findIndependence.json'

    saveOrSubmit_url = 'https://pm.bdo.com.cn/AuditSystem/projectsystem/Independence.saveOrSubmit.json'

    findIndependence_data = {
    'param1': project_Id,
    'param2': usrId,    # usrId
    'menuId': 10000668 
    }
    response = requests.post(findIndependence_url, data=findIndependence_data, headers=headers)
    if 'independenceId' in json.loads(response.text)['data'][0]:
        independence_Id = json.loads(response.text)['data'][0]['independenceId']
        saveOrSubmit_data = {
        'param1': independence_Id,
        'param2': 0,
        'jsonData': {},
        'menuId': 10000668
        }
        response = requests.post(saveOrSubmit_url, data=saveOrSubmit_data, headers=headers)
        print(response.text)
        print('当前项目的独立性声明提交成功。')
    else:
        print('当前项目独立性声明已经提交过了。')

def last_report_date(cookie, usrId):

    headers = { 'Cookie': cookie,
               'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
    data = {
        '_dc': time.time(), # 时间戳
        'menuId': '10000668',
        'sqlId': 'S000126',
        'param1': usrId,
        'param2': '1901-01-01',
        'param3': datetime.now().strftime('%Y-%m-%d'),
        'page': 1,
        'start': 0,
        'limit': 99999
    }
    url = 'https://pm.bdo.com.cn/AuditSystem/projectsystem/General.json?_dc={_dc}&menuId={menuId}&sqlId={sqlId}&param1={param1}&param2={param2}&param3={param3}&page={page}&start={start}&limit={limit}'.format(**data)
    response = requests.get(url, headers=headers)

    # 打印最近的上报工时记录
    # print(json.loads(response.text)['data'][-1])
    
    workdate = '1901-01-01'
    endTime = '00:00'
    for report in json.loads(response.text)['data']:
        if report['workDate'] > workdate:
            workdate = report['workDate']
            endTime = report['endTime']
        elif report['workDate'] == workdate:
            if report['endTime'] > endTime:
                endTime = report['endTime']
    print(workdate, endTime)
    return workdate, endTime

def main(cookie, usrId):

    project_id = last_project(cookie, usrId)
    sleep(1)
    independence_submit(cookie,usrId, project_id)
    sleep(1)
    data = {
                'start_date': '',
                'end_date': '',
                'start_time': '09:00',
                'end_time': '',
                'project_id': '',
                'work_type': '市外工作',
                'work_content': '',
                'usrId': usrId, 
                'menu_id': '10000668',
            }
    data['project_id'] = project_id

    last_rpt_date = last_report_date(cookie, usrId)[0]
    sleep(1)
    last_rpt_time = last_report_date(cookie, usrId)[1]
    sleep(1)
    last_monday = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')

    today = datetime.now().strftime('%Y-%m-%d')

    now = (datetime.now() - timedelta(minutes=datetime.now().minute % 10)).strftime('%H:%M')

    if last_rpt_date < last_monday:
        data['start_date'] = last_monday
        data['end_date'] = today

        data['start_time'] = '09:00'
        data['end_time'] = '18:00'
        print(data)

        addMemberTimesReport(cookie, data)

    else:

        if last_rpt_time < '18:00':

            data['start_time'] = last_rpt_time
            data['end_time'] = '18:00'

            data['start_date'] = last_rpt_date
            data['end_date'] = today

            print(data)
            addMemberTimesReport(cookie, data)
        
        elif last_rpt_time >= '18:00' and last_rpt_date < today:

            data['start_date'] = (datetime.strptime(last_rpt_date,'%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            data['end_date'] = today
            
            data['start_time'] = '09:00'
            data['end_time'] = '18:00'

            print(data)
            addMemberTimesReport(cookie, data)
        
        else:
            print('今天已经提交过了。')
    return data

def ServerPush(sendkey,info):
    title,content = info
    api = f"https://sc.ftqq.com/{sendkey}.send"
    data = {
        "text": title,
        "desp": content
    }
    print(content)
    requests.post(api, data=data)
    



if __name__ == '__main__':
    username = os.environ['username']
    password = os.environ['password']
    sendkey = os.environ['sendkey']
    print(username, password)
    cookie, sys_userId = login(username, password)
    sleep(1)
    data = main(cookie, sys_userId)
    sleep(1)
    project_name = last_project_name(cookie, sys_userId)
    sleep(1)
    info = [
          f"{data['start_date']} {data['start_time']}-{data['end_date']} {data['end_time']} \n \
            工作类型:{data['work_type']} \n \
            工作项目：{project_name}",
        ""
    ]
    ServerPush(sendkey,info)

