import requests
import re
import base64
import conf
import urllib.parse
import urllib3
import ssl
import time
from chaojiying_Python.chaojiying import indentify

class QiangPiao():
    def __init__(self):
        # 验证码所需要的url
        self.captcha_url='https://kyfw.12306.cn/passport/captcha/captcha-check' #验证码的url
        self.picture='https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&1545918226572&callback=jQuery19104163698370249691_1545918225148&_=1545918225149'
        self.cookie_post = "https://kyfw.12306.cn/otn/login/conf"
        urllib3.disable_warnings()  # 不显示警告信息
        ssl._create_default_https_context = ssl._create_unverified_context
        self.headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Content - Type':'application/x-www-form-urlencoded;charset=UTF-8'
        }
        self.check_picture='https://kyfw.12306.cn/passport/captcha/captcha-check?callback=jQuery19109030147633445205_1545923029059&answer={}&rand=sjrand&login_site=E&_=1545923029065'
        # 登陆所需要的url
        self.login_url = 'https://kyfw.12306.cn/passport/web/login'  # 登陆页面的url
        self.session = requests.session()
        data = self.session.get(self.cookie_post)#获取cookie
        self.tiket_buyer=conf.PASSNAME

    def get_position(self,index):
        '''
        验证码坐标
        :param index:
        :return:
        '''
        position = {
            "1": "37,50",
            "2": "109,50",
            "3": "173,50",
            "4": "250,50",
            "5": "37,116",
            "6": "109,116",
            "7": "173,116",
            "8": "250,116"
        }
        temp = []
        indexArr = index.split(",")
        for x in indexArr:
            temp.append(position.get(x))
        return  ",".join(temp)

    def check_captch(self):
        '''
        验证码
        :return:
        '''
        # index=input('请输入验证码：')
        # self.picture_data=self.get_position(index)
        self.picture_data=indentify()
        print(self.picture_data)
        print(type(self.picture_data))
        check_url=self.check_picture.format(self.picture_data)
        req=self.session.get(check_url,headers=self.headers).text
        print(req)
        result=re.findall(r'"result_message":"(.*?)"',req)
        print(result[0])
        if result[0] == '验证码校验失败':
            self.get_pic()
            self.check_captch()
        elif result[0] == '验证码校验成功':
            print('验证码验证成功')

    def get_pic(self):
        '''
        获取验证码图片
        :return:
        '''
        res =self.session.get(self.picture,headers=self.headers).text
        base64Pic = re.findall(r'"image":"(.*?)"', res)
        # base64转图片
        img2data = base64.b64decode(base64Pic[0])
        with open("./chaojiying_Python/yanzhengma.jpg", "wb") as  file:
            file.write(img2data)
            print('生成验证码成功')

    def login(self):
        #登陆
        data={
            'username': conf.username,
            'password': conf.password,
            'appid': 'otn',
            'answer': self.picture_data
        }
        resq=self.session.post(self.login_url,data,headers=self.headers).json()
        print(resq)
        print('类型{}'.format(type(resq)))
        if resq['result_message'] == '登录成功':
            data={'appid': 'otn'}
            prove=self.session.post('https://kyfw.12306.cn/passport/web/auth/uamtk',data=data).json()
            token=prove['newapptk']
            data={
                'tk':token
            }
            prove=self.session.post('https://kyfw.12306.cn/otn/uamauthclient',data).json()
            print(prove)
            self.session.get('https://kyfw.12306.cn/otn/login/userLogin')

        else:
            print('登陆失败')

    def station(self):
        url='https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        result=requests.get(url,headers=self.headers).text
        res=result.split('@')
        station_dict={}
        for i in res[1:]:
            name=i.split('|')
            station_dict[name[1]]=name[2]
        return station_dict

    def check_tikets(self,station):
        '''查询余票'''
        train_seat=''
        number = ''
        url='https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'
        print(conf.data_time,station[conf.FSTATION],station[conf.TSTATION])
        resq=self.session.get(url.format(conf.data_time,station[conf.FSTATION],station[conf.TSTATION]),headers=self.headers).json()
        result=resq['data']['result']
        print(result)
        for i in range(len(result)):
            train_info=result[i].split('|')
            print('*'*20,train_info[3])
            if train_info[3] in conf.TRAIN_NUM:
                print('+'*30,'执行了')
                print(train_info)
                train_num=train_info[3]
                if train_info[0] != '':
                    print('执行了'*20)
                    number=train_info[0]
                    print(number)
                    print('车次:{}'.format(train_info[3]))
                    print('商务特等座:{}'.format(train_info[32]))
                    print('一等座:{}'.format(train_info[31]))
                    print('二等座:{}'.format(train_info[30]))
                    if conf.SEAT == '一等座':
                        train_seat=train_info[31]
                    elif conf.SEAT == '二等座':
                        train_seat=train_info[30]
                        print('$'*20,train_seat)
                        if train_seat !='无' or train_seat != '*' or train_seat != '--' or train_seat != '':
                            break

        return number ,train_seat,train_num

    def login_confirm(self,number):
        '''
        确认登录状态
        :return:
        '''
        requests_url1='https://kyfw.12306.cn/otn/login/checkUser'
        data1={
            '_json_att':''
        }
        resq1=self.session.post(requests_url1,headers=self.headers,data=data1).json()
        print('确认用户登录状态request1:{}'.format(resq1))
        print(type(resq1))
        resq1=resq1['data']['flag']
        return resq1

    def commit_ticket_msg(self,number):
        requests_url2='https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data2={
            'back_train_date':conf.data_time,
            'purpose_codes': 'ADULT',
            'query_from_station_name':conf.FSTATION,
            'query_to_station_name':conf.TSTATION,
            'secretStr':urllib.parse.unquote(number),#注意此处提交数值的格式
            'tour_flag': 'dc',
            'train_date': conf.data_time,
            'undefined':''
        }
        resq2=self.session.post(requests_url2,data=data2,headers=self.headers)
        print('提交车票预定信息resquest2:{}'.format(resq2.text))
        return resq2.text

    def tiket_mesg_confirm(self):
        '''
        确认预定信息
        :return:
        '''
        requests_url3='https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data3={
            '_json_att': '',
        }
        html_token=self.session.post(requests_url3,data=data3,headers=self.headers).text
        strings=re.findall(r"globalRepeatSubmitToken = '(.*?)'",html_token)[0]
        print('确认预定信息requests3:{}'.format(strings))
        token = re.findall(r"var globalRepeatSubmitToken = '(.*?)';", html_token)[0]
        leftTicket = re.findall(r"'leftTicketStr':'(.*?)',", html_token)[0]
        key_check_isChange = re.findall(r"'key_check_isChange':'(.*?)',", html_token)[0]
        train_no = re.findall(r"'train_no':'(.*?)',", html_token)[0]
        stationTrainCode = re.findall(r"'station_train_code':'(.*?)',", html_token)[0]
        fromStationTelecode = re.findall(r"'from_station_telecode':'(.*?)',", html_token)[0]
        toStationTelecode = re.findall(r"'to_station_telecode':'(.*?)',", html_token)[0]
        date_temp = re.findall(r"'to_station_no':'.*?','train_date':'(.*?)',", html_token)[0]
        timeArray = time.strptime(date_temp, "%Y%m%d")
        timeStamp = int(time.mktime(timeArray))
        time_local = time.localtime(timeStamp)
        train_date_temp = time.strftime("%a %b %d %Y %H:%M:%S", time_local)
        train_date = train_date_temp + ' GMT+0800 (中国标准时间)'
        train_location = re.findall(r"tour_flag':'.*?','train_location':'(.*?)'", html_token)[0]
        purpose_codes = re.findall(r"'purpose_codes':'(.*?)',", html_token)[0]
        price_list = re.findall(r"'leftDetails':(.*?),'leftTicketStr", html_token)[0]
        return token,leftTicket,key_check_isChange,train_no,stationTrainCode,fromStationTelecode,toStationTelecode,date_temp,timeArray,timeStamp,timeStamp,train_date_temp,train_date,train_location,purpose_codes,strings

    def passgers_mesg(self,strings):
        '''
        获取乘客信息
        :param strings:
        :return:
        '''
        data4={
            '_json_att':'',
            'REPEAT_SUBMIT_TOKEN': strings
        }
        requests_url4='https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        resq4=self.session.post(requests_url4,data=data4,headers=self.headers)
        print('获取乘客信息requests4:{}'.format(resq4.json()))
        passengers = resq4.json()['data']['normal_passengers']
        print(passengers)
        print('\n')
        print('乘客信息列表:')
        for i in passengers:
            print(str(int(i['index_id']) + 1) + '号:' + i['passenger_name'] + ' ', end='')
        print('\n')
        return passengers

    def order_msg_confirm(self,strings,passengers):
        '''
        确认订单信息
        :param strings:
        :return:
        '''
        seat_dict = {'无座': '1', '硬座': '1', '硬卧': '3', '软卧': '4', '高级软卧': '6', '动卧': 'F', '二等座': 'O', '一等座': 'M',
                     '商务座': '9'}
        choose_type = seat_dict[conf.SEAT]
        pass_num = len(self.tiket_buyer.split(','))  # 购买的乘客数
        pass_list = self.tiket_buyer.split(',')
        pass_dict = []
        for i in pass_list:
            info = passengers[int(i) - 1]
            pass_name = info['passenger_name']  # 名字
            pass_id = info['passenger_id_no']  # 身份证号
            pass_phone = info['mobile_no']  # 手机号码
            pass_type = info['passenger_type']  # 证件类型
            dict = {
                'choose_type': choose_type,
                'pass_name': pass_name,
                'pass_id': pass_id,
                'pass_phone': pass_phone,
                'pass_type': pass_type
            }
            pass_dict.append(dict)
        num = 0
        TicketStr_list = []
        for i in pass_dict:
            if pass_num == 1:
                TicketStr = i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ',N'
                TicketStr_list.append(TicketStr)
            elif num == 0:
                TicketStr = i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ','
                TicketStr_list.append(TicketStr)
            elif num == pass_num - 1:
                TicketStr = 'N_' + i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ',N'
                TicketStr_list.append(TicketStr)
            else:
                TicketStr = 'N_' + i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ','
                TicketStr_list.append(TicketStr)
            num += 1
        passengerTicketStr = ''.join(TicketStr_list)
        print(passengerTicketStr)

        num = 0
        passengrStr_list = []
        for i in pass_dict:
            if pass_num == 1:
                passengerStr = i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ',1_'
                passengrStr_list.append(passengerStr)
            elif num == 0:
                passengerStr = i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ','
                passengrStr_list.append(passengerStr)
            elif num == pass_num - 1:
                passengerStr = '1_' + i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ',1_'
                passengrStr_list.append(passengerStr)
            else:
                passengerStr = '1_' + i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ','
                passengrStr_list.append(passengerStr)
            num += 1

        oldpassengerStr = ''.join(passengrStr_list)
        print(oldpassengerStr)
        requests_url5='https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data5={
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldpassengerStr,
            'tour_flag': 'dc',
            'randCode':'',
            'whatsSelect':'1',
            '_json_att':'',
            'REPEAT_SUBMIT_TOKEN': strings
        }
        resq5=self.session.post(requests_url5,headers=self.headers,data=data5).json()
        print('确认订单信息requests5:{}'.format(resq5))
        if resq5['status'] == True:
            print('检查订单信息成功!')
        else:
            print('检查订单信息失败!')
        return resq5,passengerTicketStr,oldpassengerStr

    def left_tikets(self,fromStationTelecode,leftTicket,token,stationTrainCode,toStationTelecode,train_date,train_location,train_no):
        requests_url6='https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        data6={
            '_json_att':'',
            'fromStationTelecode':fromStationTelecode,
            'leftTicket':leftTicket,
            'purpose_codes':'00',
            'REPEAT_SUBMIT_TOKEN': token,
            'seatType':'O',
            'stationTrainCode':stationTrainCode,
            'toStationTelecode':toStationTelecode,
            'train_date':train_date,
            'train_location':train_location,
            'train_no':train_no
        }
        print(data6)
        resq6=self.session.post(requests_url6,headers=self.headers,data=data6)
        print('查询余票requests6:{}'.format(resq6.text))
        return resq6

    def order_requst(self,key_check_isChange,leftTicket,train_location,token,passengerTicketStr,oldpassengerStr):
        '''
        提交订单
        :param key_check_isChange:
        :param leftTicket:
        :param train_location:
        :param token:
        :return:
        '''
        requests_url7='https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data7={
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr':oldpassengerStr,
            'randCode':'',
            'purpose_codes':'00',
            'key_check_isChange':key_check_isChange,
            'leftTicketStr':leftTicket,
            'train_location':train_location,
            'choose_seats':'',
            'seatDetailType':'000',
            'whatsSelect':'1',
            'roomType':'00',
            'dwAll':'N',
            '_json_att':'',
            'REPEAT_SUBMIT_TOKEN':token
        }
        resq7=self.session.post(requests_url7,headers=self.headers,data=data7).text
        print('发送订单请求requests7:{}'.format(resq7))
        return resq7

    def order_quen(self,token):
        '''
        查询预定结果
        :param token:
        :return:
        '''
        random_data=int(time.time()*1000)
        requests_url8='https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random={}&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN={}'
        resq8=self.session.get(requests_url8.format(random_data,token),headers=self.headers)
        print('查询排队人数requests_url8:{}'.format(resq8.text))

        random_data2=int(time.time()*1000)
        requests_url9='https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random={}&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN={}'
        resq9=self.session.get(requests_url9.format(random_data2,token),headers=self.headers)
        print('查询排队人数requests_url8:{}'.format(resq8.text))


    def run(self):
        station=self.station()
        resq1=False
        while resq1 == False:
            self.get_pic()
            self.check_captch()
            self.login()
            number,train_seat,train_num=self.check_tikets(station)
            while train_seat =='无' or train_seat == '*' or train_seat == '--' or train_seat == '' :
                print(train_seat)
                print('查询序列号是{}'.format(number))
                number, train_seat, train_num = self.check_tikets(station)
                print('有票的车次{}'.format(train_num))
                time.sleep(4)
            resq1=self.login_confirm(number)
            if resq1==False:
                print('登陆失败，请重新输入验证码')
        resq2=self.commit_ticket_msg(number)
        token,leftTicket,key_check_isChange,train_no,stationTrainCode,fromStationTelecode,toStationTelecode,date_temp,timeArray,timeStamp,timeStamp,train_date_temp,train_date,train_location,purpose_codes,strings=self.tiket_mesg_confirm()
        passengers=self.passgers_mesg(strings)
        resq5,passengerTicketStr,oldpassengerStr=self.order_msg_confirm(strings,passengers)
        resq6=self.left_tikets(fromStationTelecode,leftTicket,token,stationTrainCode,toStationTelecode,train_date,train_location,train_no)
        resq7=self.order_requst(key_check_isChange,leftTicket,train_location,token,passengerTicketStr,oldpassengerStr)
        self.order_quen(token)

if __name__ == '__main__':
    qiangpiao=QiangPiao()
    qiangpiao.run()