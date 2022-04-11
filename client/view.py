from tkinter import *
from tkinter.messagebox import *
import socket
import threading
import hashlib
import time
import rsa
import base64
from tkinter.ttk import Treeview

port = 3331

with open('public.pem', 'rb') as publickfile:
    p = publickfile.read()
pubkey = rsa.PublicKey.load_pkcs1(p)#服务器的公钥


def timestamp2time(timestamp):
    """
    时间戳转为格式化的时间字符串
    :param timestamp:
    :return: 格式化的时间字符串
    """
    time_array = time.localtime(timestamp)
    mytime = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return mytime

def dec(mes,privkey):
    text = []
    for i in range(0,len(mes),128):
        cont = mes[i:i+128]
        text.append(rsa.decrypt(cont,privkey))
    text = b''.join(text)
    return text.decode()

class MainFrame(Frame):
    def __init__(self, master=None,im = None,pri=None):
        Frame.__init__(self, master)
        self.im = im
        self.createPage()

    def createPage(self):
        Label(self, text='基于区块链的交易系统').pack()
        self.c = Canvas(self,
                        width=500,  # 指定Canvas组件的宽度
                        height=330,  # 指定Canvas组件的高度
                        bg='white')  # 指定Canvas组件的背景色
        # im = PhotoImage(file='fengmian.gif')     # 使用PhotoImage打开图片

        self.c.create_image(250, 165, image=self.im)  # 使用create_image将图片添加到Canvas组件中
        self.c.pack()


class InfoFrame(Frame):  # 继承Frame类
    def __init__(self, master=None,usr_name="",pri=None):
        Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.usr_name = usr_name
        self.privkey = pri
        self.name = StringVar()
        self.male = StringVar()
        self.bornDate = StringVar()
        self.deductPrice = StringVar()
        self.createPage()

    def createPage(self):
        mes="03"+self.usr_name
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 7929))
        mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
        client.send(mes)
        data = client.recv(1024)
        data = rsa.decrypt(data,self.privkey).decode()
        client.close()
        self.name.set(data.split("**", 3)[0])
        self.male.set(data.split("**", 3)[1])
        self.bornDate.set(data.split("**", 3)[2])
        Label(self,text='个人信息').grid(row=0, stick=E, pady=10)
        Label(self, text='Account: ').grid(row=1, stick=W, pady=10)
        Label(self, text=self.usr_name).grid(row=1, column=1,stick=W)
        Label(self, text='Name: ').grid(row=2, stick=W, pady=10)
        Label(self, textvariable=self.name).grid(row=2, column=1, stick=W)
        Label(self, text='Gender: ').grid(row=3, stick=W, pady=10)
        Label(self, textvariable=self.male).grid(row=3, column=1, stick=W)
        Label(self, text='Birthday： ').grid(row=4, stick=W, pady=10)
        Label(self, textvariable=self.bornDate).grid(row=4, column=1, stick=W)
        Button(self, text='Modify',command = self.change).grid(row=6, column=1, stick=E, pady=10)

    def change(self):
        def change_info():
            nname = new_name.get()
            nmale = new_male.get()
            nborndate = new_bornDate.get()
            mes = "04" + self.usr_name +"**"+ nname +"**"+ nmale +"**"+ nborndate
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 7929))
            mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
            client.send(mes)
            client.close()
            self.name.set(nname)
            self.male.set(nmale)
            self.bornDate.set(nborndate)
            window_change.destroy()

        def quit_change():
            window_change.destroy()

        window_change = Toplevel(self.root)
        window_change.geometry('350x200')
        window_change.title('Change info')

        new_name = StringVar()
        new_name.set(self.name.get())
        Label(window_change, text='Name:').place(x=10, y=10)
        entry_new_name = Entry(window_change, textvariable=new_name)
        entry_new_name.place(x=150, y=10)

        new_male = StringVar()
        new_male.set(self.male.get())
        Label(window_change, text='Gender：').place(x=10, y=50)
        entry_new_pwd = Entry(window_change, textvariable=new_male)
        entry_new_pwd.place(x=150, y=50)

        new_bornDate = StringVar()
        new_bornDate.set(self.bornDate.get())
        Label(window_change, text='Birthday:').place(x=10, y=90)
        entry_comfirm_sign_up = Entry(window_change, textvariable=new_bornDate)
        entry_comfirm_sign_up.place(x=150, y=90)

        btn_comfirm_sure = Button(window_change, text='Sure', command=change_info)
        btn_comfirm_sure.place(x=150, y=130)
        btn_comfirm_sure = Button(window_change, text='Quit', command=quit_change)
        btn_comfirm_sure.place(x=270, y=130)


class QueryFrame(Frame):  # 继承Frame类
    def __init__(self, master=None,usr_name="",pri=None):
        Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.usr_name = usr_name
        self.privkey = pri
        self.balance = StringVar()
        self.tranc_list_tree = self.createPage()

    def createPage(self):
        Label(self, text='钱包').pack()
        mes = "06" + self.usr_name
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 7929))
        mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
        client.send(mes)
        data = client.recv(1024)
        data = rsa.decrypt(data, self.privkey).decode()
        client.close()
        self.balance.set("尊敬的"+self.usr_name+"用户，您的余额为："+data)
        Label(self, textvariable=self.balance).pack()
        Label(self,text='').pack()
        Label(self,text='交易明细').pack()
        # 交易记录列表区
        tranc_list_frame = Frame(self)
        tranc_list_sub_frame = Frame(tranc_list_frame)
        tranc_list_tree = Treeview(tranc_list_sub_frame, selectmode='browse')
        tranc_list_tree.bind('<<TreeviewSelect>>')
        # 交易记录列表垂直滚动条
        tranc_list_vscrollbar = Scrollbar(tranc_list_sub_frame, orient="vertical", command=tranc_list_tree.yview)
        tranc_list_vscrollbar.pack(side=RIGHT, fill=Y, expand=YES)
        tranc_list_tree.configure(yscrollcommand=tranc_list_vscrollbar.set)
        tranc_list_sub_frame.pack(side=TOP, fill=BOTH, expand=YES)
        # 交易记录列表区列标题
        tranc_list_tree["columns"] = ("No.", "Time", "From", "To", "Amount","Info")
        tranc_list_column_width = [40, 160, 90, 90, 70,120]
        tranc_list_tree['show'] = 'headings'
        for column_name, column_width in zip(tranc_list_tree["columns"], tranc_list_column_width):
            tranc_list_tree.column(column_name, width=column_width, anchor='w')
            tranc_list_tree.heading(column_name, text=column_name)
        tranc_list_tree.pack(side=LEFT, fill=X, expand=YES)
        tranc_list_frame.pack(side=TOP, fill=X, padx=5, pady=5, expand=YES, anchor='n')
        return tranc_list_tree

    def tranc_update(self):
        self.tranc_list_tree.delete(*self.tranc_list_tree.get_children())
        mes = "07" + self.usr_name
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 7929))
        mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
        client.send(mes)
        data = client.recv(10240)
        data = dec(data,self.privkey)
        client.close()
        t = int(data.split("???",2)[0])
        i = 0
        while i < t:
            i = i + 1
            tranc_mes = data.split("???",t+1)[i]
            tranc_time = tranc_mes.split("**",4)[0]
            tranc_from = tranc_mes.split("**",4)[1]
            tranc_to = tranc_mes.split("**",4)[2]
            tranc_amount = tranc_mes.split("**",4)[3]
            tranc_info = ""
            if tranc_from == "None"  and tranc_amount =="10":
                tranc_info = "Dig reward"
            elif tranc_from == "None" and tranc_amount == "100":
                tranc_info = "Initial funding"
            elif tranc_from == self.usr_name:
                tranc_info = "Spending"
            elif tranc_to == self.usr_name:
                tranc_info = "Obtain"
            self.tranc_list_tree.insert("", 'end', values=(i, tranc_time, tranc_from, tranc_to, tranc_amount,tranc_info))

    def change(self):
        mes = "06" + self.usr_name
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 7929))
        mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
        client.send(mes)
        data = client.recv(1024)
        data = rsa.decrypt(data, self.privkey).decode()
        client.close()
        self.balance.set("尊敬的"+self.usr_name+"用户，您的余额为："+data)


class TranctionFrame(Frame):  # 继承Frame类
    def __init__(self, master=None,usr_name="",pri=None):
        Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.usr_name = usr_name
        self.privkey = pri
        self.name = StringVar()
        self.money = StringVar()
        self.createPage()

    def createPage(self):
        Label(self, text='交易界面').grid(row=0,column=1, pady=10)
        Label(self).grid(row=1, stick=W, pady=10)
        Label(self, text='交易账号: ').grid(row=2, stick=W, pady=10)
        Entry(self, textvariable=self.name).grid(row=2, column=1, stick=E)
        Label(self, text='交易金额: ').grid(row=3, stick=W, pady=10)
        Entry(self, textvariable=self.money).grid(row=3, column=1, stick=W)

        Button(self, text='Sure',command=self.trans).grid(row=6, column=1, stick=E, pady=10)

    def trans(self):
        gname = self.name.get()
        gmoney = self.money.get()
        mes = self.usr_name+"**"+gname+"**"+gmoney
        print("交易信息："+mes)
        signature = rsa.sign(mes.encode('utf-8'), self.privkey, 'SHA-256')
        print("签名为：")
        print(signature)
        mes = "05"+mes
        print(mes)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 7929))
        encrypt_text = []
        for i in range(0, len(mes), 100):
            cont = mes[i:i + 100]
            encrypt_text.append(rsa.encrypt(cont.encode('utf-8'),pubkey))
        mes = b''.join(encrypt_text)
        print("加密后：")
        print(mes)
        client.send(mes)
        time.sleep(0.05)
        client.send(signature)
        data = client.recv(1024).decode()
        client.close()
        if (data == 'success'):
            messagebox.showinfo(message='Successful deal')
        if (data == 'wrongname'):
            messagebox.showinfo(message='Error,your transaction object is wrong,try again.')
        if (data == 'lackmoney'):
            messagebox.showinfo(message='Error,insufficient account balance,try again.')


class DigFrame(Frame):  # 继承Frame类
    def __init__(self, master=None,usr_name="",pri=None):
        Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.privkey = pri
        self.button_text = StringVar()
        self.is_dig = True
        self.usr_name = usr_name
        self.dig_list_tree = self.createPage()

    def createPage(self):
        self.button_text.set('Stop dig')
        Label(self, text='挖矿界面').pack()
        Label(self, text='').pack()
        Button(self,textvariable=self.button_text,command = self.turn_dig).pack()
        Label(self, text='').pack()
        t = threading.Thread(target=self.tcplink)
        t.start()
        # 交易记录列表区
        dig_list_frame = Frame(self)
        dig_list_sub_frame = Frame(dig_list_frame)
        dig_list_tree = Treeview(dig_list_sub_frame, selectmode='browse')
        dig_list_tree.bind('<<TreeviewSelect>>')
        # 交易记录列表垂直滚动条
        dig_list_vscrollbar = Scrollbar(dig_list_sub_frame, orient="vertical", command=dig_list_tree.yview)
        dig_list_vscrollbar.pack(side=RIGHT, fill=Y, expand=YES)
        dig_list_tree.configure(yscrollcommand=dig_list_vscrollbar.set)
        dig_list_hscrollbar = Scrollbar(dig_list_sub_frame, orient="horizontal", command=dig_list_tree.xview)
        dig_list_hscrollbar.pack(side=BOTTOM, fill=X, expand=YES)
        dig_list_tree.configure(xscrollcommand=dig_list_hscrollbar.set)
        dig_list_sub_frame.pack(side=TOP, fill=BOTH, expand=YES)
        # 交易记录列表区列标题
        dig_list_tree["columns"] = ("Time","Info")
        dig_list_column_width = [ 160, 370]
        dig_list_tree['show'] = 'headings'
        for column_name, column_width in zip(dig_list_tree["columns"], dig_list_column_width):
            dig_list_tree.column(column_name, width=column_width, anchor='w')
            dig_list_tree.heading(column_name, text=column_name)
        dig_list_tree.pack(side=LEFT, fill=X, expand=YES)
        dig_list_frame.pack(side=TOP, fill=X, padx=5, pady=5, expand=YES, anchor='n')
        dig_list_tree.insert("", 'end', values=(timestamp2time(time.time()), '加入挖矿啦1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20'))
        return dig_list_tree

    def tcplink(self):
        #告知服务器本用户的挖矿服务器地址
        mes = '08' + self.usr_name + '**' + 'localhost' + '**' + str(port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 7929))
        mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
        client.send(mes)
        client.close()
        #挖矿服务器监听是否有需要挖矿的区块
        client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_s.bind(('localhost', port))  # 绑定要监听的端口
        client_s.listen(2)
        while True:
            conn, addr = client_s.accept()
            t = threading.Thread(target=self.dig, args=(conn, addr))
            t.start()

    def dig(self,conn,addr):
        data = conn.recv(1024).decode()  # 接收数据
        self.dig_list_tree.insert("", 'end', values=(timestamp2time(time.time()), '开始挖矿啦！'))
        difficulty = int(data.split('**',2)[0])
        data = data.split('**',2)[1]
        nonce = 0

        hash_n = self.calculate_hash(data+str(nonce))
        while hash_n[0: difficulty] != ''.join(['0'] * difficulty):
            # 符合要求
            nonce += 1
            hash_n = self.calculate_hash(data+str(nonce))

        mes = str(nonce)
        conn.send(mes.encode('utf-8'))
        data = conn.recv(1024).decode()  # 接收数据
        if data == 'success':
            self.dig_list_tree.insert("", 'end', values=(timestamp2time(time.time()), '挖矿成功，获得奖励！'))
        else:
            self.dig_list_tree.insert("", 'end', values=(timestamp2time(time.time()), '挖矿失败了！'))
        conn.close()

    def calculate_hash(self,data):
        '''
        计算哈希值
        :return:
        '''
        sha256 = hashlib.sha256()
        sha256.update(data.encode('utf-8'))
        hash = sha256.hexdigest()
        return hash

    def turn_dig(self):
        if self.button_text.get() == 'Start dig':
            self.button_text.set('Stop dig')
            mes = '08' + self.usr_name + '**' + 'localhost' + '**' + str(port)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 7929))
            mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
            client.send(mes)
            client.close()
            self.dig_list_tree.insert("", 'end', values=(timestamp2time(time.time()), '加入挖矿啦！'))
        else:
            self.button_text.set('Start dig')
            mes = '09' + self.usr_name
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 7929))
            mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
            client.send(mes)
            client.close()
            self.dig_list_tree.insert("", 'end', values=(timestamp2time(time.time()), '退出挖矿啦！'))
