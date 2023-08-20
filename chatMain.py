from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import *
import chatgpt
import openai
from PyQt6.QtWidgets import QPushButton, QMessageBox, QRadioButton, QTableWidgetItem
import pymysql
import json

class gpt():
    #전역 변수 : API KEY / MODEL 유형
    chatgpt_api_key = ''
    chatgpt_api_model = ''

    #아이디 중복여부 체크
    id_use_yn = True
    # 현재 로그인 중인 계정
    current_user = ''

    # db 공통 connection 연결
    def dbConnect(self):
        host = "my8002.gabiadb.com"
        user = "amsdb"
        password = "manager123!@"
        database = "amsdb"

        # 데이터베이스 연결
        connection = pymysql.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=database)
        return connection

    # db 공통(select 실행)
    def dbSearch(self, query, connection):
        try:
            with connection.cursor() as cursor:
                sql = query
                cursor.execute(sql)
                result = cursor.fetchall()
        except Exception as e:
            print("Error:", e)
        finally:
            connection.close()
            return result
    # db 공통(insert / update 실행)
    def dbInsert(self, query, connection):
        try:
            with connection.cursor() as cursor:
                sql = query
                cursor.execute(sql)
                # 변경사항 커밋
                connection.commit()
        except Exception as e:
            print("Error:", e)
        finally:
            connection.close()
    # 아이디 중복 여부 확인
    def checkId(self):
        id = ui.lineEdit_sign_id.text()
        connection = self.dbConnect()
        result = self.dbSearch(query=f"SELECT COUNT(*) FROM T_CHATGPT_USER WHERE USER_ID='{id}'", connection=connection)
        if id =='':
            msgBox = QMessageBox()
            msgBox.setText("아이디를 먼저 입력해주세요.")
            msgBox.exec()
            return
        if result[0][0] == 0:
            msgBox = QMessageBox()
            msgBox.setText("사용 가능한 아이디입니다.")
            msgBox.exec()
            self.id_use_yn = False
        else:
            msgBox = QMessageBox()
            msgBox.setText("이미 사용중인 아이디입니다.")
            msgBox.exec()
            self.id_use_yn = True
    # 회원가입 진행
    def signup(self):
        id = ui.lineEdit_sign_id.text()
        pwd = ui.lineEdit_sign_pwd.text()
        email = ui.lineEdit_sign_email.text() + "@knou.ac.kr"
        authKey = ui.lineEdit_sign_email_key.text()

        if pwd == '':
            msgBox = QMessageBox()
            msgBox.setText("비밀번호를 입력해주세요.")
            msgBox.exec()
            return
        elif email == '':
            msgBox = QMessageBox()
            msgBox.setText("이메일을 입력해주세요.")
            msgBox.exec()
            return
        elif id == '' and self.id_use_yn == True:
            msgBox = QMessageBox()
            msgBox.setText("아이디를 입력해주세요.")
            msgBox.exec()
            return
        elif authKey == '':
            msgBox = QMessageBox()
            msgBox.setText("인증번호을 입력해주세요.")
            msgBox.exec()
            return
        #아이디 중복 체크
        connection = self.dbConnect()
        result = self.dbSearch(query=f"SELECT COUNT(*) FROM T_CHATGPT_USER WHERE USER_ID='{id}'", connection=connection)
        if result[0][0] != 0:
            msgBox = QMessageBox()
            msgBox.setText("이미 존재하는 아이디입니다.")
            msgBox.exec()
            return
        # DB INSERT
        connection = self.dbConnect()
        self.dbInsert(
            query=f"INSERT INTO T_CHATGPT_USER(USER_ID,USER_PWD,USER_EMAIL) VALUES('{id}','{pwd}','{email}')"
            ,connection=connection)
        # DB SELECT
        connection1 = self.dbConnect()
        result = self.dbSearch(query=f"SELECT COUNT(*) FROM T_CHATGPT_USER WHERE USER_ID='{id}'", connection=connection1)
        if result[0][0] == 1:
            msgBox = QMessageBox()
            msgBox.setText("회원가입에 성공하였습니다.")
            msgBox.exec()
            ui.stackedWidget_main.setCurrentIndex(0);
    # 로그인 진행
    def login(self):
        id = ui.lineEdit_id.text()
        pwd = ui.lineEdit_pwd.text()
        if id =='' or pwd =='':
            return
        connection = self.dbConnect()
        result = self.dbSearch(
            query=f"SELECT USER_ID,USER_PWD,USER_CHATGPT_APIKEY FROM T_CHATGPT_USER WHERE USER_ID='{id}'",
            connection=connection)
        if len(result)==0:
            msgBox = QMessageBox()
            msgBox.setText("아이디/패스워드를 확인해주세요.")
            msgBox.exec()
            return

        if result[0][0] == id and result[0][1] == pwd:
            msgBox = QMessageBox()
            msgBox.setText("비밀노트에 성공적으로 로그인했습니다.")
            msgBox.exec()
            ui.stackedWidget_main.setCurrentIndex(2);
            ui.lineEdit_apikey.setText(result[0][2])
            self.current_user = id
        else:
            msgBox = QMessageBox()
            msgBox.setText("아이디/패스워드를 확인해주세요.")
            msgBox.exec()
            return
    # 로그인 화면 이동
    def goLogin(self):
        ui.stackedWidget_main.setCurrentIndex(0)
        ui.lineEdit_apikey.setText('')
        self.current_user = ''
        self.id_use_yn = True
    # 회원가입 화면 이동
    def moveSignup(self):
        ui.stackedWidget_main.setCurrentIndex(1)

    # api key 와 model 필수 값 validation 체크
    def validSetting(self):
        if self.chatgpt_api_key =='':
            msgBox = QMessageBox()
            msgBox.setText("API KEY를 입력하세요.")
            msgBox.exec()
            return True
        elif self.chatgpt_api_model  =='':
            msgBox = QMessageBox()
            msgBox.setText("CHATGPT MODEL를 입력하세요.")
            msgBox.exec()
            return True
        else:
            return False

    def validCheck(self,text,type):
        if text =='':
            msgBox = QMessageBox()
            msgBox.setText(f"{type}을(를) 입력하세요.")
            msgBox.exec()
            return True
        else:
            return False

    #open ai key 저장
    def saveApiKey(self):
        #api key 와 model 유형 선택
        self.chatgpt_api_key = ui.lineEdit_apikey.text()
        openai.api_key = self.chatgpt_api_key
        start_index = ui.comboBox.currentText().find(']')+1
        model= ui.comboBox.currentText()[start_index:].strip()
        self.chatgpt_api_model = model

        connection = self.dbConnect()
        self.dbInsert(
            query=f"UPDATE T_CHATGPT_USER SET USER_CHATGPT_APIKEY = '{self.chatgpt_api_key}' WHERE USER_ID ='{self.current_user}'"
            , connection=connection)
        msgBox = QMessageBox()
        msgBox.setText("chat gpt key가 등록되었습니다.")
        msgBox.exec()

    #chat-gpt completion api
    # chat gpt 실행
    def chat_gpt_content(self,prom,model):
        response = openai.Completion.create(
            engine=model,
            prompt=prom,
            max_tokens=2000,
            temperature=0.7
        )
        message = response.choices[0].text
        return message
    # 오류 해결사 함수
    def errorSolution(self):
        print("error")
        #유효성 체크
        # 유효성 체크 1) api-key 및 유형 선택 여부
        if self.validSetting():
            return

        #유효성 체크 2) 오류 코드 작성 여부
        err_code = ui.plainTextEdit_err.toPlainText()
        if self.validCheck(text=err_code,type="에러코드"):
            return

        #선택된 언어
        prgLanguage=''
        if ui.radioButton_err_java.isChecked():
            prgLanguage = ui.radioButton_err_java.text()
        elif ui.radioButton_err_py.isChecked():
            prgLanguage = ui.radioButton_err_py.text()
        elif ui.radioButton_err_c.isChecked():
            prgLanguage = ui.radioButton_err_c.text()
        elif ui.radioButton_err_cpl.isChecked():
            prgLanguage = ui.radioButton_err_cpl.text()
        elif ui.radioButton_err_js.isChecked():
            prgLanguage = ui.radioButton_err_js.text()
        elif ui.radioButton_err_sql.isChecked():
            prgLanguage = ui.radioButton_err_sql.text()

        #prompt 설정
        prompt = f"{prgLanguage}에서 발생한 에러 {err_code} 의 에러 원인과 해결 방안에 대해서 설명. 대답은 json 타입으로 해주고 원인은 reason,해결방안은 solution 이름으로 줄바꿈없이 반환해줘."
        print(prompt)

        #CHAT GPT 함수 실행
        try:
            result = self.chat_gpt_content(prom=prompt,model=self.chatgpt_api_model)
            data = json.loads(result)
            reason = data['reason']
            solution = data['solution']
            ui.plainTextEdit_err_sol.clear()
            ui.plainTextEdit_err_reason.clear()
            ui.plainTextEdit_err_reason.appendPlainText(reason)
            ui.plainTextEdit_err_sol.appendPlainText(solution)
        except Exception as e:
            print(e)
            ui.plainTextEdit_err_sol.clear()
            ui.plainTextEdit_err_sol.appendPlainText(str(e))

    # 쿼리 메이커 함수
    def querySolution(self):
        print("query")
        # 유효성 체크
        # 유효성 체크 1) api-key 및 유형 선택 여부
        if self.validSetting():
            return

        # 유효성 체크 2) 쿼리 요청 사항 작성 여부
        query = ui.plainTextEdit_query.toPlainText()
        if self.validCheck(text=query, type="쿼리 요청사항"):
            return

        # 선택된 언어
        queryType = ''
        if ui.radioButton_qy_my.isChecked():
            queryType = ui.radioButton_qy_my.text()
        elif ui.radioButton_qy_ms.isChecked():
            queryType = ui.radioButton_qy_ms.text()
        elif ui.radioButton_qy_mon.isChecked():
            queryType = ui.radioButton_qy_mon.text()
        elif ui.radioButton_qy_ora.isChecked():
            queryType = ui.radioButton_qy_ora.text()

        # prompt 설정
        prompt = f"{queryType} 문법으로 {query} 내용의 쿼리를 작성해줘."
        print(prompt)

        # CHAT GPT 함수 실행
        try:
            result = self.chat_gpt_content(prom=prompt, model=self.chatgpt_api_model)
            ui.plainTextEdit_query_2.clear()
            ui.plainTextEdit_query_2.appendPlainText(result)
        except Exception as e:
            print(e)
            ui.plainTextEdit_query_2.clear()
            ui.plainTextEdit_query_2.appendPlainText(str(e))

    # 함수 메이커 함수
    def functionSolution(self):
        print("function")
        # 유효성 체크
        # 유효성 체크 1) api-key 및 유형 선택 여부
        if self.validSetting():
            return

        # 유효성 체크 2) 함수 요청 사항 여부
        func = ui.plainTextEdit_func_request.toPlainText()
        if self.validCheck(text=func, type="함수 요청사항"):
            return

        # 유효성 체크  3) 1개 이상의 파라미터 입력 여부
        cnt =0;
        paraChk = list()
        var01 = ui.lineEdit_func_para1.text()
        var02 = ui.lineEdit_func_para2.text()
        var03 = ui.lineEdit_func_para2.text()
        var04 = ui.lineEdit_func_para2.text()
        paraChk.append(var01)
        paraChk.append(var02)
        paraChk.append(var03)
        paraChk.append(var04)
        for x in paraChk:
            if x != '':
                cnt+=1

        # 함수 파라미터 유효성 검사(1개 이상 입력)
        if cnt ==0:
            msgBox = QMessageBox()
            msgBox.setText("함수 파라미터를 1개 이상 입력하세요.")
            msgBox.exec()
            return


        # 선택된 언어
        prgLanguage = ''
        if ui.radioButton_func_c.isChecked():
            prgLanguage = ui.radioButton_func_c.text()
        elif ui.radioButton_func_cpl.isChecked():
            prgLanguage = ui.radioButton_func_cpl.text()
        elif ui.radioButton_func_py.isChecked():
            prgLanguage = ui.radioButton_func_py.text()
        elif ui.radioButton_func_java.isChecked():
            prgLanguage = ui.radioButton_func_java.text()
        elif ui.radioButton_func_js.isChecked():
            prgLanguage = ui.radioButton_func_js.text()

        # prompt 설정
        prompt = f"{prgLanguage} 언어를 사용하여, 파라미터 명은 {var01},{var02},{var03},{var04}를 사용하고 기능은 {func} 에 맞게 함수를 만들어줘."
        print(prompt)

        # CHAT GPT 함수 실행
        try:
            result = self.chat_gpt_content(prom=prompt, model=self.chatgpt_api_model)
            print(result)
            ui.plainTextEdit_func_sol.clear()
            ui.plainTextEdit_func_sol.appendPlainText(result)
        except Exception as e:
            print(e)
            ui.plainTextEdit_func_sol.clear()
            ui.plainTextEdit_func_sol.appendPlainText(str(e))

        def registerDB(self):
            host = "my8002.gabiadb.com"
            user = "amsdb"
            password = "manager123!@"
            database = "amsdb"
            # self.db_host = ui.lineEdit_queryadv_hosturl
            # self.db_user = ui.lineEdit_queryadv_user
            # self.db_pwd = ui.lineEdit_queryadv_pwd
            # self.db_database = ui.lineEdit_queryadv_database
            connection = self.dbConnect()
            # connection = self.dbConnect_queryadv(host=self.db_host,user=self.db_user,pwd=self.db_pwd,database=self.db_database)

            result = self.dbSearch(
                query=f"SELECT table_name,column_name, data_type FROM information_schema.`COLUMNS` WHERE TABLE_SCHEMA = 'amsdb' and (TABLE_NAME  ='a_class' or TABLE_NAME ='a_member')",
                connection=connection
            )
            print(result)
            prompt = f"mysql로된 db의 테이블이름,컬럼명, 데이터 타입을 정의한 정보는 {result}.이 정보를 토대로 클래스별 멤버 리스트를 뽑는 쿼리 작성해줘."
            answer_learning = self.chat_gpt_content(prom=prompt, model=self.chatgpt_api_model)
            answer_learning = str(answer_learning).replace(";", "")
            print(answer_learning)
            connection = self.dbConnect()
            result = self.dbSearch(
                query=answer_learning,
                connection=connection
            )
            print(result)
            prompt2 = f"위에 알려준 테이블 정보를 토대로 클래스별 학생 리스트를 뽑는 쿼리"
            # answer_order = self.chat_gpt_content(prom=prompt2,model=self.chatgpt_api_model)
            # print(answer_order)
            # ui.tableWidget_queryadv_result.
            data = result
            ui.tableWidget_queryadv_result.setRowCount(len(data))
            ui.tableWidget_queryadv_result.setColumnCount(2)  # 테이블은 3개의 열로 구성

            for row_index, row_data in enumerate(data):
                for col_index, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    ui.tableWidget_queryadv_result.setItem(row_index, col_index, item)

                    # 헤더 레이블 설정
            ui.tableWidget_queryadv_result.setHorizontalHeaderLabels(["학생명", "클래스명"])

            # 테이블 크기에 따라 셀 크기 조절
            ui.tableWidget_queryadv_result.resizeColumnsToContents()
            ui.tableWidget_queryadv_result.resizeRowsToContents()
    def logging(self, text):
        ui.plainTextEdit_log.appendPlainText(text)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = chatgpt.Ui_ComputerScienceSecretNote()
    ui.setupUi(MainWindow)
    MainWindow.setWindowTitle("컴퓨터과학과 학생의 비밀노트")
    bot = gpt()

    ##회원가입 화면 이동
    ui.pushButton_signup.clicked.connect(bot.moveSignup)
    ##회원가입 아이디 체크
    ui.pushButton_chk_btn.clicked.connect(bot.checkId)
    ##회원가입 인증번호 발송

    ##회원가입 완료
    ui.pushButton_signup_comp.clicked.connect(bot.signup)
    ## 로그인
    ui.pushButton_login.clicked.connect(bot.login)
    ##로그인 화면으로 이동
    ui.pushButton_go_login.clicked.connect(bot.goLogin)

    ##chat-gpt api key 등록
    ui.pushButton_save_api.clicked.connect(bot.saveApiKey)
    ##오류 해결사) 오류 분석
    ui.radioButton_err_java.setChecked(True)
    ui.pushButton_err_sol.clicked.connect(bot.errorSolution)
    ##쿼리 메이커) 쿼리 생성
    ui.radioButton_qy_ora.setChecked(True)
    ui.pushButton_query.clicked.connect(bot.querySolution)
    ##함수 메이커) 함수 생성
    ui.radioButton_func_java.setChecked(True)
    ui.pushButton_func_make.clicked.connect(bot.functionSolution)

    MainWindow.show()
    sys.exit(app.exec())
