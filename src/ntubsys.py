import requests
from bs4 import BeautifulSoup
import re
from enum import Enum
from datetime import datetime
import xml.etree.ElementTree as ET


class NtubLoginFailedException(Exception):
    def __init__(self,message):
        super(NtubLoginFailedException,self).__init__(message)

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
        self.MAIN_PAGE_URL = "http://ntcbadm1.ntub.edu.tw/STDWEB/SelChoose/SelChooseMain.aspx" #GET URL
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
    def grab_deptNo(self):
        mainPageResponse = self.session.get(self.MAIN_PAGE_URL)
        try:
            soup = BeautifulSoup(mainPageResponse.text,'lxml')
        except:
            soup = BeautifulSoup(mainPageResponse.text,'html.parser')
        submit_data = {
            "ModuleName": "InitSelDept",
            "Years": soup.find("input",{"id":"SelYear"})["value"],
            "Term": soup.find("input",{"id":"SelTerm"})["value"],
            "Desire": '',
            "EduNo": soup.find("input",{'id':'EduNo'})['value']
        }
        response = self.session.post(self.LESSON_URL,data=submit_data)
        root = ET.fromstring(response.text)
        dataDict = {}
        for e in root.findall("DataItem"):
            dataDict[e[1].text] = e[0].text
        return dataDict
    def get_deptNo(self,name):
        return self.grab_deptNo()[name]

    def parse_lessons(self,deptNo,day,section): #901 , 400
        mainPageResponse = self.session.get(self.MAIN_PAGE_URL)
        try:
            soup = BeautifulSoup(mainPageResponse.text,'lxml')
        except:
            soup = BeautifulSoup(mainPageResponse.text,'html.parser')
        submit_dict = {
            "ModuleName": 'QueryCurData',
            "EduNo": soup.find("input",{'id':'EduNo'})['value'],
            "Desire": '',
            "DeptNo": deptNo,
            "Grade": '',
            "Week": day,
            "Section": section,
            "CosName": '',
            "CurClass": ''
        }
        response = self.session.post(self.LESSON_URL,data=submit_dict)
        root = ET.fromstring(response.text)
        dic = {}
        for e in root.findall("DataItem"):
            dataColumn = {}
            for f in e:
                dataColumn[f.tag] = f.text
            dic[dataColumn["Cos_ID"]] = dataColumn
        return dic
    def grab_lessons(self,currentDict):
        mainPageResponse = self.session.get(self.MAIN_PAGE_URL)
        try:
            soup = BeautifulSoup(mainPageResponse.text,'lxml')
        except:
            soup = BeautifulSoup(mainPageResponse.text,'html.parser')
        submit_dict = {
            "ModuleName": "DoAddCur",
            "Years": soup.find("input",{"id":"SelYear"})["value"],
            "Term": soup.find("input",{"id":"SelTerm"})["value"],
            "Desire": '',
            "OpClass": currentDict["OP_Class"],
            "Serial": currentDict["Serial"],
            "CurTerm": currentDict["Cur_Term"],
            "EduData": soup.find("input",{"id":"EduData"})["value"],
            "Contrast": soup.find("input",{"id":"Contrast"})["value"],
            "CreditData": soup.find("input",{"id":"CreditData"})["value"],
            "AddData": soup.find("input",{"id":"AddData"})["value"],
            "EduCourseData": soup.find("input",{"id":"EduCourseData"})["value"],
            "OtherData": soup.find("input",{"id":"OtherData"})["value"],
            "ConvertData": soup.find("input",{"id":"ConvertData"})["value"]
        }
        response = self.session.post(self.LESSON_URL,data=submit_dict)
        print(response.text)
    def quit_lessons(self,currentDict):
        mainPageResponse = self.session.get(self.MAIN_PAGE_URL)
        try:
            soup = BeautifulSoup(mainPageResponse.text,'lxml')
        except:
            soup = BeautifulSoup(mainPageResponse.text,'html.parser')
        submit_dict = {
        "ModuleName": "DoDelCur",
        "Years": soup.find("input",{"id":"SelYear"})["value"],
        "Term": soup.find("input",{"id":"SelTerm"})["value"],
        "Desire": "",
        "OpClass": currentDict["OP_Class"],
        "Serial": currentDict["Serial"],
        "CurTerm": currentDict["Cur_Term"]
        }
        response = self.session.post(self.LESSON_URL,data=submit_dict)
        print(response.text)

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

 
        
if __name__ == "__main__":
    import getpass
    import pprint
    ntubLogin = NtubLoginSystem(input('User Name:'),getpass.getpass())
    #lesson = ntubLogin.parse_lessons(ntubLogin.get_deptNo("四技資管"),2,5)
    pprint.pprint(ntubLogin.search_curriculum(109,2))
