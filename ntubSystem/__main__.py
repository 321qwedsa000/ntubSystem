from .ntubsys import NtubLoginSystem , NtubLoginFailedException, NtubNoClassException
import getpass
from prettytable import PrettyTable
import json
import os
desc='''
1)預選您想要的課程
2)查詢自己的課表
3)加選您預選的課程
4)加選(未實作)
5)退選(未實作)
請輸入選項(1-3)︰'''

def preGrab(student:NtubLoginSystem):
    def getString(func,*args,**kwargs):
        TypeOptions = func(*args,**kwargs)
        TypeOptions = list(TypeOptions.keys())
        i = None
        print("請輸入要查詢的選項")
        for i,e in enumerate(TypeOptions,1):
            print(f"{i}){e}")
        i = int(input(f"請輸入數字(1~{i})︰"))
        TypeOptions = TypeOptions[i-1]
        return TypeOptions
    year = int(input("查詢年度︰"))
    term = int(input("查詢學期︰"))
    eduTypeOptions = getString(student.getEduTypeOptions)
    deptTypeOptions = getString(student.getDeptTypeOptions,eduTypeOptions)
    classTypeOptions = getString(student.getClassTypeOptions,eduTypeOptions,deptTypeOptions)
    op = student.getDeptTypeOptions(eduTypeOptions)[deptTypeOptions]
    print(op)
    lesson = student.get_lesson_info(year,term,eduTypeOptions,deptTypeOptions,classTypeOptions)
    i = None
    lesson[0] = ["代號"] + lesson[0]
    for i in range(1,len(lesson)):
        lesson[i] = [i] + lesson[i]
    table = PrettyTable(lesson[0])
    table.add_rows(lesson[1:])
    print(table)
    selectIndex = int(input(f"請輸入代號(1~{i})︰"))
    print(lesson[selectIndex])
    jsonData = None
    if os.path.exists("preGrab.json"):
        with open("preGrab.json","r") as FileObj:
            jsonData = json.load(FileObj)
    if jsonData:
        with open("preGrab.json","w") as FileObj:
            jsonData.append({
                "OpClass":op,
                "Serial":lesson[selectIndex][3],
                "CurTerm":lesson[selectIndex][2]
            })
            json.dump(jsonData,FileObj)
    else:
        with open("preGrab.json","w") as FileObj:
            jsonData = []
            jsonData.append({
                "OpClass":op,
                "Serial":lesson[selectIndex][3],
                "CurTerm":lesson[selectIndex][2]
            })
            json.dump(jsonData,FileObj)

def queryCurriculum(student:NtubLoginSystem):
    year = int(input("查詢年度︰"))
    term = int(input("查詢學期︰"))
    curriculum = student.search_curriculum(year,term)
    table = PrettyTable(curriculum[0])
    table.add_rows(curriculum[1:])
    print(table)

def grabpreGrabLessons(student:NtubLoginSystem):
    if os.path.exists("preGrab.json"):
        with open("preGrab.json","r") as FileObj:
            jsonData = json.load(FileObj)
            for elements in jsonData:
                print(student.grab_lessons(elements))

def main():
    try:
        student = NtubLoginSystem(input("學號︰"),getpass.getpass('密碼︰'))
        while True:
            functional_lst = [preGrab,queryCurriculum,grabpreGrabLessons]
            op = int(input(desc))
            functional_lst[op-1](student)

    except NtubLoginFailedException:
        print("登入失敗")
    except NtubNoClassException:
        print("選課未開放")
    finally:
        print("Mod By Techaonical")


if __name__ == '__main__':
    main()