from .ntubsys import NtubLoginSystem , NtubLoginFailedException
import getpass
from prettytable import PrettyTable
def main():
    try:
        student = NtubLoginSystem(input("學號︰"),getpass.getpass('密碼︰'))
        while True:
            s = '''
請問要做什麼事
1.查課表
2.查期中考成績
3.查學期所有成績
4.加退選
5.結束
請輸入(1~5)︰'''
            print(s,end='')
            option = int(input())
            if option == 1:
                print('查詢年度︰',end='')
                year = int(input())
                print('查詢學期︰',end='')
                term = int(input())
                lst = student.search_curriculum(year,term)
                table = PrettyTable(lst[0])
                table.add_rows(lst[1::])
                print(f"{year}年度第{term}學期之課表如下︰")
                print(table)
            elif option == 2:
                print('查詢年度︰',end='')
                year = int(input())
                print('查詢學期︰',end='')
                term = int(input())
                dic = student.search_midtern_score(year,term)
                print(f"{year}年度第{term}學期之成績如下︰")
                table = PrettyTable(["科目","成績"])
                for key in dic:
                    table.add_row([key,dic[key]])
                print(table)
            elif option == 3:
                print('查詢年度︰',end='')
                year = int(input())
                print('查詢學期︰',end='')
                term = int(input())
                lst = student.search_all_score(year,term)
                print(f"{year}年度第{term}學期之成績如下︰")
                table = PrettyTable(["科目","期中成績","期末成績"])
                table.add_rows(lst)
                print(table)
            elif option == 4:
                data = student.grab_deptNo()
                lst = []
                index = 1
                for e in data:
                    lst.append([index,e])
                    index += 1
                table = PrettyTable(["代號","學系"])
                table.add_rows(lst)
                print(table)
                deptNo = lst[int(input(f"請選擇代號(1~{index-1})︰"))-1][1]
                print(f"你選了'{deptNo}'")
                day = int(input("請輸入星期(1~7)︰"))
                print(f"你選了星期{day}")
                section = int(input("請輸入節次(1-14):"))
                data = student.parse_lessons(data[deptNo],day,section)
                table = PrettyTable(['代號','必選修','開課班級/組別','科目名稱','學分','通識領域','上課節次','授課老師','已選人數','人數上限'])
                lst = []
                index = 1
                for e in data:
                    lst.append(e)
                    table.add_row([index,data[e]['SelKind_Name'],data[e]['Class_Name'],data[e]['Cos_Name'],data[e]['Cos_Hours'],data[e]['CurClass_SecName'],data[e]['Cur_Time'],data[e]['Teacher_Name'],data[e]['Sel_Counts'],data[e]['Sel_Max']])
                    index += 1
                print(table)
            elif option == 5:
                break
    except NtubLoginFailedException:
        print('學號或密碼錯誤')
    finally:
        print("Mod by Techaonical ©2021")

if __name__ == '__main__':
    main()