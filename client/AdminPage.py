from tkinter import *
from tkinter.ttk import Treeview
import socket
import time
import rsa

with open('public.pem', 'rb') as publickfile:
    p = publickfile.read()
pubkey = rsa.PublicKey.load_pkcs1(p)#服务器的公钥

def dec(mes,privkey):
    text = []
    for i in range(0,len(mes),128):
        cont = mes[i:i+128]
        text.append(rsa.decrypt(cont,privkey))
    text = b''.join(text)
    return text.decode()

class AdminPage(object):
    def __init__(self, master=None,usr_name="",pri=None):
        self.root = master  # 定义内部变量root
        self.root.geometry('750x350')  # 设置窗口大小
        self.usr_name = usr_name
        self.privkey = pri
        self.usr_list_tree = self.createPage()
        self.usr_info = []
        self.update_info()
        self.choose_item = 0;

    def createPage(self):
        Label(self.root, text='').pack()
        Label(self.root, text='系统用户信息管理').pack()
        Label(self.root, text='').pack()
        # 交易记录列表区
        usr_list_frame = Frame(self.root)
        usr_list_sub_frame = Frame(usr_list_frame)
        usr_list_tree = Treeview(usr_list_sub_frame, selectmode='browse')
        usr_list_tree.bind('<<TreeviewSelect>>',self.on_click_usr_list_tree)
        # 交易记录列表垂直滚动条
        usr_list_vscrollbar = Scrollbar(usr_list_sub_frame, orient="vertical", command=usr_list_tree.yview)
        usr_list_vscrollbar.pack(side=RIGHT, fill=Y, expand=YES)
        usr_list_tree.configure(yscrollcommand=usr_list_vscrollbar.set)
        usr_list_sub_frame.pack(side=TOP, fill=BOTH, expand=YES)
        # 交易记录列表区列标题
        usr_list_tree["columns"] = ("No.", "Account","Password","Name","Gender","Birthday","Balance")
        usr_list_column_width = [40,90,110,90,90,150,90]
        usr_list_tree['show'] = 'headings'
        for column_name, column_width in zip(usr_list_tree["columns"], usr_list_column_width):
            usr_list_tree.column(column_name, width=column_width, anchor='w')
            usr_list_tree.heading(column_name, text=column_name)
        usr_list_tree.pack(side=LEFT, fill=X, expand=YES)
        usr_list_frame.pack(side=TOP, fill=X, padx=5, pady=5, expand=YES, anchor='n')
        Button(self.root, text='Modify', command=self.modify).pack()
        return usr_list_tree

    def update_info(self):
        self.usr_info = []
        self.usr_list_tree.delete(*self.usr_list_tree.get_children())
        mes = "10"
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 7929))
        mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
        client.send(mes)
        data = client.recv(10240)
        data = dec(data,self.privkey)
        client.close()
        t = int(data.split("???", 2)[0])
        i = 0
        while i < t:
            i = i + 1
            usr_mes = data.split("???", t + 1)[i]
            usr_account = usr_mes.split("**", 6)[0]
            usr_password = usr_mes.split("**", 6)[1]
            usr_name = usr_mes.split("**", 6)[2]
            usr_gender = usr_mes.split("**", 6)[3]
            usr_birthday = usr_mes.split("**", 6)[4]
            usr_balance = usr_mes.split("**", 6)[5]
            info = {'account':usr_account,'password':usr_password,'name':usr_name,'gender':usr_gender,'birthday':usr_birthday,'balance':usr_balance}
            self.usr_info.append(info)
            self.usr_list_tree.insert("", 'end',
                                        values=(i, usr_account, "******", usr_name, usr_gender,usr_birthday,usr_balance))

    def on_click_usr_list_tree(self,event):
        for item in self.usr_list_tree.selection():
            item_text = self.usr_list_tree.item(item, "values")
            self.choose_item = int(item_text[0])-1

    def modify(self):
        def change_info():
            mes = '11' + usr['account'] + '**' + new_password.get() + '**' + new_name.get() + '**' + new_gender.get() + '**' + new_birthday.get()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 7929))
            mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
            client.send(mes)
            time.sleep(0.05)
            self.update_info()
            window_change.destroy()

        def quit_change():
            window_change.destroy()

        window_change = Toplevel(self.root)
        window_change.geometry('350x330')
        window_change.title('Change info')

        usr = self.usr_info[self.choose_item]

        Label(window_change, text='Account:').place(x=10, y=10)
        Label(window_change, text=usr['account']).place(x=150, y=10)

        new_password = StringVar()
        new_password.set(usr['password'])
        Label(window_change, text='Password：').place(x=10, y=50)
        Entry(window_change, textvariable=new_password).place(x=150, y=50)

        new_name = StringVar()
        new_name.set(usr['name'])
        Label(window_change, text='Name：').place(x=10, y=90)
        Entry(window_change, textvariable=new_name).place(x=150,y=90)

        new_gender = StringVar()
        new_gender.set(usr['gender'])
        Label(window_change, text='Gender：').place(x=10, y=140)
        Entry(window_change, textvariable=new_gender).place(x=150, y=140)

        new_birthday = StringVar()
        new_birthday.set(usr['birthday'])
        Label(window_change, text='Birthday：').place(x=10, y=190)
        Entry(window_change, textvariable=new_birthday).place(x=150, y=190)

        Label(window_change, text='Balance:').place(x=10, y=240)
        Label(window_change, text=usr['balance']).place(x=150, y=240)

        btn_comfirm_sure = Button(window_change, text='Modify', command=change_info)
        btn_comfirm_sure.place(x=150, y=290)
        btn_comfirm_sure = Button(window_change, text='Quit', command=quit_change)
        btn_comfirm_sure.place(x=230, y=290)

