from tkinter import *
from view import *  # 菜单栏对应的各个子页面


class MainPage(object):
    def __init__(self, master=None,usr_name="",im = None,pri = None):
        self.root = master  # 定义内部变量root
        self.root.geometry('650x400')  # 设置窗口大小
        self.usr_name = usr_name
        self.im = im
        self.privkey = pri
        self.createPage()

    def createPage(self):

        self.mainPage = MainFrame(self.root,self.im) # 创建不同Frame
        self.infoPage = InfoFrame(self.root,self.usr_name,self.privkey)
        self.queryPage = QueryFrame(self.root,self.usr_name,self.privkey)
        self.tranctionPage = TranctionFrame(self.root,self.usr_name,self.privkey)
        self.digPage = DigFrame(self.root,self.usr_name,self.privkey)
        self.mainPage.pack()  # 默认显示数据录入界面
        menubar = Menu(self.root,font=("Arial", 20))
        menubar.add_command(label='个人信息', command=self.infoData)
        menubar.add_command(label='钱包余额', command=self.queryData)
        menubar.add_command(label='交易', command=self.tranction)
        menubar.add_command(label='挖矿', command=self.aboutDisp)
        self.root['menu'] = menubar  # 设置菜单栏

    def infoData(self):
        self.mainPage.pack_forget()
        self.infoPage.pack()
        self.queryPage.pack_forget()
        self.tranctionPage.pack_forget()
        self.digPage.pack_forget()


    def queryData(self):
        self.mainPage.pack_forget()
        self.infoPage.pack_forget()
        self.queryPage.pack()
        self.tranctionPage.pack_forget()
        self.digPage.pack_forget()
        self.queryPage.change()
        self.queryPage.tranc_update()

    def tranction(self):
        self.mainPage.pack_forget()
        self.infoPage.pack_forget()
        self.queryPage.pack_forget()
        self.tranctionPage.pack()
        self.digPage.pack_forget()

    def aboutDisp(self):
        self.mainPage.pack_forget()
        self.infoPage.pack_forget()
        self.queryPage.pack_forget()
        self.tranctionPage.pack_forget()
        self.digPage.pack()