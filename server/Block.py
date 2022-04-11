# -*- coding:utf-8 -*-
import hashlib
import json
import time
from Transaction import TransactionEncoder


class Block:

    def __init__(self, timestamp, transactions, previous_hash=''):
        '''
        区块的初始化
        :param timestamp: 创建时的时间戳
        :param transactions: 区块数据
        :param previous_hash: 上一个区块的hash
        :param hash: 区块的hash
        '''
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        '''
        计算区块哈希值
        :return:
        '''
        # 将区块信息拼接然后生成sha256的hash值
        raw_str = self.previous_hash + str(self.timestamp) + json.dumps(self.transactions, ensure_ascii=False, cls=TransactionEncoder) + str(self.nonce)
        sha256 = hashlib.sha256()
        sha256.update(raw_str.encode('utf-8'))
        hash = sha256.hexdigest()
        return hash

    def mine_block(self, difficulty):
        '''
        验证挖矿
        :param difficulty: 难度
        :return:
        '''
        self.hash = self.calculate_hash()
        if self.hash[0: difficulty] == ''.join(['0'] * difficulty):
            return True
        else:
            return False



