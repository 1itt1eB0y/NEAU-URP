#! py -3.5
#-*- coding:utf-8 -*-
from __future__ import print_function
from random import sample
from requests import get, post, session
from requests.exceptions import Timeout, ReadTimeout, ConnectionError
from re import compile
from os import remove, mkdir
from os.path import isfile, exists

CONNECTION_TIME_OUT = 5
READ_TIME_OUT = 10

file_dir = './export/'
kb_File = file_dir + '选课结果.html'
yzm_File = file_dir + 'yzm.jpg'
cjb_File = file_dir + '成绩总表.html'
bjg_File = file_dir + '不及格成绩总表.html'
css_File = file_dir + 'project.css'

vpn_url = 'http://vpn.neau.edu.cn/do-login/'

lg_in = 'loginAction.do'
lg_out = 'logout.do'

xk = 'xkAction.do'
tk = 'xkAction.do?actionType=10&kcId='
kb = 'xkAction.do?actionType=6'
cj = 'gradeLnAllAction.do?type=ln&oper=qbinfo'
bjgcj = 'gradeLnAllAction.do?type=ln&oper=bjg'

name = 'menu/top.jsp'
yzm = 'validateCodeAction.do'
css = 'css/newcss/project.css'


proxy = {
    "http": "http://127.0.0.1:8080"
}
url_port = ['',
            'http://jws1.vpn.neau.edu.cn/',
            'http://jws2.vpn.neau.edu.cn/',
            'http://jws3.vpn.neau.edu.cn/',
            'http://jws4.vpn.neau.edu.cn/',
            'http://jwt1.vpn.neau.edu.cn/',
            'http://jwt2.vpn.neau.edu.cn/',
            'http://jwt3.vpn.neau.edu.cn/'
            ]
header = {
    'Accept': 'image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, */*',
    'Accept-Language': 'zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3',
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Encoding': 'gzip, deflate'
}
login_params = {
    "zjh1": "",
    "tips": "",
    "lx": "",
    "evalue": "",
    "eflag": "",
    "fs": "",
    "dzslh": "",
    "zjh": "",
    "mm": "",
    "v_yzm": "0"
}
vpn_params = {
    'auth_type': 'local',
    'username': '',
    'sms_code': '',
    'password': '',
    'captcha': '',
    'needCaptcha': 'false'
    # 'captcha_id': 'pnNauNa3WE6uG07'
}


def setCookie(ori_cookie):
    cookie_tmp = session()
    for key, value in ori_cookie.items():
        cookie_tmp.cookies.set(key, value)
    return cookie_tmp.cookies


def randomSession(x):
    return ''.join(sample('1234567890zyxwvutsrqponmlkjihgfedcbaABCDEFGHIGKLMOPQRSTUVWXYZ', x))


def file_write(fname, content, mode='w', if_print=1):
    with open(fname, mode) as f:
        f.write(content)
    if if_print == 1:
        print('\n  ' + fname + '已生成！\n')


def filter_str(cont, exp):
    pattern = compile(exp)
    result = pattern.findall(cont)


def POST(url, cookie, debug, data={}):
    if(debug == 1):
        return post(url, headers=header, data=data, cookies=cookie, timeout=(CONNECTION_TIME_OUT, READ_TIME_OUT), proxies=proxy)
    else:
        return post(url, headers=header, data=data, cookies=cookie, timeout=(CONNECTION_TIME_OUT, READ_TIME_OUT))


def GET(url, cookie, debug, data={}):
    if(debug == 1):
        return get(url, headers=header, data=data, cookies=cookie, timeout=(CONNECTION_TIME_OUT, READ_TIME_OUT), proxies=proxy)
    else:
        return get(url, headers=header, data=data, cookies=cookie, timeout=(CONNECTION_TIME_OUT, READ_TIME_OUT))


def port1():
    choice = input(
        '选择端口：\n1.jws1学生入口1\n2.jws2学生入口2\n3.jws3学生入口3\n4.jws4学生入口4\n\n5.jwt1教师入口1\n6.jwt2教师入口2\n7.jwt3教师入口3\n\n请输入序号：')
    return url_port[int(choice)]


def port2(choice):
    return url_port[int(choice)]


def get_yzm(debug=0):
    try:
        response = GET(url_selected + yzm, cookie, debug)
        print('\n    【验证码】获取成功！\n')
        file_write(yzm_File, response.content, 'wb', 0)
        login_params['v_yzm'] = input("请打开yzm.jpg查看并输入验证码【如看不清或未成功获取请输入0】：")
        if exists(yzm_File):
            remove(yzm_File)
        return 1
    except Timeout or ConnectionError or ReadTimeout:
        print('    【验证码】 请求超时！请重试或更换端口！')
        return 0


def get_css(debug=0):
    try:
        response = GET(url_selected + css, cookie, debug)
        file_write(css_File, response.text)
    except Timeout or ConnectionError or ReadTimeout:
        print('    【CSS】请求超时！用于输出网页带表格格式，非必要组件，可登陆后重试！')


def name_check(debug=0):
    try:
        response = GET(url_selected + name, cookie, debug)
        pattern = compile(r'当前用户:(.*)\)')
        result = pattern.findall(response.text)
        if(result):
            print('\n    当前用户：'+result[0]+')  ')
            return '当前用户：'+result[0]+')'
    except Timeout or ConnectionError or ReadTimeout:
        print('\n     【账户校验】请求超时！请重试或更换端口！')


def kyl(cont):
    pattern = compile(r'(<td.*>.*\n\t\t[0-9]*</td>)')
    result = pattern.findall(cont)
    # print(result)
    i = 0
    while i < len(result):
        print('  课序号：', end='')
        print(
            ((compile(r'<td.*>.*\n\t\t([0-9]*)</td>')).findall(result[i]))[0])
        print('  课余量：', end='')
        print(
            ((compile(r'<td.*>.*\n\t\t([0-9]*)</td>')).findall(result[i+1]))[0])
        i += 2


def xkjg(cont):
    pattern = compile(r'<strong><font color="#990000">(.*)</font></strong>')
    result = pattern.findall(cont)
    # print(result)
    if(result):
        return '  选/退课结果：' + result[0]
    else:
        return '  请检查代码是否出错！'


def valid(debug=0):
    try:
        response = GET(url_selected + kb, cookie, debug)
        print('      课表核对结果：', end='')
        print(bool((response.text.find(kcId)) > 0))
        return bool(response.text.find(kcId) > 0)
        # with open(kb_File, 'w') as f:
        # 	f.write(response.text)
        # f.write(response.text.replace('charset=GBK', 'charset
    except Timeout or ConnectionError or ReadTimeout:
        print('\n     【课表】请求超时！请重试或更换端口！\n')


def tk_do(debug=0):
    try:
        response = GET(url_selected + tk + kcId, cookie, debug)
        print(response.status_code)
        if (response.status_code == 200):
            print('\n  退课已执行！')
            print(xkjg(response.text))
            valid()
        else:
            print('\n  连接失败！')
    except Timeout or ConnectionError or ReadTimeout:
        print('\n     【退课】请求超时！请重试或更换端口！\n')


def kb_do(debug=0):
    try:
        response = GET(url_selected + kb, cookie, debug)
        file_write(kb_File, response.text.replace(
            '/css/newcss/project.css', './project.css'))
    except Timeout or ConnectionError or ReadTimeout:
        print('\n     【课表】请求超时！请重试或更换端口！\n')


def cj_do(debug=0):
    try:
        response = GET(url_selected + cj, cookie, debug)
        file_write(cjb_File, response.text.replace(
            '/css/newcss/project.css', './project.css'))
        response = GET(url_selected + bjgcj, cookie, debug)
        file_write(bjg_File, response.text.replace(
            '/css/newcss/project.css', './project.css'))
    except Timeout or ConnectionError or ReadTimeout:
        print('\n     【成绩总表】请求超时！请重试或更换端口！\n')


def login(cookie, debug=0):
    jwc_password = input('请输入教务处密码：')
    login_params['zjh'] = jwc_username
    login_params['mm'] = jwc_password
    if not get_yzm(debug) or login_params['v_yzm'] == '0':
        count = 1
        while login_params['v_yzm'] == '0':
            print('\n正在第 %d 次重新获取验证码...' % count)
            if get_yzm(debug):
                count = 0
            count += 1
            if(count > 4):
                print('\n已经连续 5 次无法成功获取读取验证码！\n')
                return 0
    for i in range(3):
        try:
            response = POST(url_selected + lg_in, cookie, debug, login_params)
            # print(len(response.text))  8289  484
            # success:content-lenth = 491  fail:~~content-lenth~~
            if len(response.text) > 1000:
                print('\n登录失败！请检查账号密码或验证码是否输入错误！')
                return 0
            else:
                print('\n登录成功！开始执行！\n')
                return 1
        except Timeout or ConnectionError or ReadTimeout:
            print('\n    【教务处登录】 请求超时！正在重试！\n')

    print('【教务处登录】重试 3 次超时！请尝试更换端口！（头铁可以继续）')


def logout(cookie, debug=0):
    try:
        response = GET(url_selected + lg_out, cookie, debug)
        if(response.status_code == 200):
            print('\n已经登出当前账号！\n')
    except Timeout or ConnectionError or ReadTimeout:
        print('\n    【教务处登出】 请求超时！请重试或更换端口！\n')


def vpn(debug=0):
    global cookie
    vpn_params['username'] = input('请输入VPN账号：')
    vpn_params['password'] = input('请输入VPN密码：')
    try:
        response = POST(vpn_url, cookie, debug,  vpn_params)
        # print(response.headers['Set-Cookie'])
        if response.headers['Content-Length'] != '35':
            print('\nVPN登录失败！请检查账号密码或验证码是否输入错误！\n')
            return 0
        else:
            pattern = compile(r'cn=(.*); P')
            result = pattern.findall(response.headers['Set-Cookie'])
            cookie = setCookie(
                {"wengine_vpn_ticketvpn_neau_edu_cn": result[0]})
            # print(cookie.items())
            print('\nVPN登录成功！')
            return 1
    except Timeout or ConnectionError or ReadTimeout:
        print('\n    【VPN登录】 请求超时！请重试或更换端口！\n')

if __name__ == '__main__':
    if exists(file_dir):
        if isfile(file_dir):
            mkdir(file_dir)
    else:
        mkdir(file_dir)
    debug_mode = int(input("127.0.0.1:8080代理模式(0/1)【不清楚有什么用的请选0】："))
    # debug_mode = 1
    vpncookie = {"wengine_vpn_ticketvpn_neau_edu_cn": randomSession(25)}
    cookie = setCookie(vpncookie)
    vpncl = -1
    vpn_tries = 0
    jwc_tries = 0
    while(vpncl):
        if(vpn_tries >= 3):
            print(
                '\n警告：VPN已连续 3 次尝试失败，为防止账户被封锁（连续五次登陆失败），脚本即将退出！\n为防止账户被锁，请仔细核对密码后！\n')
            break
        vpn_tries += 1
        if vpn(debug_mode) == 1:
            tmp = setCookie({"JSESSIONID": randomSession(16)})
            cookie.update(tmp)
            vpn_tries = 0
            print('\n当前账户cookie：', cookie.items(), end='\n\n')
            url_selected = port2(7)
            while vpncl:
                if vpncl == -1:
                    url_selected = port1()
                    vpncl = 1
                if(jwc_tries >= 5):
                    print('\n教务处账号已连续 5 次尝试错误，请仔细核对后重新尝试！\n')
                    break
                jwc_username = input('请输入教务处账号：')
                if(login(cookie, debug_mode)):
                    get_css(debug_mode)
                    print('===================================')
                    usr_tries = 1
                    usrname = None
                    while(usrname == None):
                        print('正在尝试第 %d 次用户名校验...' % usr_tries)
                        usrname = name_check(debug_mode)
                        usr_tries += 1
                        if usr_tries == 5:
                            print("你这网也太差了吧……登录上了读不到用户名？？？")
                    print(
                        '\n注意cookie有效时间！\n建议每10分钟左右执行一次名字校验，如无返回结果，则证明cookie已过期，需退出当前账号重新登录！')
                    jwc_tries = 0
                    choose = 1
                    while(choose):

                        print('===================================')
                        print('%s\n' % usrname)
                        print('1、选课  2、退课  3、查课表  4、成绩总表')
                        print('5、抢课模式  6、名字校验（刷新cookie有效期）')
                        print('7、重新获取CSS')
                        print('0、教务系统账号（退出后可更换端口）')
                        choose = int(input('\n请输入选项：'))

                        if choose == 1 or choose == 2 or choose == 5:
                            kcId = input("请输入课程号：")
                            if choose == 1 or choose == 5:
                                lkId = '_'
                                kxId = input("请输入课序号：")
                                xkcx_params['kch'] = kcId
                                xkcx_params['cxkxh'] = kxId
                                xkqr_params["kcId"] = kcId + lkId + kxId
                                if choose == 1:
                                    print('\n【选课模式】功能不公开提供！\n')
                                else:
                                    print('\n【抢课模式】功能不公开提供！\n')
                            elif choose == 2:
                                tk_do(debug_mode)
                            print('\n请登录教务处核对课表！')
                        elif choose == 3:
                            kb_do(debug_mode)
                            print('\n请以教务处课表为准！')
                        elif choose == 4:
                            cj_do(debug_mode)
                            print('\n请以教务处成绩表为准！')
                        elif choose == 6:
                            if usrname == None:
                                usrname = name_check(debug_mode)
                            else:
                                name_check(debug_mode)
                        elif choose == 7:
                            get_css(debug_mode)
                        print(' \n执行完毕！')
                        print('***********************************')
                    logout(cookie, debug_mode)
                    print('-----------------------------------')
                print('当前账号%s已登出/停止尝试，是否继续处理其他账号？' % (jwc_username))
                vpncl = int(input('(0 退出/ 1 处理其他账号/ -1 更换端口)\n'))
    print('选课脚本已退出！感谢您的支持与使用！\n')
    print('如有任何修改建议或bug反馈请发送至：a17github@126.com 或 https://github.com/adobe17/NEAU-URP 的issue处提出')
    input('Press AnyKey to Exit...')
