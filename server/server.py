#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import pickle
import time
import json
import threading
import rsa
import hashlib
from Block import Block
from BlockChain import BlockChain
from Transaction import Transaction
from Transaction import TransactionEncoder

usr_port ={}
address_time = {}
blockChain = BlockChain()
with open('private.pem', 'rb') as privatefile:
    p = privatefile.read()
privkey = rsa.PrivateKey.load_pkcs1(p)

pubkey_client = {}


def timestamp2time(timestamp):
    """
    时间戳转为格式化的时间字符串
    :param timestamp:
    :return: 格式化的时间字符串
    """
    time_array = time.localtime(timestamp)
    mytime = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return mytime

is_dig_over =False
def dig_link(usr_name,addr,block):
	print("已发送挖矿通知")
	time_start = time.clock()
	mes = str(blockChain.difficulty)+'**'+block.previous_hash + str(block.timestamp) + json.dumps(block.transactions, ensure_ascii=False, cls=TransactionEncoder)
	dig_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	dig_client.connect(addr)
	dig_client.send(mes.encode('utf-8'))
	data = dig_client.recv(1024).decode()
	global  is_dig_over
	mes = "unsuccess"
	if is_dig_over == False:
		block.nonce = int(data)
		if block.mine_block(blockChain.difficulty) == True:
			is_dig_over = True
			time_use = time.clock()-time_start
			blockChain.adjust_difficulty(time_use)
			blockChain.chain[-1].nonce = block.nonce
			blockChain.add_transaction(Transaction(time.time(), None, usr_name, blockChain.mining_reward)) #挖矿奖励
			mes = 'success'
			print(usr_name+'挖矿成功\n耗时'+str(time_use)+'s\n奖励'+str(blockChain.mining_reward)+'\n挖到的区块hash：'+block.hash)
	dig_client.send(mes.encode('utf-8'))
	dig_client.close()

def dec(mes): #rsa 解密
    text = []
    for i in range(0,len(mes),128):
        cont = mes[i:i+128]
        text.append(rsa.decrypt(cont,privkey))
    text = b''.join(text)
    return text.decode()

def enc(mes,pub): #rsa 加密
	encrypt_text = []
	for i in range(0, len(mes), 50):
		cont = mes[i:i + 50]
		encrypt_text.append(rsa.encrypt(cont.encode('utf-8'), pub))
	mes = b''.join(encrypt_text)
	return mes

def tcplink(conn,addr):
	data = conn.recv(1024)  # 接收数据
	data = dec(data)
	print("解密后："+data[2:])
	type = data[0:2]
	# 登录
	if (type == "01"):
		data = data[2:]
		usr_name = data.split("**", 2)[0]
		usr_pwd = data.split("**", 2)[1]
		try:
			with open('usrs_pwd.pickle', 'rb') as usr_pwd_file:
				usrs_pwd = pickle.load(usr_pwd_file)
		except FileNotFoundError:
			with open('usrs_pwd.pickle', 'wb') as usr_pwd_file:
				usrs_pwd = {'admin': 'admin'}
				pickle.dump(usrs_pwd, usr_pwd_file)
		mes = ""
		if usr_name in usrs_pwd:
			if usr_pwd == usrs_pwd[usr_name]:
				mes = "success"
				if usr_name == 'admin' :
					mes = "successadmin"
				conn.send(mes.encode('utf-8'))
				print(usr_name + "登录成功")
				data = conn.recv(1024)
				pub = pickle.loads(data)
				print(pub)
				pubkey_client[usr_name] = pub
			else:
				mes = "wrongpassword"
				conn.send(mes.encode('utf-8'))
		else:
			mes = "nouser"
			conn.send(mes.encode('utf-8'))


	# 注册
	if (type == "02"):
		data = data[2:]
		usr_name = data.split("**", 2)[0]
		usr_pwd = data.split("**", 2)[1]
		IP = addr[0]
		mes = ""
		if IP in address_time.keys() and time.clock()-address_time[IP]<30 :
			mes = "wait"
		else:
			try:
				with open('usrs_pwd.pickle', 'rb') as usr_pwd_file:
					exist_usr_pwd = pickle.load(usr_pwd_file)
			except FileNotFoundError:
				with open('usrs_pwd.pickle', 'wb') as usr_pwd_file:
					exist_usr_pwd = {'admin': 'admin'}
					pickle.dump(exist_usr_pwd, usr_pwd_file)
			if usr_name in exist_usr_pwd:
				mes = "samename"
			else:
				exist_usr_pwd[usr_name] = usr_pwd
				with open('usrs_pwd.pickle', 'wb') as usr_pwd_file:
					pickle.dump(exist_usr_pwd, usr_pwd_file)
				# 初始化个人信息
				try:
					with open('usrs_info.pickle', 'rb') as usr_info_file:
						exist_usr_info = pickle.load(usr_info_file)
				except FileNotFoundError:
					exist_usr_info = {'admin': {'name': '冯彬', 'gender': '男', 'borndate': '19971025'}}

				exist_usr_info[usr_name] = {'name': '冯彬', 'gender': '男', 'borndate': '19971025'}
				with open('usrs_info.pickle', 'wb') as usr_info_file:
					pickle.dump(exist_usr_info, usr_info_file)
				address_time[IP] = time.clock()
				mes = "success"
				print(usr_name + "注册成功")
		conn.send(mes.encode('utf-8'))

	# 查询个人信息
	if (type == "03"):
		usr_name = data[2:]
		with open('usrs_info.pickle', 'rb') as usr_info_file:
			exist_usr_info = pickle.load(usr_info_file)
		mes=exist_usr_info[usr_name]['name']+"**"+exist_usr_info[usr_name]['gender']+"**"+exist_usr_info[usr_name]['borndate']
		mes = rsa.encrypt(mes.encode('utf-8'),pubkey_client[usr_name])
		conn.send(mes)
		print(usr_name+'查询了个人信息')

	# 修改个人信息
	if(type == "04"):
		data = data[2:]
		usr_name = data.split("**", 4)[0]
		nname = data.split("**", 4)[1]
		nmale = data.split("**", 4)[2]
		nborndate = data.split("**", 4)[3]
		with open('usrs_info.pickle', 'rb') as usr_info_file:
			exist_usr_info = pickle.load(usr_info_file)
		exist_usr_info[usr_name]['name'] = nname
		exist_usr_info[usr_name]['gender'] = nmale
		exist_usr_info[usr_name]['borndate'] = nborndate
		with open('usrs_info.pickle', 'wb') as usr_info_file:
			pickle.dump(exist_usr_info,usr_info_file)
		print(usr_name+'修改了个人信息')

	#交易
	if(type == "05"):
		data = data[2:]
		giver = data.split("**", 3)[0]
		getter = data.split("**", 3)[1]
		amount = data.split("**", 3)[2]
		signature = conn.recv(1024)
		tmp = False
		try:
			rsa.verify((giver+"**"+getter+"**"+amount).encode('utf-8'),signature, pubkey_client[giver])
			print("交易验证成功")
			tmp = True
		except:
			print("交易验证失败")

		with open('usrs_pwd.pickle', 'rb') as usr_pwd_file:
			usrs_pwd = pickle.load(usr_pwd_file)
		mes = ""
		if getter in usrs_pwd and tmp:
			if int(blockChain.get_balance_of_address(giver)) >= int(amount):
				blockChain.add_transaction(Transaction(time.time(),giver, getter, int(amount)))
				print(giver+'向'+getter+'转账'+amount)
				mes="success"
				global is_dig_over
				is_dig_over =False
				block = blockChain.add_block()
				for k,v in usr_port.items():
					t = threading.Thread(target=dig_link, args=(k, v, block))
					t.start()
			else:
				mes = "lackmoney"
		else:
			mes = "wrongname"
		conn.send(mes.encode('utf-8'))

	#余额查询
	if(type == "06"):
		usr_name = data[2:]
		mes = str(blockChain.get_balance_of_address(usr_name))
		mes = enc(mes,pubkey_client[usr_name])
		conn.send(mes)
		print(usr_name+'查询了余额')

	#查询余额明细
	if(type == "07"):
		address = data[2:]
		t = 1
		mes = ""
		for block in blockChain.chain:
			for trans in block.transactions:
				if trans.from_address == address or trans.to_address == address:
					t = t+1
					trans_mes = timestamp2time(trans.time)+"**"+str(trans.from_address)+"**"+str(trans.to_address)+"**"+str(trans.amount)
					mes = mes + "???" + trans_mes
		mes = str(t-1) + mes
		#mes = rsa.encrypt(mes.encode('utf-8'), pubkey_client[address])
		mes = enc(mes,pubkey_client[address])
		conn.send(mes)
		print(address+'查询了余额明细')

	#用户加入挖矿
	if(type == "08"):
		data = data[2:]
		usr_name = data.split('**',3)[0]
		usr_p = (data.split('**',3)[1],int(data.split('**',3)[2]))
		usr_port[usr_name] = usr_p
		print(usr_name+'加入挖矿')

	#用户退出挖矿
	if(type == '09'):
		data = data[2:]
		usr_port.pop(data)
		print(data+'退出挖矿')

	#管理员查询所有数据
	if(type == '10'):
		with open('usrs_pwd.pickle', 'rb') as usr_pwd_file:
			exist_usr_pwd = pickle.load(usr_pwd_file)
		with open('usrs_info.pickle', 'rb') as usr_info_file:
			exist_usr_info = pickle.load(usr_info_file)
		mes = str(len(exist_usr_pwd))
		for k in exist_usr_pwd.keys():
			mes = mes + "???" + k + '**' + exist_usr_pwd[k] + '**' +exist_usr_info[k]['name']+'**'+exist_usr_info[k]['gender']+"**"+exist_usr_info[k]['borndate']+'**'+str(blockChain.get_balance_of_address(k))

		mes = enc(mes,pubkey_client['admin'])
		conn.send(mes)

	#管理员修改信息
	if(type == '11'):
		with open('usrs_pwd.pickle', 'rb') as usr_pwd_file:
			exist_usr_pwd = pickle.load(usr_pwd_file)
		with open('usrs_info.pickle', 'rb') as usr_info_file:
			exist_usr_info = pickle.load(usr_info_file)
		usr_pwd_file.close()
		usr_info_file.close()
		usr_mes = data[2:]
		print(usr_mes)
		usr_account = usr_mes.split("**", 5)[0]
		usr_password = usr_mes.split("**", 5)[1]
		usr_name = usr_mes.split("**", 5)[2]
		usr_gender = usr_mes.split("**", 5)[3]
		usr_birthday = usr_mes.split("**", 5)[4]
		exist_usr_pwd[usr_account] = usr_password
		exist_usr_info[usr_account]['name'] = usr_name
		exist_usr_info[usr_account]['gender'] = usr_gender
		exist_usr_info[usr_account]['borndate'] = usr_birthday
		with open('usrs_pwd.pickle', 'wb') as usr_pwd_file:
			pickle.dump(exist_usr_pwd, usr_pwd_file)
		with open('usrs_info.pickle', 'wb') as usr_info_file:
			pickle.dump(exist_usr_info, usr_info_file)
		usr_pwd_file.close()
		usr_info_file.close()
		print('admin 修改了'+usr_account+'的个人信息')


	conn.close()

# 建立一个服务端
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('localhost',7929)) #绑定要监听的端口
server.listen(10) #开始监听 表示可以使用十个链接排队

with open('usrs_pwd.pickle', 'rb') as usr_pwd_file:
	usrs_pwd = pickle.load(usr_pwd_file)
for usr_name in usrs_pwd.keys():
	blockChain.reward_first(usr_name)
blockChain.mine_pending_transaction('admin')
usr_pwd_file.close()

while True:# conn就是客户端链接过来而在服务端为期生成的一个链接实例
	conn,addr = server.accept() #等待链接,多个链接的时候就会出现问题,其实返回了两个值
	#print(addr)
	t = threading.Thread(target=tcplink, args=(conn, addr))
	t.start()

