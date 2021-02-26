from ntubsys import NtubLoginSystem , NtubLoginFailedException
import getpass

def main():
    try:
        student = NtubLoginSystem(input("學號"),getpass.getpass('密碼'))
        while True:
            print
            (
                '''
                    請問要做什麼事
                    1.查課表
                    2.查期中考成績
                    3.查所有成績
                    4.加退選
                    請輸入(1~4)︰
                '''
            )
            option = input()
    except NtubLoginFailedException:
        print('學號或密碼錯誤')
    except:
        print('輸入有誤')
    finally:
        print("Bye by Techhonical")

if __name__ == '__main__':
    main()