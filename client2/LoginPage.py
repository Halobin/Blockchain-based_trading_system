from tkinter import *
from tkinter.messagebox import *
from MainPage import *
from AdminPage import *
import socket
import pickle
import rsa
from PIL import ImageTk, Image

with open('public.pem', 'rb') as publickfile:
    p = publickfile.read()
pubkey = rsa.PublicKey.load_pkcs1(p) #服务器的公钥

class LoginPage(object):
    def __init__(self, master=None,im=None):
        self.root = master  # 定义内部变量root
        self.root.geometry('500x330')  # 设置窗口大小
        self.username = StringVar()
        self.password = StringVar()
        self.im= im
        self.createPage()

    def createPage(self):
        self.username.set('Bin')
        self.password.set('bin123')
        self.page = Frame(self.root)  # 创建Frame

        self.c = Canvas(self.page,
                        width=500,  # 指定Canvas组件的宽度
                        height=330,  # 指定Canvas组件的高度
                        bg='white')  # 指定Canvas组件的背景色

        self.c.create_image(250, 165, image=self.im)  # 使用create_image将图片添加到Canvas组件中
        self.c.pack()

        Label(self.page, text='Username: ').place(x=100,y=90)
        Entry(self.page, textvariable=self.username).place(x=230,y=90)
        Label(self.page, text='Password: ').place(x=100,y=140)
        Entry(self.page, textvariable=self.password, show='*').place(x=230,y=140)
        Button(self.page, text='Login', command=self.usr_login).place(x=100,y=220)
        Button(self.page, text='Sign up', command=self.usr_sign_up).place(x=220,y=220)
        Button(self.page, text='Quit', command=self.page.quit).place(x=360,y=220)
        self.page.pack()

    def usr_login(self):
        # 用户登录
        # 获取输入的用户名密码
        usr_name = self.username.get()
        usr_pwd = self.password.get()
        # 构造发送的数据
        mes = "01" + usr_name + "**" + usr_pwd;
        # socket连接服务器，并发送用户名密码让服务器进行比对
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 7929))
        mes = rsa.encrypt(mes.encode('utf-8'),pubkey)
        client.send(mes)
        # 根据返回结果判断
        data = client.recv(1024).decode()
        print(data)
        if (data == "success"):
            messagebox.showinfo(title='Welcome', message='How are you?' + usr_name)
            self.page.destroy()
            self.c.pack_forget()
            (pubkey_c, privkey_c) = rsa.newkeys(1024)
            #print(pubkey_c)
            mes = pickle.dumps(pubkey_c)
            client.send(mes)
            MainPage(self.root,usr_name,self.im,privkey_c)
        if (data == "wrongpassword"):
            messagebox.showinfo(message='Error,your password is wrong,try again.')
        if (data == "nouser"):
            messagebox.showinfo(message='Error,your username is wrong,try again.')
        if (data == 'successadmin'):
            self.page.destroy()
            (pubkey_c, privkey_c) = rsa.newkeys(1024)
            mes = pickle.dumps(pubkey_c)
            client.send(mes)
            AdminPage(self.root, usr_name,privkey_c)
        client.close()

    def usr_sign_up(self):
        # 用户注册
        def sign_to_Mofan_Python():
            # 获取用户名，密码。
            np = new_pwd.get()
            npf = new_pwd_confirm.get()
            nn = new_name.get()
            # 两次密码需要相同
            if np != npf:
                messagebox.showinfo('Error', 'Password and confirm password must be the same!')
                return NONE
            mes = "02" + nn + "**" + np;
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 7929))
            mes = rsa.encrypt(mes.encode('utf-8'), pubkey)
            client.send(mes)
            data = client.recv(1024).decode()
            client.close()
            if (data == "success"):
                messagebox.showinfo('Welcome', 'You have successfully signed up!')
                window_sign_up.destroy()
            if (data == "samename"):
                messagebox.showinfo('Error', 'The user has already signed up!')
            if (data == 'wait'):
                messagebox.showinfo('Error', 'Registration is too frequent, please try again later!')
            client.close()

        # 绘制注册GUI
        window_sign_up = Toplevel(self.root)
        window_sign_up.geometry('350x200')
        window_sign_up.title('Sign up')

        new_name = StringVar()
        Label(window_sign_up, text='Username:').place(x=10, y=10)
        entry_new_name = Entry(window_sign_up, textvariable=new_name)
        entry_new_name.place(x=150, y=10)

        new_pwd = StringVar()
        Label(window_sign_up, text='Password:').place(x=10, y=50)
        entry_new_pwd = Entry(window_sign_up, textvariable=new_pwd, show='*')
        entry_new_pwd.place(x=150, y=50)

        new_pwd_confirm = StringVar()
        Label(window_sign_up, text='Confirm password:').place(x=10, y=90)
        entry_comfirm_sign_up = Entry(window_sign_up, textvariable=new_pwd_confirm, show='*')
        entry_comfirm_sign_up.place(x=150, y=90)

        btn_comfirm_sign_up = Button(window_sign_up, text='Sign up', command=sign_to_Mofan_Python)
        btn_comfirm_sign_up.place(x=150, y=130)