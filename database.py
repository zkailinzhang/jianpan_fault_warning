from enum import IntEnum
import happybase
import pandas as pd
import numpy as np
from pandas.io import sql
import pymysql
from redis import ConnectionPool, Redis
import os
from qianconfig import MyLogging

myLogger = MyLogging()

class Hbase:

    def __init__(self):
        self.connection = None
        self.table_sent = None
        self.table_receive = None
        self.value = []
        self.value_array = np.array
        self.fail_connect_counts = 0

    def connect(self, host, port):
        while True:
            try:
                #self.connection = happybase.Connection(host, port, autoconnect=False)
                self.connection = happybase.Connection(host,  autoconnect=False)
                self.connection.open()
                print('hbase连接成功!!')
                myLogger.write_logger('hbase connect success')
                break
            except:
                self.fail_connect_counts += 1
                print('hbase连接失败,尝试重新连接!!')

            if self.fail_connect_counts == 5:
                self.fail_connect_counts = 0
                break

        return self.connection


    # 参数重置以便重复使用
    def initialize(self):
        self.value = []
        self.value_array = np.array

    def get_data(self, table, row_start, row_end, key_need):
        cf = '1:'+key_need
        key_need = bytes(cf, encoding='utf-8')
        self.initialize()
        if type(table) == str:
            self.table_receive = self.connection.table(table)
            if self.table_receive != None:
                for key_circle, value in self.table_receive.scan(row_start=row_start, row_stop=row_end):
                    self.value.append(float(value[key_need].decode()))

        else:
            table = str(table)
            self.table_receive = self.connection.table(table)
            if self.table_receive != None:
                for key, value in self.table_receive.scan(row_start=row_start, row_stop=row_end):
                    self.value.append(float(value[key_need].decode()))

        self.value_array = np.array(self.value).astype(float)
        self.value_array = self.value_array.ravel()

        return self.value_array

    def insert_data(self, table, rowkey, cf, value):
        self.table_sent = self.connection.table(table)
        if type(cf) == str and type(value) == str:
            try:
                self.table_sent.put(rowkey, {cf: value})
            except:
                print('hbase未传输成功!')
        else:
            cf = str(cf)
            value = str(value)
            try:
                self.table_sent.put(rowkey, {cf: value})
            except:
                print('hbase未传输成功!')
        # if type(cf) == str and type(value) == str:
        #     self.table_sent.put(rowkey, {cf: value})
        # else:
        #     cf = str(cf)
        #     value = str(value)
        #     self.table_sent.put(rowkey, {cf: value})

    def close(self):
        self.connection.close()



class MySQL:
    def __init__(self, host, port, user, passport, database):
        self.fail_connect_counts = 0
        while True:
            try:
                self.db = pymysql.connect(host=host, port=port, user=user, password=passport, database=database,
                                          charset='utf8mb4')
                self.cursor = self.db.cursor()
                print('mysql数据库连接成功！！')
                break
            except:
                self.fail_connect_counts += 1
                print('mysql数据库未连接,尝试重新连接!!')

            if self.fail_connect_counts == 5:
                self.fail_connect_counts = 0
                break

    def get_data(self, item, table, limit):
        sql = 'select {} from {} {}'.format(str(item), str(table), str(limit))
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            self.db.commit()
            return data
        except:
            self.db.rollback()
            print('mysql未传输成功！！')

    def insert_data2(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
            # print('传输成功!!')
        except:
            self.db.rollback()
            # self.cursor.close()
            print('mysql未传输成功！！')


    def insert_data(self, table, item, values):
        sql_word = ''
        if len(values) == 1:
            sql_word = '%s'
        elif len(values) > 1:
            for i in range(len(values)):
                if i == len(values) - 1:
                    sql_word += '%s'
                else:
                    sql_word += '%s' + ','

        # for i in range(len(item)):
        sql = 'insert into {}({}) values ({})'.format(table, item,sql_word)
        print(sql)
        print(values)
        try:
            self.cursor.execute(sql, values)
            self.db.commit()
            # print('传输成功!!')
        except:
            self.db.rollback()
            # self.cursor.close()
            print('mysql未传输成功！！')
            # test
        # self.cursor.execute(sql, values)
        # self.db.commit()


    def delete_kks(self, table, system_id,kks):
        #sql = 'delete from {} where system_id={} and kks=`{}`'.format(table, system_id,kks)
        sql = 'delete from {} where system_id={} and kks="{}"'.format(table, system_id,kks)
        print(sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            print('数据未删除!!')

    def cleantable(self, table):
        sql = 'truncate table {}'.format(table)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            pass

    def delete(self, table, system_id):
        sql = 'delete from {} where system_id={}'.format(table, system_id)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            print('数据未删除!!')
    
    def update(self, table, item, value, kks):
        for i in range(len(item)):
            sql = 'update {} set {}={} where kks = {}'.format(table, item[i], value[i], kks)
            try:
                self.cursor.execute(sql)
                self.db.commit()
            except:
                self.db.rollback()
                print('数据未更新！')
        
    def search_warn_fault(self,table,system_id,fault_id):
        #sql = 'select COUNT(*) from %s where system_id=%d and fault_id =%d and end_time =NULL'%(table, system_id,fault_id)
        sql = 'select COUNT(*) from {} where system_id={} and fault_id ={} and endtime is NULL'.format(str(table), system_id,fault_id)
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            self.db.commit()
            return data
        except:
            self.db.rollback()
            print('数据未count成功!!')


    def search_warn_diag(self,table,diagnose_id):
        sql = 'select COUNT(*) from {} where system_id={}'.format(str(table), diagnose_id)
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            self.db.commit()
            return data
        except:
            self.db.rollback()
            print('数据未count成功!!')        



class RedisControl:
    def __init__(self, host, port, db,Password):
        self.fail_connect_counts = 0
        while True:
            try:
                self.pool = ConnectionPool(host=host, port=port, db=db,password=Password, decode_responses=True)
                self.rdb = Redis(connection_pool=self.pool)
                print('redis数据库连接成功!!!')
                break
            except:
                self.fail_connect_counts += 1
                print('redis数据库未连接，尝试重新连接!!')

            if self.fail_connect_counts == 5:
                self.fail_connect_counts = 0
                break

    def set_string(self, name, value):
        self.rdb.set(name, value)

    def mset_string(self, insert_dict):
        self.rdb.mset(insert_dict)

    def insert_hash(self, name, value):
        self.rdb.hmset(name, value)


if __name__ == '__main__':
    path = '数据/上海电力数据/高加数据'
    file_list = os.listdir(path)
    print(file_list)
    hbase = Hbase()
    hbase.connect()
    # hbase.sent_table_set('gaojia')
    # a = input_parameters((1, 2), (3, 4))
    # print(a)
    print(path + '/' + file_list[0])

    for i in range(15):
        print(path+'/'+file_list[i])
        data = pd.read_csv(path+'/'+file_list[i])
        time_data = np.array(data.iloc[:, 0]).astype(str)
        # print(time_data)
        name = data.iloc[:, 1].name
        value_data = np.array(data.iloc[:, 1]).astype(str)
        print(value_data)
        cf = '1'+':'+name
        print(cf)
        print('i:', i)
        for m in range(200000):
            print('m:', m)
            hbase.insert_data('gaojia', time_data[m], cf, value_data[m])
            # time.sleep(0.1)