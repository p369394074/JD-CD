import re
import sys
import sqlite3
import time
import pymysql
import requests
import selenium.webdriver.support.expected_conditions as EC

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QCursor, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QApplication, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QTextEdit, QMessageBox, QMainWindow, QTableView, QFrame, QSplitter, QGroupBox, QTextBrowser, QMenu, \
    QMenuBar, QDialog, QAbstractItemView, QHeaderView, QStatusBar, QShortcut, QCheckBox, QComboBox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import Chrome, ChromeOptions

global rownumweb, isrun, isstop
rownumweb = -1
isrun = True
isstop = False

# class startwork(QThread):
#     def __init__(self):
#         super(startwork, self).__init__()
#     def run(self):
#         while isrun:
#
class loginwin(QWidget):
    def __init__(self):
        super(loginwin, self).__init__()
        self.initUI()
    def initUI(self):
        self.setWindowTitle("登陆")
        palette1 = QtGui.QPalette()
        palette1.setBrush(self.backgroundRole(),QtGui.QBrush(QtGui.QPixmap("./image/login.png")))
        self.setPalette(palette1)
        # self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.resize(500,300)
        self.label_count = QLabel("账号：")
        self.label_count.setFont(QFont("微软雅黑",15,40))
        self.label_pwd = QLabel("密码：")
        self.label_pwd.setFont(QFont("微软雅黑",15,40))
        self.linedit_count = QLineEdit()
        self.linedit_count.sizeHint()
        self.linedit_pwd = QLineEdit()
        self.linedit_pwd.setEchoMode(QLineEdit.Password)
        self.btn_login = QPushButton("登陆")
        self.btn_exit = QPushButton("退出")
        self.glayout = QGridLayout()
        self.glayout.addWidget(self.label_count,0,0,1,1)
        self.glayout.addWidget(self.linedit_count,0,1,1,3)
        self.glayout.addWidget(self.label_pwd,1,0,1,1)
        self.glayout.addWidget(self.linedit_pwd,1,1,1,3)
        self.glayout.addWidget(self.btn_exit,3,1,1,1)
        self.glayout.addWidget(self.btn_login,3,2,1,1)
        self.setLayout(self.glayout)
        self.btnclieced()
    def btnclieced(self):
        self.btn_exit.clicked.connect(self.btn_exit_event)
        self.btn_login.clicked.connect(self.btn_login_event)
    def btn_login_event(self):
        if self.linedit_count.text() == "" or self.linedit_pwd.text() == "":
            QMessageBox.warning(self,"错误","\n账号或密码不能为空\n",QMessageBox.Yes)
        else:
            if self.isexist("countname",self.linedit_count.text()) and self.isexist("password",self.linedit_pwd.text()):
                self.hide()
                self.mainwin = mainwin()
                self.mainwin.show()
            else:QMessageBox.critical(self,"错误","\n账号或密码错误，请重新输入！\n",QMessageBox.Yes)
    def isexist(self,colname,value):
        namelist = []
        for i in self.databasevalue("remote","select %s from applicationusers"%(colname)):
            namelist.append(i[0])
        if value in namelist:
            return True
        return False

    def btn_exit_event(self):
        massage = QMessageBox.question(self,"退出","\n是否退出本程序？\n",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if massage == QMessageBox.Yes:
            self.close()
        if massage == QMessageBox.No:
            pass
    def closeEvent(self, QCloseEvent):
        massage = QMessageBox.question(self,"退出","\n是否退出本程序？\n",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if massage == QMessageBox.Yes:
            pass
        if massage == QMessageBox.No:
            QCloseEvent.ignore()
    def databasevalue(self,select,sqlstr):
        if select == "remote":
            remotdatabase = pymysql.connect(host = "1562800uq9.51mypc.cn",
                                            port = 26171,
                                            user = "root",
                                            passwd = "1111aaaa",
                                            db = "jd")
            cursor = remotdatabase.cursor()
            cursor.execute(sqlstr)
            value = cursor.fetchall()
            remotdatabase.commit()
            remotdatabase.close()
            return value
        if select == "local":
            localdatabase = sqlite3.connect("./db/db.users")
            cursor = localdatabase.cursor()
            cursor.execute(sqlstr)
            value = cursor.fetchall()
            localdatabase.commit()
            localdatabase.close()
            return value
class mainwin(QMainWindow):
    def __init__(self):
        super(mainwin, self).__init__()
        self.initUI()
    def initUI(self):
        self.cdgetorder()
        # self.setWindowTitle("茶蛋接单")
        titletext = (loginwin.linedit_count.text()+"，当前剩余余额"+self.databasevalue("remote",'select balance from applicationusers where countname = "%s"'%(loginwin.linedit_count.text()))[0][0])
        self.setWindowTitle(titletext)
        self.resize(1440,900)
        self.menu = QMenuBar()
        self.menu.addMenu("京东账号导入").addAction("网页登录导入")
        self.menu.addMenu("京东活动抽话费券").addAction("开始抽奖")
        self.menu.triggered.connect(self.menuaction)
        self.setMenuBar(self.menu)
        self.widget = QWidget()
        glayout = QGridLayout()
        self.widget.setLayout(glayout)
        self.setCentralWidget(self.widget)

        self.statbar = QStatusBar()
        self.setStatusBar(self.statbar)
        self.nowtime = QLabel()
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(lambda :self.nowtime.setText(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())))
        self.timer.timeout.connect(self.timeoutevn)
        self.statbar.addPermanentWidget(self.nowtime)
        self.leftframe = QFrame()
        self.leftframe.setFrameShape(QFrame.StyledPanel)
        leftframelayout = QGridLayout()
        self.leftframe.setLayout(leftframelayout)
        self.cdorderstatuslabel = QLabel()
        self.statbar.addWidget(self.cdorderstatuslabel)

        self.usermodel()
        self.userlistbox =QGroupBox("账号列表")
        self.getusername = getusername()
        windowliset.append(self.getusername)
        self.getusername.start()
        self.getusername.complete.connect(self.freshuserview)
        userlistboxlayout = QGridLayout()
        self.userlistbox.setLayout(userlistboxlayout)
        self.userview = QTableView()
        self.userview.setModel(self.usermodel)
        self.userview.setShowGrid(True)
        self.userview.verticalHeader().hide()
        self.userview.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.userview.setSelectionMode(QAbstractItemView.SingleSelection)
        self.userview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.userview.horizontalHeader().setStretchLastSection(True)
        self.userview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.userview.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.userview.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        self.userview.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.userview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        userlistboxlayout.addWidget(self.userview)

        self.ctrlbox = QGroupBox("接单配置")
        cotrolboxlayout = QGridLayout()
        self.ctrlbox.setLayout(cotrolboxlayout)
        self.startbtn = QPushButton("开始接单")
        self.stopbtn = QPushButton("停止接单")
        self.stopbtn.hide()
        self.cdlogin = QFrame()
        self.cdlogin.setAutoFillBackground(True)
        cdglayout = QGridLayout()
        self.cdlogin.setLayout(cdglayout)
        self.countlabel = QLabel("茶蛋账号：")
        self.countlinedit = QLineEdit()
        self.cdpwdlabel = QLabel("茶蛋密码：")
        self.cdpwdlinedit = QLineEdit()
        self.cdpwdlinedit.setEchoMode(QLineEdit.Password)
        self.cdloginbtn = QPushButton("登陆")
        self.cdloginbtn.setShortcut(Qt.Key_Return)
        cdglayout.addWidget(self.countlabel,0,0,1,1)
        cdglayout.addWidget(self.countlinedit,1,0,1,2)
        cdglayout.addWidget(self.cdpwdlabel,2,0,1,1)
        cdglayout.addWidget(self.cdpwdlinedit,3,0,1,2)
        cdglayout.addWidget(self.cdloginbtn,5,0,1,1)
        self.cdloginbtn.clicked.connect(self.cdloginevn)
        self.startbtn.setFont(QFont("微软雅黑",15,35))
        self.stopbtn.setFont(QFont("微软雅黑",15,35))
        cotrolboxlayout.addWidget(self.startbtn,0,0)
        cotrolboxlayout.addWidget(self.stopbtn,0,0)
        cotrolboxlayout.addWidget(self.cdlogin,0,0)

        leftframelayout.addWidget(self.userlistbox,0,0,5,0)
        leftframelayout.addWidget(self.ctrlbox,6,0,5,0)

        self.rightframe = QFrame()
        self.rightframe.setFrameShape(QFrame.StyledPanel)
        rightframelayout = QGridLayout()
        self.rightframe.setLayout(rightframelayout)

        self.infobox = QGroupBox("订单列表")
        infoboxlayout = QGridLayout()
        self.infobox.setLayout(infoboxlayout)
        self.infoview = QTableView()
        self.infoview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.infoview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.infoview.verticalHeader().hide()
        self.infoview.horizontalHeader().setStretchLastSection(True) #自动占满整个窗口
        # self.infoview.setColumnWidth(10,10)
        self.orderform()
        self.infoview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.infoview.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents) #自动调整单元格大小
        self.infoview.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.infoview.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        self.infoview.horizontalHeader().setSectionResizeMode(6,QHeaderView.ResizeToContents)
        self.infoview.horizontalHeader().setSectionResizeMode(7,QHeaderView.ResizeToContents)
        infoboxlayout.addWidget(self.infoview)

        self.logbox = QGroupBox("输出日志")
        logboxlayout = QGridLayout()
        self.logbox.setLayout(logboxlayout)
        self.textbrowser = QTextBrowser()
        logboxlayout.addWidget(self.textbrowser)

        rightframelayout.addWidget(self.infobox,0,0,6,0)
        rightframelayout.addWidget(self.logbox,6,0,4,0)


        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.leftframe)
        splitter.addWidget(self.rightframe)
        splitter.setStretchFactor(0,3)
        splitter.setStretchFactor(1,7)

        glayout.addWidget(splitter)
        self.widget.setLayout(glayout)
        self.btnevn()
        windowliset.append(self)
        self.ordertimer = QTimer()
        self.ordertimer.start(10000)
        self.ordertimer.timeout.connect(self.freshorderview)
    def freshorderview(self):
        self.fresh = freshorderstat()
        self.fresh.start()
        self.orderform()
    def timeoutevn(self):
        self.cdgetorder()
        try:
            if self.cdprice != "0" or self.cdprice != "1":
                self.cdorderstatuslabel.setText("茶蛋100面值当前结算价:%s￥"%(self.cdprice))
                self.cdlogin.close()
            if self.cdprice == 0:
                self.cdorderstatuslabel.setText("请先登录茶蛋")
                self.cdlogin.show()
                self.timer.stop()
            if self.cdprice == 1:
                self.cdlogin.close()
                self.cdorderstatuslabel.setText("京东话费100当前已下架")
                # self.textbrowser.append(time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())+"茶蛋京东话费已下架")
        except Exception as err:
            pass
    def cdgetorder(self):
        self.cdprice = ""
        with open("./db/cdck.users","r") as f:
            k = f.read()
            f.close()
        j = re.findall("userInfor=(.*?)\n",k)
        cookiejar = requests.cookies.RequestsCookieJar()
        for i in re.findall("(.*?)=.*?\n",k):
            if i in ("userInfor","logged","JSESSIONID"):
                cookiejar.set(i,re.findall("%s=(.*?)\n"%i,k)[0],domain = "chadan.wang")
        headers = {
            "Origin": "http://chadan.wang",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        s = requests.Session()
        s.cookies = cookiejar
        s.headers = headers
        getpricedata = {}
        getpricedata["getOtherType"] = "true"
        getpricedata["JSESSIONID"] = re.findall("logged=(.*?)\n",k)[0]
        s = s.post("http://api.chadan.cn/order/other/getValidProduct",data = getpricedata)
        try:
            self.cdprice = re.findall('"结算价：(.*?)元",',s.text)[0]
        except Exception as err:
            if s.text == '{"errorMsg":"OK","data":[],"errorCode":200}':
                self.cdprice = 1
            if s.text == '{"errorCode":2000,"errorMsg":"登录超时，请重新登录","expire":null}':
                self.cdprice = 0
    def orderform(self):
        self.infoModel = QStandardItemModel(self.databasevalue("local","select count(cardNumber) from products")[0][0],9)
        self.infoModel.setHorizontalHeaderLabels(["序号","京东订单","充值号码","订单信息","付款金额"," 结算金额","下单账号","状态","备注"])
        for i in range(self.databasevalue("local","select count(cardNumber) from products")[0][0]):
            item0 = QStandardItem(str(i+1))
            item0.setTextAlignment(Qt.AlignHCenter)
            self.infoModel.setItem(i,0,item0)
            item1 = QStandardItem(self.databasevalue("local","select JDinformation from products")[i][0])
            item1.setTextAlignment(Qt.AlignHCenter)
            self.infoModel.setItem(i,1,item1)
            item2 = QStandardItem(self.databasevalue("local","select cardNumber from products")[i][0])
            item2.setTextAlignment(Qt.AlignHCenter)
            self.infoModel.setItem(i,2,item2)
            item3 = QStandardItem(self.databasevalue("local","select JDinformationinfo from products")[i][0])
            item3.setTextAlignment(Qt.AlignHCenter)
            self.infoModel.setItem(i,3,item3)
            item4 = QStandardItem(self.databasevalue("local","select JDpaymoney from products")[i][0])
            item4.setTextAlignment(Qt.AlignHCenter)
            self.infoModel.setItem(i,4,item4)
            item5 = QStandardItem(self.databasevalue("local","select CDprice from products")[i][0])
            item5.setTextAlignment(Qt.AlignHCenter)
            self.infoModel.setItem(i,5,item5)
            item6 = QStandardItem(self.databasevalue("local","select JDcount from products")[i][0])
            item6.setTextAlignment(Qt.AlignHCenter)
            self.infoModel.setItem(i,6,item6)
            i7 = self.databasevalue("local","select orderStatus from products ")[i][0]
            if i7 == "6":
                i7 = "待充值"
            if i7 == "7":
                i7 = "失败"
            if i7 == "3":
                i7 = "充值成功"
            if i7 == "1":
                i7 = "处理中"
            if i7 == "4":
                i7 = "失败"
            item7 = QStandardItem(i7)
            item7.setTextAlignment(Qt.AlignHCenter)
            self.infoModel.setItem(i,7,item7)
        self.infoview.setModel(self.infoModel)
    def cdloginevn(self):
        if self.countlinedit.text() == "" or self.cdpwdlinedit.text() == "":
            self.textbrowser.append(time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())+"请输入账号和密码！")
        else:
            self.textbrowser.append(time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())+"正在登陆茶蛋")
            self.cdlogin.setEnabled(False)
            self.cdloginevnn = cdlogin()
            self.cdloginevnn.complete.connect(self.cdloginevntips)
            windowliset.append(self.cdloginevnn)
            self.cdloginevnn.start()
    def cdloginevntips(self,bool):
        if bool and True:
            self.textbrowser.append(time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())+"茶蛋登陆成功")
            self.timer.start()
            self.cdlogin.close()
        else:
            self.textbrowser.append(time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())+"茶蛋登陆失败，请重新登陆")
            self.cdlogin.setEnabled(True)
    def menuaction(self,QAction):
        if QAction.text() == "网页登录导入":
            self.weblogindialog()
        if QAction.text() == "开始抽奖":
            prize = prizeDraw()
            windowliset.append(prize)
            prize.start()
            def input(text):
                self.textbrowser.append(text)
            prize.text.connect(input)
    def usermodel(self):
        self.usermodel=QStandardItemModel(self.databasevalue("local","select count(jd_pin) from jdusers")[0][0],4)
        #设置水平方向四个头标签文本内容
        self.usermodel.setHorizontalHeaderLabels(["序号","账号","登陆状态","是否启用"])
        for row in range(self.databasevalue("local","select count(jd_pin) from jdusers")[0][0]):
            item0 = QStandardItem("%s"%(row+1))
            item0.setTextAlignment(Qt.AlignHCenter)
            self.usermodel.setItem(row,0,item0)
            item1 = QStandardItem(self.databasevalue("local","select jd_pin from jdusers")[row][0])
            item1.setTextAlignment(Qt.AlignHCenter)
            self.usermodel.setItem(row,1,item1)
            item3 = self.databasevalue("local","select jd_name from jdusers")[row][0]
            if item3 == "1":
                item3 = "登陆成功"
            if item3 == "0":
                item3 = "登录失败"
            item3 = QStandardItem(item3)
            item3.setTextAlignment(Qt.AlignHCenter)
            self.usermodel.setItem(row,2,item3)
            i4 = str(self.databasevalue("local","select isUse from jdusers")[row][0])
            if i4 == "1":
                i4 = "已启用"
            if i4 =="0":
                i4 = "已停用"
            item4 = QStandardItem(i4)
            item4.setTextAlignment(Qt.AlignHCenter)
            self.usermodel.setItem(row,3,item4)
    def weblogindialog(self):
        self.weblogin = QDialog()
        self.weblogin.resize(400,650)
        self.weblogin.setWindowTitle("网页登录导入")
        glayout = QGridLayout()
        self.weblogin.setLayout(glayout)
        self.weblogin.setFixedSize(self.weblogin.width(),self.weblogin.height())
        self.weblogin.setWindowFlags(Qt.WindowCloseButtonHint)
        self.weblogin.setWindowModality(Qt.ApplicationModal)
        self.url_btn = QPushButton("京东首页")
        self.clean_btn = QPushButton("清除缓存")
        self.logined_btn = QPushButton("我已登录")
        self.web = MyWebEngineView()
        self.web.load(QUrl("https://plogin.m.jd.com/login/login"))
        glayout.addWidget(self.url_btn,1,1,1,1)
        glayout.addWidget(self.clean_btn,2,1,1,1)
        glayout.addWidget(self.logined_btn,1,2,2,1)
        glayout.addWidget(self.web,3,1,5,2)
        self.webdialogbtnevn()
        self.weblogin.show()
        windowliset.append(self.weblogin)
    def webdialogbtnevn(self):
        self.url_btn.clicked.connect(self.url_btn_evn)
        self.logined_btn.clicked.connect(self.logined_btn_evn)
        self.clean_btn.clicked.connect(self.clean_evn)
    def clean_evn(self):
        self.web.page().profile().cookieStore().deleteAllCookies()
        self.web.page().profile().clearHttpCache()
        QMessageBox.information(self,"清除","\n清除缓存，cookie成功\n",QMessageBox.Yes)
    def logined_btn_evn(self):
        if self.web.isloginsuccess():
            self.databasevalue("local","insert or replace into jdusers(jd_pin,jd_key) values('%s','%s')"%(self.web.cookies["pt_pin"],self.web.cookies["pt_key"]))
            self.web.page().profile().cookieStore().deleteAllCookies()
            self.web.page().profile().clearHttpCache()
            self.weblogin.close()
            self.freshuserview()
            self.getusername.start()
        else:QMessageBox.warning(self,"登陆","\n未查询到登录信息，请重新登陆！\n",QMessageBox.Yes)
    def url_btn_evn(self):
        self.web.load(QUrl("https://m.jd.com"))
    def databasevalue(self,select,sqlstr):
        if select == "local":
            localdatabase = sqlite3.connect("./db/db.users")
            cusor = localdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            localdatabase.commit()
            localdatabase.close()
            return value
        if select == "remote":
            remotdatabase = pymysql.connect(host = "1562800uq9.51mypc.cn",
                                            port = 26171,
                                            user = "root",
                                            passwd = "1111aaaa",
                                            db = "jd")
            cusor= remotdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            remotdatabase.commit()
            remotdatabase.close()
            return value
    def btnevn(self):
        self.startbtn.clicked.connect(self.workstart)
        self.stopbtn.clicked.connect(self.workstop)
        self.userview.customContextMenuRequested.connect(self.userevn)
    def freshuserview(self):
        self.usermodel=QStandardItemModel(self.databasevalue("local","select count(jd_pin) from jdusers")[0][0],4)
        #设置水平方向四个头标签文本内容
        self.usermodel.setHorizontalHeaderLabels(["序号","账号","登陆状态","是否启用"])
        for row in range(self.databasevalue("local","select count(jd_pin) from jdusers")[0][0]):
            item0 = QStandardItem("%s"%(row+1))
            item0.setTextAlignment(Qt.AlignHCenter)
            self.usermodel.setItem(row,0,item0)
            item1 = QStandardItem(self.databasevalue("local","select jd_pin from jdusers")[row][0])
            item1.setTextAlignment(Qt.AlignHCenter)
            self.usermodel.setItem(row,1,item1)
            item3 = self.databasevalue("local","select jd_name from jdusers")[row][0]
            if item3 == "1":
                item3 = "登陆成功"
            if item3 == "0":
                item3 = "登录失败"
            item3 = QStandardItem(item3)
            item3.setTextAlignment(Qt.AlignHCenter)
            self.usermodel.setItem(row,2,item3)
            i4 = str(self.databasevalue("local","select isUse from jdusers")[row][0])
            if i4 == "1":
                i4 = "已启用"
            if i4 =="0":
                i4 = "已停用"
            item4 = QStandardItem(i4)
            item4.setTextAlignment(Qt.AlignHCenter)
            self.usermodel.setItem(row,3,item4)
        self.userview.setModel(self.usermodel)
    def userevn(self):
        row = -1
        if self.userview.currentIndex().row != -1:
            row = self.userview.currentIndex().row()
        self.usermenu = QMenu(self.userview)
        self.usermenu.addAction("启用该账号")
        self.usermenu.addAction("停用该账号")
        self.usermenu.addAction("进入个人中心")
        self.usermenu.addAction("刷新账号列表")
        self.usermenu.addAction("删除当前账号")
        self.usermenu.move(QCursor.pos())
        self.usermenu.show()
        self.usermenu.triggered.connect(self.usermenuevn)
    def usermenuevn(self,QAction):
        if QAction.text() == "刷新账号列表":
            self.freshuserview()
            self.textbrowser.append("<font color=\"#006400\">" + time.strftime("%Y-%m-%d %H:%M:%S\t",time.localtime()) + "刷新账号列表成功" "</font> ")
        if QAction.text() == "删除当前账号":
            self.textbrowser.append("<font color=\"#A52A2A\">" + time.strftime("%Y-%m-%d %H:%M:%S\t",time.localtime()) + "删除账号【%s】成功" "</font> "%(self.databasevalue("local","select * from jdusers")[self.userview.currentIndex().row()][0]))
            self.databasevalue("local","delete from jdusers where jd_pin = '%s'"%(self.databasevalue("local","select * from jdusers")[self.userview.currentIndex().row()][0]))
            self.freshuserview()
        if QAction.text() == "进入个人中心":
            global  rownumweb
            rownumweb = self.userview.currentIndex().row()
            loginevn = cocuntlogin()
            windowliset.append(loginevn)
            loginevn.start()
        if QAction.text() == "启用该账号":
            count = self.usermodel.item(self.userview.currentIndex().row(),1).text()
            self.databasevalue("local",'update jdusers set isUse = 1 where jd_pin = "%s"'%(count))
            self.freshuserview()
            self.textbrowser.append(time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())+"已启用"+count)
        if QAction.text() == "停用该账号":
            count = self.usermodel.item(self.userview.currentIndex().row(),1).text()
            self.databasevalue("local",'update jdusers set isUse = 0 where jd_pin = "%s"'%(count))
            self.freshuserview()
            self.textbrowser.append(time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())+"已停用"+count)
    def workstart(self):
        global isstop
        isstop = False
        self.startbtn.hide()
        self.conculatmethod()
        self.stopbtn.show()
    def conculatmethod(self):
        tee = mainRun()
        windowliset.append(tee)
        tee.start()
        def puttext(text):
            self.textbrowser.append(time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())+text)
        tee.singnal.connect(puttext)
        tee.refresh.connect(lambda :self.orderform())

    def workstop(self):
        self.stopbtn.hide()
        self.startbtn.show()
        global  isstop
        isstop = True
    def closeEvent(self,QCloseEvent):
        MSG = QMessageBox.question(self,"退出","\n是否退出？\n",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if MSG == QMessageBox.Yes:
            pass
        if MSG == QMessageBox.No:
            QCloseEvent.ignore()

#保留函数，未来进一步开发
class browser(QWidget):
    def __init__(self):
        super(browser, self).__init__()
        self.initUI()
    def initUI(self):
        self.setWindowTitle("京东账号登陆")
        self.setWindowFlags(Qt.WindowMinimizeButtonHint|Qt.WindowCloseButtonHint)
        self.resize(400,800)
        self.setFixedSize(self.width(),self.height())
        self.glayout = QGridLayout()
        self.setLayout(self.glayout)
        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://m.jd.com"))
        self.browser.page().profile().cookieStore().deleteAllCookies()
        self.glayout.addWidget(self.browser)
        windowliset.append(self)
class cdlogin(QThread):
    complete = pyqtSignal(bool)
    timerstart = pyqtSignal()
    def __init__(self):
        super(cdlogin, self).__init__()
    def run(self):
        chropt = ChromeOptions()
        chropt.add_argument("User-Agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36")
        chropt.add_argument("lang=zh_CN.UTF-8")
        mobileEmulation = {'deviceName': 'iPhone X'}
        chropt.add_experimental_option("mobileEmulation",mobileEmulation)
        prefs = {"profile.managed_default_content_settings.images": 2}
        chropt.add_experimental_option("prefs", prefs)
        chropt.add_argument("--headless")
        chrome = Chrome(options=chropt)
        # chrome.set_window_size(400,800)
        chrome.get("http://chadan.wang/wang/login")
        chrome.implicitly_wait(120)
        chrome.find_element_by_xpath("/html/body/div[3]/div[1]/label[1]/input").clear()
        chrome.find_element_by_xpath("/html/body/div[3]/div[1]/label[1]/input").send_keys(loginwin.mainwin.countlinedit.text())
        chrome.find_element_by_xpath("/html/body/div[3]/div[1]/label[2]/input").clear()
        chrome.find_element_by_xpath("/html/body/div[3]/div[1]/label[2]/input").send_keys(loginwin.mainwin.cdpwdlinedit.text())
        time.sleep(1)
        chrome.find_element_by_xpath("/html/body/div[3]/button").click()
        time.sleep(2)
        if chrome.title == "茶蛋":
            WebDriverWait(120,0.5).until(EC.title_is,"茶蛋")
            with open("./db/cdck.users","w",encoding="utf-8") as f:
                for cookie in chrome.get_cookies():
                    f.write(cookie["name"]+"="+cookie["value"]+"\n")
                    f.write("domain="+cookie["domain"]+"\n")
                f.close()
            chrome.quit()
            self.complete.emit(True)
            self.timerstart.emit()
        else:
            chrome.quit()
            self.complete.emit(False)
class cocuntlogin(QThread):
    def __init__(self):
        super(cocuntlogin, self).__init__()
    def run(self):
        cookies = []
        cookies.append(dict(name = "pt_pin",value = self.databasevalue("local","select * from jdusers")[rownumweb][0],path = "/",domain = ".jd.com"))
        cookies.append(dict(name = "pt_key",value = self.databasevalue("local","select * from jdusers")[rownumweb][1],path = "/",domain = ".jd.com"))
        chropt = ChromeOptions()
        chropt.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36")
        self.chrome = Chrome(options=chropt)
        self.chrome.set_window_size(400,800)
        self.chrome.implicitly_wait(120)
        self.chrome.get("https://m.jd.com")
        self.chrome.delete_all_cookies()
        for cookie in cookies:
            self.chrome.add_cookie(cookie)
        self.chrome.get("https://m.jd.com")
        self.chrome.implicitly_wait(120)
        self.chrome.get("https://home.m.jd.com/")
    def databasevalue(self,select,sqlstr):
        if select == "local":
            localdatabase = sqlite3.connect("./db/db.users")
            cusor = localdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            localdatabase.commit()
            localdatabase.close()
            return value
        if select == "remote":
            remotdatabase = pymysql.connect(host = "1562800uq9.51mypc.cn",
                                            port = 26171,
                                            user = "root",
                                            passwd = "1111aaaa",
                                            db = "jd")
            cusor= remotdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            remotdatabase.commit()
            remotdatabase.close()
            return value

class MyWebEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(MyWebEngineView, self).__init__(*args, **kwargs)
        # 绑定cookie被添加的信号槽
        QWebEngineProfile.defaultProfile().cookieStore().cookieAdded.connect(self.onCookieAdd)
        self.cookies = {}          # 存放cookie字典

    def onCookieAdd(self, cookie):                       # 处理cookie添加的事件
        name = cookie.name().data().decode('utf-8')     # 先获取cookie的名字，再把编码处理一下
        value = cookie.value().data().decode('utf-8')   # 先获取cookie值，再把编码处理一下
        self.cookies[name] = value                       # 将cookie保存到字典里

    # 获取cookie
    def get_cookie(self):
        cookie_str = ''
        for key, value in self.cookies.items():         # 遍历字典
            cookie_str += (key + ':' + value + ';')     # 将键值对拿出来拼接一下
        return cookie_str
    def isloginsuccess(self):
        if "pt_pin" and "pt_key" in self.cookies:
            return True
        return False
class getusername(QThread):
    complete = pyqtSignal()
    def __init__(self):
        super(getusername, self).__init__()
    def run(self):
        users = self.databasevalue("local",'select jd_pin,jd_key from jdusers')
        for i in users:
            self.bro(i[0],i[1])
    def bro(self,pt_pin,pt_key):
        headers = {
            "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36"
        }
        s = requests.Session()
        s.headers = headers
        cookiejar = requests.cookies.RequestsCookieJar()
        cookiejar.set("pt_pin",pt_pin,domain = ".jd.com")
        cookiejar.set("pt_key",pt_key,domain = ".jd.com")
        s.cookies = cookiejar
        req = s.get("https://home.m.jd.com/myJd/newhome.action")
        req.encoding = "utf-8"
        text = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><link rel=icon href=//m.jd.com/favicon.ico type=image/x-icon><title></title><link href=//h5.360buyimg.com/h5/login_v1.0.6/static/css/app.fac3e8fc585d25dfcd3612a7cbcdc22d.css rel=stylesheet></head><body><div id=app></div><script type=text/javascript src=//h5.360buyimg.com/h5/login_v1.0.6/static/js/manifest.7ce7bfe45323ac6db37d.js></script><script type=text/javascript src=//h5.360buyimg.com/h5/login_v1.0.6/static/js/vendor.edc1f732946bb2cfdcb3.js></script><script type=text/javascript src=//h5.360buyimg.com/h5/login_v1.0.6/static/js/app.0db8a3a7f8da9b64931f.js></script></body><script src=//wl.jd.com/unify.min.js></script><script src="//h5.360buyimg.com/ws_js/jdwebm.js?v=mregister"></script><script src=//payrisk.jd.com/m.html></script><script src=//payrisk.jd.com/js/m.js></script><script src=//h5.360buyimg.com/h5/jd-login/js/report.min.js></script><script src=//h5.360buyimg.com/login/js/common_mlogin_v20190402.js></script><script type=text/javascript>try{
        MPing.inputs.Click.attachEvent();
    }catch(e){}</script></html>"""
        if req.text == text:
            self.databasevalue("local","update jdusers set jd_name = '0',isUse = 0 where jd_pin = '%s'"%(pt_pin))
            self.complete.emit()
        else:
            self.databasevalue("local","update jdusers set jd_name = '1',isUse = 1 where jd_pin = '%s'"%(pt_pin))
            self.complete.emit()
    def databasevalue(self,select,sqlstr):
        if select == "local":
            localdatabase = sqlite3.connect("./db/db.users")
            cusor = localdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            localdatabase.commit()
            localdatabase.close()
            return value
        if select == "remote":
            remotdatabase = pymysql.connect(host = "1562800uq9.51mypc.cn",
                                            port = 26171,
                                            user = "root",
                                            passwd = "1111aaaa",
                                            db = "jd")
            cusor= remotdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            remotdatabase.commit()
            remotdatabase.close()
            return value
class mainRun(QThread):
    singnal = pyqtSignal(str)
    refresh = pyqtSignal()
    cdorderid = ""
    jdorderid = ""
    def __init__(self):
        super(mainRun, self).__init__()
    def run(self):
        global isstop
        for i in self.databasevalue("local",'select jd_pin,jd_key from jdusers where isUse = 1'):#第一层循环，根据账号数量循环次数
            timenum = 0
            while True:#第二层循环，按照每个账号19单的限制循环
                if isstop:
                    break
                num = str(self.getnumber())
                self.updatecdorderstat()
                self.refresh.emit()
                if len(num) != 11:#获取订单号码失败的情况下进入循环
                    while isstop == False:
                        time.sleep(3)
                        num = str(self.getnumber())
                        if len(num) != 11:
                            self.updatecdorderstat()
                            self.singnal.emit(num)
                        if len(str(num)) == 11:
                            break
                if len(num) == 11:#成功获取到订单手机号码
                    self.cdorderstat(self.cdorderid)
                    self.updatecdorderstat()
                    self.refresh.emit()
                    jdcomitstst = self.jdordercomit(num,i[0],i[1],self.cdorderid)#提交京东充值订单
                    self.updatecdorderstat()
                    self.refresh.emit()
                    if jdcomitstst != 1:#提交失败的处理
                        while True:
                            time.sleep(2)
                            jdcomitstst = self.jdordercomit(num,i[0],i[1],self.cdorderid)
                            self.updatecdorderstat()
                            self.refresh.emit()
                            if jdcomitstst != 1:
                                self.singnal.emit(jdcomitstst)
                            else:
                                break
                    else:#京东订单提交成功的处理
                        jdorderstat = self.jdoderstat(i[0],i[1],self.jdorderid)
                        self.updatecdorderstat()
                        self.refresh.emit()
                        if jdorderstat == "等待付款":
                            while True:
                                time.sleep(2)
                                jdorderstat = self.jdoderstat(i[0],i[1],self.jdorderid)
                                self.refresh.emit()
                                if jdorderstat == "充值成功" or jdorderstat == "正在充值":
                                    break
                        else:
                            break
                comitstat = self.commitcdorder(self.cdorderid)
                if comitstat != 1:
                    while True:
                        time.sleep(2)
                        comitstat = self.commitcdorder(self.cdorderid)
                        self.refresh.emit()
                        if comitstat != 1:
                            self.updatecdorderstat()
                            self.singnal.emit(comitstat)
                        else:
                            break
                else:
                    self.databasevalue("local",'update products set JDinformationstat = "%s" where id = %s'%(str(self.jdoderstat(i[0],i[1],self.jdorderid)),str(self.cdorderid)))
                    time.sleep(1)
                    self.cdorderstat(self.cdorderid)
                    timenum += 1
                if timenum >= 19:
                    break
            self.refresh.emit()
            if isstop:
                break
    def updatecdorderstat(self):
        orders = self.databasevalue("local",'select id from products where orderStatus = "6" or orderStatus = "1"')
        for i in orders:
            self.cdorderstat(i[0])
    def getnumber(self):
        headers = {
            "Origin": "http://chadan.wang",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        with open("./db/cdck.users") as f:
            k = f.read()
            f.close()
        jessionid = re.findall("logged=(.*?)\n",k)
        s = requests.Session()
        cookiejar = requests.cookies.RequestsCookieJar()
        s.cookies = cookiejar
        s.headers = headers
        data = {
            "JSESSIONID": jessionid,
            "productId": "8",
            "shopId": "72",
            "shopName": "京东话费",
            "amount": "1",
            "cardType": "1"
        }
        req = s.post("http://api.chadan.cn/order/other/getJdOtherOrder",data = data)
        head = ""
        values = ""
        if str(req.text) == '{"errorCode":201,"errorMsg":"店铺名称验证不正确!","expire":null}':
            return "茶蛋话费未上架，请稍后重试！"
        else:
            if req.text == '{"errorCode":4002,"errorMsg":"订单列表未完成订单完成后可以获取","expire":null}':
                return "订单列表存在未完成订单，完成后可以获取，请到茶蛋订单中心手动提交订单！"
            if req.text == "{'errorCode': 4003, 'errorMsg': '获取频繁,请稍后再试', 'expire': None}":
                return "获取订单频繁,请稍后再试！"
            if req.json()["errorCode"] == 200:
                for i in req.json()["data"]:
                    for j in i:
                        head += "'"+j+"',"
                        values += "'"+str(i[j])+"',"
            else:
                return str(req.json()["errorMsg"])
            self.cdorderid = req.json()["data"][0]["id"]
            self.databasevalue("local","insert or replace into products(%s) values(%s)"%(head[0:len(head)-1],values[0:len(values)-1]))
            return str(req.json()["data"][0]["cardNumber"])
    def cdorderstat(self,cdorderid):
        headers = {
            "Origin": "http://chadan.wang",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        with open("./db/cdck.users") as f:
            k = f.read()
            f.close()
        jessionid = re.findall("logged=(.*?)\n",k)
        data = {
            "JSESSIONID": jessionid,
            "id":cdorderid
        }
        s = requests.Session()
        cookiejar = requests.cookies.RequestsCookieJar()
        s.cookies = cookiejar
        s.headers = headers
        req = s.post("http://api.chadan.cn/order/other/getOtherOrder",data = data)
        for i in req.json()["data"]:
            self.databasevalue("local",'update products set %s = "%s" where id = %s'%(str(i),str(req.json()["data"][i]),cdorderid))
        getpricedata = {}
        getpricedata["getOtherType"] = "true"
        getpricedata["JSESSIONID"] = re.findall("logged=(.*?)\n",k)[0]
        s = s.post("http://api.chadan.cn/order/other/getValidProduct",data = getpricedata)
        try:
            CDprice = re.findall('"结算价：(.*?)元",',s.text)[0]
            self.databasevalue("local",'update products set CDprice = "%s" where id = %s'%(CDprice,cdorderid))
        except Exception as err:
            pass
    def jdordercomit(self,num,pt_pin,pt_key,cdorderid):
        headers = {
            "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36"
        }
        s = requests.Session()
        s.headers = headers
        cookiejar = requests.cookies.RequestsCookieJar()
        cookiejar.set("pt_pin",pt_pin,domain = ".jd.com")
        cookiejar.set("pt_key",pt_key,domain = ".jd.com")
        s.cookies = cookiejar
        req = s.get("https://newcz.m.jd.com/")
        csrfToken = re.findall('<input type="hidden" id="csrfToken" value="(.*?)"/>',req.text)[0]
        data = {
            "mobile":num
        }
        req = s.post("https://newcz.m.jd.com/newcz/product.json",data=data)
        for i in req.json()["skuPrice"]["skuList"]:
            if i["facePrice"] == "100":
                jdprice = i['jdPrice']
                faceprice = i['facePrice']
                skuid = i['skuId']
            #https://newcz.m.jd.com/newcz/submitOrder.action?mobile=17551592843&newSkuId=1000523811&orderPrice=9990&onlinePay=99.90&skuId=100&origin=&csrfToken=ffa6c1c73eb64e7cb6f288e653ef93bc&loginStatus=true
        url = "https://newcz.m.jd.com/newcz/submitOrder.action?mobile=" + str(num) + "&newSkuId=" + str(skuid) + "&orderPrice=" + str(jdprice) + "&onlinePay=" + str(jdprice/100) + "&skuId=" + str(faceprice) + "&origin=&csrfToken=" + csrfToken
        req = s.get(url)
        try:
            JDinformation = re.findall('<input type="hidden" id="orderId" value="(.*?)" />',req.text)[0]
            url = "https://newcz.m.jd.com/newcz/detail.action?orderId="+str(JDinformation)+"&channel="
            req = s.get(url)
            JDinformationstat = re.findall('<span class="details-status">(.*?)</span>',req.text)[0]
            JDinformationinfo = re.findall('<span class="area">归属地区：(.*?)</span>',req.text)[0]
            JDpaymoney = re.findall('<span class="amount-box">实付款：<em class="yen">&yen;</em><em class="yen-int">(.*?)</em></span>',req.text)[0]
            JDcount = str(pt_pin)
            self.databasevalue('local','update products set JDinformation="%s",JDinformationstat="%s",JDinformationinfo="%s",JDpaymoney="%s",JDcount="%s" where id = "%s"'%(JDinformation,JDinformationstat,JDinformationinfo,JDpaymoney,JDcount,cdorderid))
            self.jdorderid = JDinformation
            return 1
        except Exception as err:
            return err
    def jdoderstat(self,pt_pin,pt_key,orderid):
        headers = {
            "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36"
        }
        s = requests.Session()
        s.headers = headers
        cookiejar = requests.cookies.RequestsCookieJar()
        cookiejar.set("pt_pin",pt_pin,domain = ".jd.com")
        cookiejar.set("pt_key",pt_key,domain = ".jd.com")
        s.cookies = cookiejar
        url = "https://newcz.m.jd.com/newcz/detail.action?orderId="+orderid+"&channel="
        req = s.get(url)
        req.encoding = "utf-8"
        return re.findall('<span class="details-status">(.*?)</span>',req.text)[0]
    def commitcdorder(self,cdoderid):
        headers = {
            "Origin": "http://chadan.wang",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        with open("./db/cdck.users") as f:
            k = f.read()
            f.close()
        jessionid = re.findall("logged=(.*?)\n",k)
        s = requests.Session()
        cookiejar = requests.cookies.RequestsCookieJar()
        s.cookies = cookiejar
        s.headers = headers
        data = {
            "JSESSIONID": jessionid,
            "id": cdoderid,
            "orderStatus": "3",
            "cardType": "1"
        }
        req = s.post("http://api.chadan.cn/order/other/reportJdHf",data = data)
        if req.json()["errorCode"] == 4000:
            return "请先去店铺支付成功再上报"
        if req.json()["errorCode"] == 200:
            return 1
    def databasevalue(self,select,sqlstr):
        if select == "local":
            localdatabase = sqlite3.connect("./db/db.users")
            cusor = localdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            localdatabase.commit()
            localdatabase.close()
            return value
        if select == "remote":
            remotdatabase = pymysql.connect(host = "1562800uq9.51mypc.cn",
                                            port = 26171,
                                            user = "root",
                                            passwd = "1111aaaa",
                                            db = "jd")
            cusor= remotdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            remotdatabase.commit()
            remotdatabase.close()
            return value

class prizeDraw(QThread):
    text = pyqtSignal(str)
    def __init__(self):
        super(prizeDraw, self).__init__()
    def run(self):
        users = self.databasevalue("local",'select jd_pin,jd_key from jdusers where jd_name = "1"')
        for i in users:
            self.bro(i[0],i[1])
    def bro(self,pt_pin,pt_key):
            headers = {
                "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36"
            }
            self.s = requests.Session()
            self.s.headers = headers
            cookiejar = requests.cookies.RequestsCookieJar()
            cookiejar.set("pt_pin",pt_pin,domain = ".jd.com")
            cookiejar.set("pt_key",pt_key,domain = ".jd.com")
            self.s.cookies = cookiejar
            chancedata = {
                "activityId": "6626",
                "businessType": -119
            }
            startdata = {
                "activityId": 6626,
                "businessType": -119
            }
            chance = self.s.post("https://luck.m.jd.com/index/getChance.json?random=1584755329662",data = chancedata)
            text = "账号："+chance.json()["chance"]["userPin"]+", 共"+str(chance.json()["chance"]["chance"])+"次抽奖机会"
            self.text.emit(text)
            prize = 0
            for i in range(chance.json()["chance"]["chance"]):
                req = self.s.post("https://luck.m.jd.com/index/play.json",data = startdata)
                if req.json()["prize"]["id"] != 0:
                    prize += 1
            text = "共抽奖"+str(chance.json()["chance"]["chance"])+"次，中奖"+str(prize)+"次"
            self.text.emit(text)

    def databasevalue(self,select,sqlstr):
        if select == "local":
            localdatabase = sqlite3.connect("./db/db.users")
            cusor = localdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            localdatabase.commit()
            localdatabase.close()
            return value
        if select == "remote":
            remotdatabase = pymysql.connect(host = "1562800uq9.51mypc.cn",
                                            port = 26171,
                                            user = "root",
                                            passwd = "1111aaaa",
                                            db = "jd")
            cusor= remotdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            remotdatabase.commit()
            remotdatabase.close()
            return value
class freshorderstat(QThread):
    def __init__(self):
        super(freshorderstat, self).__init__()
    def run(self):
        orders = self.databasevalue("local",'select id from products where orderStatus = "6" or orderStatus = "1"')
        for i in orders:
            self.cdorderstat(i[0])
    def cdorderstat(self,cdorderid):
        headers = {
            "Origin": "http://chadan.wang",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        with open("./db/cdck.users") as f:
            k = f.read()
            f.close()
        jessionid = re.findall("logged=(.*?)\n",k)
        data = {
            "JSESSIONID": jessionid,
            "id":cdorderid
        }
        s = requests.Session()
        cookiejar = requests.cookies.RequestsCookieJar()
        s.cookies = cookiejar
        s.headers = headers
        req = s.post("http://api.chadan.cn/order/other/getOtherOrder",data = data)
        for i in req.json()["data"]:
            self.databasevalue("local",'update products set %s = "%s" where id = %s'%(str(i),str(req.json()["data"][i]),cdorderid))
        getpricedata = {}
        getpricedata["getOtherType"] = "true"
        getpricedata["JSESSIONID"] = re.findall("logged=(.*?)\n",k)[0]
        s = s.post("http://api.chadan.cn/order/other/getValidProduct",data = getpricedata)
        try:
            CDprice = re.findall('"结算价：(.*?)元",',s.text)[0]
            self.databasevalue("local",'update products set CDprice = "%s" where id = %s'%(CDprice,cdorderid))
        except Exception as err:
            pass
    def databasevalue(self,select,sqlstr):
        if select == "local":
            localdatabase = sqlite3.connect("./db/db.users")
            cusor = localdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            localdatabase.commit()
            localdatabase.close()
            return value
        if select == "remote":
            remotdatabase = pymysql.connect(host = "1562800uq9.51mypc.cn",
                                            port = 26171,
                                            user = "root",
                                            passwd = "1111aaaa",
                                            db = "jd")
            cusor= remotdatabase.cursor()
            cusor.execute(sqlstr)
            value = cusor.fetchall()
            remotdatabase.commit()
            remotdatabase.close()
            return value

if __name__ == '__main__':

#调试完成后正式代码
    app = QApplication(sys.argv)
    loginwin = loginwin()
    loginwin.show()
    windowliset = []
    sys.exit(app.exec_())

# # # #调试代码
#     app = QApplication(sys.argv)
#     windowliset = []
#     mainwin = mainwin()
#     mainwin.show()
#     sys.exit(app.exec_())