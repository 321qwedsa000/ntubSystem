import requests
from bs4 import BeautifulSoup
import re

class NtubLoginSystem:
    def __search_VIEW(self,url,dic):
        response = self.session.get(url)
        if response.status_code == 404:
            raise "No Internet Connection"
        try:
            soup = BeautifulSoup(response.content,features='lxml')
        except:
            soup = BeautifulSoup(response.content,features='html.parser')
        dic['__VIEWSTATE'] = soup.select_one('#__VIEWSTATE')['value'] if soup.select_one('#__VIEWSTATE') != None else ''
        dic['__VIEWSTATEGENERATOR'] = soup.select_one('#__VIEWSTATEGENERATOR')['value'] if soup.select_one('#__VIEWSTATEGENERATOR') != None else ''
        dic['__EVENTVALIDATION'] = soup.select_one('#__EVENTVALIDATION')['value'] if soup.select_one('#__EVENTVALIDATION') != None else ''

    def __init__(self,username,password):
        self.session = requests.Session()
        self.LOGIN_URL = "http://ntcbadm1.ntub.edu.tw/login.aspx?Type=0" #POST url
        self.CURRICULUM_URL = "http://ntcbadm1.ntub.edu.tw/STDWEB/Sel_Student.aspx" #GET url
        self.username = username
        self.password = password
        loginData = {
            'UserID':self.username,
            'PWD':self.password,
            'loginbtn':''
        }
        self.__search_VIEW(self.LOGIN_URL,loginData)
        self.cookies = None
        loginResponse = self.session.post(self.LOGIN_URL,data=loginData)
        self.cookies = loginResponse.cookies
    
    def search_curriculum(self,thisYear,thisTeam):
        search_dict = {
            'ThisYear':thisYear,
            'ThisTeam':thisTeam,
        }
        self.__search_VIEW(self.CURRICULUM_URL,search_dict)
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
                    column.append(f'{lesson}\n{teacher}\n{classroom}')
                else:
                    replaceStr = re.sub(r'\d\d:\d\d\d\d:\d\d','',col.text)
                    column.append(replaceStr)
            table.append(column)
        return table
        
        

if __name__ == "__main__":
    import getpass
    import pprint
    ntubLogin = NtubLoginSystem(input(),getpass.getpass())
    pprint.pprint(ntubLogin.search_curriculum(108,2))