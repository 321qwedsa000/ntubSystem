import requests
from bs4 import BeautifulSoup
import re
from enum import Enum
from datetime import datetime
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

    def __init__(self,username,password):
        #####################
        # Ntub Related URLS #
        #####################
        self.LOGIN_URL = "http://ntcbadm1.ntub.edu.tw/login.aspx?Type=0" #POST url
        self.CURRICULUM_URL = "http://ntcbadm1.ntub.edu.tw/STDWEB/Sel_Student.aspx" #GET url
        self.MIDTERM_URL = "http://ntcbadm1.ntub.edu.tw/ACAD/STDWEB/GRD_GRDMQry.aspx" #POST url
        self.SCORE_URL = "http://ntcbadm1.ntub.edu.tw/ACAD/STDWEB/GRD_GRDQry.aspx" #POST url
        self.LEAVE_URL = "http://ntcbadm1.ntub.edu.tw/StdAff/STDWeb/ABS0101Add.aspx" #POST url
        ###################
        # Login into NTUB #
        ###################
        #
        self.session = requests.Session()
        self.username = username
        self.password = password
        loginData = {
            'UserID':self.username,
            'PWD':self.password,
            'loginbtn':''
        }
        self.__search_Asp_Utils(self.LOGIN_URL,loginData)
        self.cookies = None
        loginResponse = self.session.post(self.LOGIN_URL,data=loginData)
        if loginResponse.text.startswith('<script>'):
            raise NtubLoginFailedException(f'Login {username} failed')
        self.cookies = loginResponse.cookies
        #

    def search_curriculum(self,thisYear,thisTeam):
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
    
    def search_midtern_score(self,seayear,seaterm):
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

''' Deprecated
    def online_leave(self,startDate:datetime,endDate:datetime,selection:list):
        submit_dict = {
            'SEA_SDate':startDate.strftime('%Y/%m/%d'),
            'SEA_EDate':endDate.strftime('%Y/%m/%d'),
            'SEA_Note':'Leave From Python',
            'SEA_Holiday':LeaveReason.PERSONAL.value,
            'REC_File_Value':'',
            'REC_FILE_UKEY':'',
            'REC_Insert':''
        }
        for e in selection:
            submit_dict[f'SEA_Section${e}']='on'
        self.__search_Asp_Utils(self.LEAVE_URL,submit_dict)
        response = self.session.post(self.LEAVE_URL,data=submit_dict,cookies=self.cookies)
        print(response.text)
'''
        
if __name__ == "__main__":
    import getpass
    import pprint
    ntubLogin = NtubLoginSystem(input('User Name:'),getpass.getpass())
    pprint.pprint(ntubLogin.search_all_score(108,1))