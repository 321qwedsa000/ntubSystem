import requests
from bs4 import BeautifulSoup
import re
from enum import Enum
from datetime import datetime
import xml.etree.ElementTree as ET


class NtubLoginFailedException(Exception):
    def __init__(self,message):
        super(NtubLoginFailedException,self).__init__(message)

class LeaveSubmitMode(Enum):
    SUBMIT = "送出"
    SAVE_BUT_NOT_SUBMIT="儲存尚未送出"
'''
"AA"=公假
"AB"=喪假
"AC"=事假
"AD"=病假
"AF"=產前假
"AI"=分娩假
"AJ"=流產假
"AK"=陪產假
"AL"=公假(不)
"AM"=重大傷病(不)
"AN"=停班停課
"AO"=防疫假'
'''
class LeaveReason(Enum):
    OFFICIAL="AA"
    FUNERAL="AB"
    PERSONAL="AC"
    SICK="AD"
    PREMATERNITY="AF"
    MATERNITY="AI"	
    MISCARRIAGE="AJ"
    PATERNITY="AK"
    SERIOUSINJURE="AM"
    EPIDEMIC_PREVENTATION="AO"

class NtubLoginSystem:
    def __search_Asp_Utils(self,url,dic):
        response = self.session.get(url)
        if response.status_code == 404:
            raise NtubLoginFailedException("No Internet Connection")
        try:
            soup = BeautifulSoup(response.content,features='lxml')
        except:
            soup = BeautifulSoup(response.content,features='html.parser')
        dic['__VIEWSTATE'] = soup.select_one('#__VIEWSTATE')['value'] if soup.select_one('#__VIEWSTATE') != None else ''
        dic['__VIEWSTATEGENERATOR'] = soup.select_one('#__VIEWSTATEGENERATOR')['value'] if soup.select_one('#__VIEWSTATEGENERATOR') != None else ''
        dic['__EVENTVALIDATION'] = soup.select_one('#__EVENTVALIDATION')['value'] if soup.select_one('#__EVENTVALIDATION') != None else ''

    def __init__(self,username:str,password:str):
        #####################
        # Ntub Related URLS #
        #####################
        self.LOGIN_URL = "http://ntcbadm1.ntub.edu.tw/login.aspx?Type=0" #POST url
        self.CURRICULUM_URL = "http://ntcbadm1.ntub.edu.tw/STDWEB/Sel_Student.aspx" #GET url
        self.MIDTERM_URL = "http://ntcbadm1.ntub.edu.tw/ACAD/STDWEB/GRD_GRDMQry.aspx" #POST url
        self.SCORE_URL = "http://ntcbadm1.ntub.edu.tw/ACAD/STDWEB/GRD_GRDQry.aspx" #POST url
        self.LEAVE_URL = "http://ntcbadm1.ntub.edu.tw/StdAff/STDWeb/ABS0101Add.aspx" #POST url
        self.CHANGEPWD_URL = "http://ntcbadm1.ntub.edu.tw/STDWEB/STD_PwdChange.aspx" #POST url
        self.LESSON_URL = "http://ntcbadm1.ntub.edu.tw/HttpRequest/SELChooseHttpXML.aspx" #POST URL
        ###################
        # Login into NTUB #
        ###################
        #
        self.session = requests.Session()
        loginData = {
            'UserID':username,
            'PWD':password,
            'loginbtn':''
        }
        self.__search_Asp_Utils(self.LOGIN_URL,loginData)
        self._password = password
        loginResponse = self.session.post(self.LOGIN_URL,data=loginData)
        if loginResponse.text.startswith('<script>'):
            raise NtubLoginFailedException(f'Login {username} failed')
        self._cookies = loginResponse.cookies
        try:
            soup = BeautifulSoup(loginResponse.text,'lxml')
        except:
            soup = BeautifulSoup(loginResponse.text,'html.parser')
        self._classname = soup.find('span',{'id':'ClassName'}).text
        self._stdno = soup.find('span',{'id':'StdNo'}).text
        self._name = soup.find('span',{'id':'Name'}).text
        #
    @property
    def cookies(self):
        return self._cookies
    @property
    def password(self):
        return self._password
    @property
    def className(self):
        return self._classname
    @property
    def studentNumber(self):
        return self._stdno
    @property
    def name(self):
        return self._name
    def parse_lessons(self,day,section): #901 , 400
        submit_dict = {
            "ModuleName": 'QueryCurData',
            "EduNo": 4,
            "Desire": '',
            "DeptNo": 400,
            "Grade": '',
            "Week": day,
            "Section": section,
            "CosName": '',
            "CurClass": ''
        }
        response = self.session.post(self.LESSON_URL,data=submit_dict)
        root = ET.fromstring(response.text)
        lst = []
        for e in root.findall("DataItem"):
            dataColumn = {}
            for f in e:
                dataColumn[f.tag] = f.text
            lst.append(dataColumn)
        return lst
    def grab_lessons(self,*args,**kwargs):
        pass

    def search_curriculum(self,thisYear:int,thisTeam:int):
        search_dict = {
            'ThisYear':thisYear,
            'ThisTeam':thisTeam,
        }
        self.__search_Asp_Utils(self.CURRICULUM_URL,search_dict)
        response = self.session.get(self.CURRICULUM_URL,data=search_dict,cookies=self.cookies)
        try:
            soup = BeautifulSoup(response.text,'lxml')
        except:
            soup = BeautifulSoup(response.text,'html.parser')
        curriculum = soup.find('table',{'id':'bgBase'})
        table = []
        for row in curriculum.findAll('tr'):
            column = []
            for col in row.findAll('td'):
                a_tag = col.find('a')
                if a_tag != None:
                    lesson = a_tag.text
                    teacher = col.text[len(lesson):-4]
                    classroom = col.text[len(lesson)+len(teacher):]
                    column.append(f'{lesson}\n{teacher}\n{classroom}') #split it
                else:
                    replaceStr = re.sub(r'\d\d:\d\d\d\d:\d\d','',col.text) #Remove class time
                    column.append(replaceStr)
            table.append(column)
        return table
    
    def search_midtern_score(self,seayear:int,seaterm:int):
        search_dict = {
            'ctl00$ContentPlaceHolder1$SEA_Year':seayear,
            'ctl00$ContentPlaceHolder1$SEA_Term':seaterm
        }
        self.__search_Asp_Utils(self.MIDTERM_URL,search_dict)
        response = self.session.post(self.MIDTERM_URL,data=search_dict,cookies=self.cookies)
        try:
            soup = BeautifulSoup(response.text,'lxml')
        except:
            soup = BeautifulSoup(response.text,'html.parser')
        score_dict = {}
        itemTable = soup.findAll('td',attrs={'width':'380'})
        scoreTable = soup.findAll('span',attrs={'id':lambda a: a and len(a) >= 8 and a[-8:] == "_Score_M"})
        for i in range(len(itemTable)):
            score_dict[itemTable[i].text] = float(scoreTable[i].text.replace('*','') if scoreTable[i].text != "" else "0.00")
        return score_dict

    def changepassword(self,newPassword:str):
        if len(newPassword) < 6: return
        submit_pwd = {
            'txtOri_Pwd':self._password,
            'txtNew_Pwd':newPassword,
            'txtSure_Pwd':newPassword,
            'btnOK':''
        }
        self.__search_Asp_Utils(self.CHANGEPWD_URL,submit_pwd)
        response = self.session.post(self.CHANGEPWD_URL,data=submit_pwd,cookies=self.cookies)
        self._password = newPassword
        

    def search_all_score(self,seayear:int,seaterm:int):
        search_dict = {
            'ctl00$ContentPlaceHolder1$SEA_Year':seayear,
            'ctl00$ContentPlaceHolder1$SEA_Term':seaterm
        }
        self.__search_Asp_Utils(self.SCORE_URL,search_dict)
        response = self.session.post(self.SCORE_URL,data=search_dict,cookies=self.cookies)
        try:
            soup = BeautifulSoup(response.text,'lxml')
        except:
            soup = BeautifulSoup(response.text,'html.parser')
        scoreTable = []
        itemTable = soup.findAll('td',attrs={'width':'330'})
        midScore = soup.findAll('span',attrs={'id':lambda a: a and len(a) >= 8 and a[-8:] == "_Score_M"})
        endScore = soup.findAll('span',attrs={'id':lambda a: a and len(a) >= 6 and a[-6:] == "_Score"})
        print(len(itemTable),len(midScore),len(endScore))
        for i in range(len(itemTable)):
            scoreTable.append([itemTable[i].text,
            float(midScore[i].text.replace('*','') if midScore[i].text != "" else "0.00"),
            float(endScore[i].text.replace('*','') if endScore[i].text != "" else "0.00")])
        return scoreTable


    def online_leave(self,startDate:datetime,endDate:datetime,selection:list):
        submit_dict = {
            'SEA_SDate':(None,startDate.strftime('%Y/%m/%d')),
            'SEA_EDate':(None,endDate.strftime('%Y/%m/%d')),
            'SEA_Note':(None,'Leave From Python'),
            'SEA_Holiday':(None,LeaveReason.PERSONAL.value),
            'REC_Insert':(None,'')
        }
        for e in selection:
            submit_dict[f'SEA_Section${e}']=(None,'on')
        self.__search_Asp_Utils(self.LEAVE_URL,submit_dict)
        response = self.session.post(self.LEAVE_URL,data=submit_dict,cookies=self.cookies)
        print(response.text)
    
        
if __name__ == "__main__":
    import getpass
    import pprint
    ntubLogin = NtubLoginSystem(input('User Name:'),getpass.getpass())
    pprint.pprint(ntubLogin.parse_lessons(3,5))

