#!/usr/bin/env python
# coding: utf-8

# In[1]:

import numpy as np
import pandas as pd
import math
import pymysql
import pymysql.cursors
from sqlalchemy import create_engine
from sqlalchemy.types import DATE,CHAR,VARCHAR ,INT
from datetime import datetime
import redis
import json
import threading
import time
import happybase
import os
import datetime
from qianconfig import MyLogging
myLogger = MyLogging()

#from database import *


# In[124]:


class Conf:
    #故障开始时间fault_datetime
    fault_datetime = 0
    # mysql_host = '172.17.224.171'
    # mysql_port = 3306
    # mysql_user = 'root'
    # mysql_password = 'Qwe123!!'
    # mysql_db = 'yuhuan_monitor_prd3'
    
    mysql_host = "127.0.0.1"
    mysql_user = "root"
    mysql_password = "123456"
    mysql_db = "mysql"
    mysql_port = 3306
    
    redis_host = '172.17.224.172'
    redis_port = 6379
    redis_password = "123456"
    redis_db = 5
    
    hbase_host = '172.17.224.171'
    hbase_port = 9090
    hbase_table = 'history_point_new'
    row_start = "2021-10-18 12:00:00"
    row_end =   "2021-10-18 12:10:00"
    time_interval = 5

    fault_list = "fault_list"
    symptom_list = "symptom_list"
    threshold_list = "limit_list" ##该限值列表是高斯聚类的结果表
    sys_id = 63
    
    ##涉及到指令与反馈的偏差 ：反馈在前，指令在后
    special_kks_list1 = ["40CXA50020CRP01R","40CXA50006CRP01R"] ## special_kks_list1[0] 为反馈
    special_kks_list2 = ["40HFE50CG110XQ01","40HFE50AA110XQ01"] ## special_kks_list2[0] 为反馈
    


def Read_Redis(pointname,Host,Port,Password,DB):
    spot_name = pointname
    
    #建立数据库连接
    counts = 0
    while True :
        try:
#             pool = redis.ConnectionPool(host='127.0.0.1',port=6379,password='123456',db=0,decode_responses=True)
            pool = redis.ConnectionPool(host=Host,port=Port,password=Password,db=DB,decode_responses=True)
            conn = redis.Redis(connection_pool=pool,encoding='utf-8')
            break
        except:
            counts += 1
            if counts > 5:
                print("读取Redis失败！未连接")
                break
    
    point_current_info = []
    for spot_name_ in spot_name :

        data  = conn.get("REAL_TIME_VALUE:" + spot_name_)
        if(data == None):
            continue
        data_ = eval(data)

        point_current_info.append(data_)
        
    conn.connection_pool.disconnect()
    
    return point_current_info


# In[5]:


def Read_mysql(Config,Host,User,Password,DB,Port):
    #从mysql数据库读入列表:
    counts = 0
    while True:
        try:
            con = pymysql.connect(host = Host, 
                                  port = Port,
                                  user = User, password = Password, 
                                  db = DB, charset='utf8')

            break
        except:
            counts += 1
            if counts > 5:
                print("读取MySQL失败！未连接")
                break
  
    fault_list = Config.fault_list
    symptom_list = Config.symptom_list
    threshold_list = Config.threshold_list ##该限值列表是高斯聚类的结果表
    #charset用于修正中文输出为问号的问题
    sql = "select * from %s;" %(fault_list)
    Fault_dataframe = pd.read_sql(sql, con)

    sql = "select * from %s;" %(symptom_list)
    Symptom_dataframe = pd.read_sql(sql, con)

    sql = "select * from %s;" %(threshold_list)
    Threshold_dataframe = pd.read_sql(sql, con)

    con.close()  
    
    return  Fault_dataframe,Symptom_dataframe,Threshold_dataframe


# In[6]:
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
                self.connection = happybase.Connection(host, port, autoconnect=False)
                #self.connection = happybase.Connection(host,  autoconnect=False)
                self.connection.open()
                print('hbase连接成功!!')
                
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
                print('未传输成功!')
        else:
            cf = str(cf)
            value = str(value)
            try:
                self.table_sent.put(rowkey, {cf: value})
            except:
                print('未传输成功!')
        # if type(cf) == str and type(value) == str:
        #     self.table_sent.put(rowkey, {cf: value})
        # else:
        #     cf = str(cf)
        #     value = str(value)
        #     self.table_sent.put(rowkey, {cf: value})

    def close(self):
        self.connection.close()


def Write_mysql(Config, device_name,sys_id,Host,User,Password,DB,port,result_list) :
    
    ID_fault = result_list[0]
    name_fault = result_list[1]
    conc_deg = result_list[3]
    device_num = result_list[4]
    timestamp = result_list[5]
    
    Name_symptom = str()
    for i in result_list[2] :
        Name_symptom += i + "  "

    ##建立数据库连接
    counts = 0
    while True:
        try:

            con = pymysql.connect(host = Host, port=port,
                                  user = User, password = Password, 
                                  db = DB, charset='utf8mb4')
            break
        except:
            counts += 1
            if counts > 5:
                print("写入MySQL失败！未连接")
                break

    diagnosis_list = str("diagnosis_list")
    diagnosis_history = str("diagnosis_history")

    ##如果故障id为0，表示未诊断出故障，不写入诊断历史储存表，只写入诊断结果表
    if ID_fault != 0 :
        myLogger.write_logger('诊断结果 写入成功！设备id {} ,故障id {}'.format(sys_id,ID_fault))
        ## UPDATE 语句,写入诊断结果表
        sql = "UPDATE %s set fault_id=%s,fault_name='%s',degree=%s,related_symptoms='%s',datetime='%s',device='%s'  WHERE system_id=%s;" %(diagnosis_list,ID_fault,name_fault,conc_deg,Name_symptom
                               ,timestamp
                               ,device_num
                               ,sys_id) 

        # 执行新增或更新数据操作,返回受影响的行数
        cursor = con.cursor()
        res_row = cursor.execute(sql)
        # 提交事务
        con.commit()
        #print("更新成功！")

        ##INSERT语句，写入诊断历史储存表
        sql = "SELECT datetime FROM %s WHERE system_id=%s and fault_name='%s' ;" %(diagnosis_history,sys_id, name_fault)
        # sql = 'select datetime from {} where system_id={} and fault_name ={} '.format(str(diagnosis_history), Config.sys_id,name_fault)
        try:
            cursor = con.cursor()
            cursor.execute(sql)
            datetime_tuple = cursor.fetchall() 
            con.commit()

        except:
            print('数据未cont成功!!')

        datetime_list = []
        for i in datetime_tuple:
            datetime_list.append(i[0].strftime("%Y-%m-%d %H:%M:%S"))
        # print(datetime_list)    
        if  (Config.fault_datetime not in datetime_list)  :
            sql = "INSERT INTO %s (system_id,device,fault_name,degree,datetime,endtime) VALUES(%s,'%s','%s',%s,'%s','%s');" %(
                                                                                            diagnosis_history
                                                                                            ,sys_id
                                                                                            ,device_num
                                                                                            ,name_fault
                                                                                            ,conc_deg
                                                                                            ,Config.fault_datetime
                                                                                            ,timestamp)

            cursor = con.cursor()
            res_row = cursor.execute(sql)
            # 提交事务
            con.commit()
            print("故障写入成功！")
            con.close()
        else:
            sql = "UPDATE %s set endtime='%s'  WHERE system_id = %s and datetime='%s';" %(diagnosis_history
                                                                                          ,timestamp
                                                                                          ,sys_id
                                                                                          ,Config.fault_datetime) 
            cursor = con.cursor()
            res_row = cursor.execute(sql)
            # 提交事务
            con.commit()
            con.close()
        
    else :
        ## UPDATE 语句,写入诊断结果表
        sql = "UPDATE %s set fault_id=%s,fault_name='%s',degree=%s,related_symptoms='%s',datetime='%s',device='%s'    WHERE system_id = %s;" %(diagnosis_list,ID_fault,name_fault,conc_deg,Name_symptom
                               ,timestamp
                               ,device_num
                               ,sys_id) 

        # 执行新增或更新数据操作,返回受影响的行数
        cursor = con.cursor()
        res_row = cursor.execute(sql)
        # 提交事务
        con.commit()
    
        # 关闭链接
        con.close()
        #print("更新成功！")
        
# In[121]:


def Fault_diagnosis(Config,device_name,sys_id,kks_special,row_start,row_end):
###################################################################################################    
    Fault_dataframe,Symptom_dataframe,Threshold_dataframe = Read_mysql(Config,Host = Config.mysql_host
                                                                   ,Port = Config.mysql_port
                                                                   ,User = Config.mysql_user
                                                                   ,Password = Config.mysql_password
                                                                   ,DB = Config.mysql_database)
    
    ###############################################################################################
    ##筛选同一系统的故障表，放在Sub_Fault_dataframe内
    record_num = []
    for iter0 in  range(Fault_dataframe.shape[0]):
        if Fault_dataframe.iloc[iter0]["system_id"] == sys_id:
            record_num.append(iter0)      
    record_start = record_num[0]
    record_end = record_num[-1] + 1
    Sub_Fault_dataframe = Fault_dataframe.iloc[record_start:record_end]
    Sub_Fault_dataframe = Sub_Fault_dataframe.reset_index(drop=True)
    ##############################################################################################
    ##筛选同一系统的征兆表，放在Sub_Symptom_dataframe内
    record_num = []
    for iter0 in  range(Symptom_dataframe.shape[0]):
        if Symptom_dataframe.iloc[iter0]["system_id"] == sys_id:
            record_num.append(iter0)      
    record_start = record_num[0]
    record_end = record_num[-1] + 1
    Sub_Symptom_dataframe = Symptom_dataframe.iloc[record_start:record_end]
    Sub_Symptom_dataframe = Sub_Symptom_dataframe.reset_index(drop=True)
    ##############################################################################################
    ##筛选同一系统的限值表，放在Sub_Threshold_dataframe内
    record_num = []
    for iter0 in  range(Threshold_dataframe.shape[0]):
        if Threshold_dataframe.iloc[iter0]["system_id"] == sys_id:
            record_num.append(iter0)      
    record_start = record_num[0]
    record_end = record_num[-1] + 1
    Sub_Threshold_dataframe = Threshold_dataframe.iloc[record_start:record_end]
    Sub_Threshold_dataframe = Sub_Threshold_dataframe.reset_index(drop=True)
    #############################################################################################                                                                 
    ##记录同一系统所有故障对应的所有KKS
    Full_Point_name = list(np.unique(Sub_Symptom_dataframe["kks"]))                                                                    
    Full_Time_Point_values = []
    ##从hbase读取kks历史值                                                                   
    hbase = Hbase()
    hbase.connect(host = Config.hbase_host, port = Config.hbase2_port)   

    for iter1,kks_name in enumerate(Full_Point_name) :  
        value_array = hbase.get_data(Config.hbase_table, row_start, row_end, key_need = kks_name)
        # print(value_array)
        Full_Time_Point_values.append(list(value_array)) 

    Full_Time_Point_values = np.array(Full_Time_Point_values,dtype=float).T
    
    if len(Full_Point_name) ==  Full_Time_Point_values.shape[1] :
        print("成功读取kks历史数据！")
    else:
        print("读取kks历史数据失败！")
    #####################################################################################################
    ##用在存放所有时刻诊断结果
    Diagnosis_list = []   
    ##时间指针: iter1  , (Config.row_start + iter1 * Config.time_interval )代表当前诊断时刻                                                                 
    for iter1 in range(Full_Time_Point_values.shape[0]): 
        ##获取当前诊断时间
        Timestamp = (datetime.datetime.strptime(row_start,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=iter1*Config.time_interval)).strftime("%Y-%m-%d %H:%M:%S")
        ##用在存放当前时刻设备所有kks值
        Current_Point_values = []                                                              
        ##kks指针: iter2，依次指向各个kks                                                              
        for iter2 in range(Full_Time_Point_values.shape[1]):
            Current_Point_values.append(Full_Time_Point_values[iter1][iter2])
    ######################################################################################################
        ##################################################################################################
        ##依次诊断当前系统所有故障
        for iter3, fault_id_ in enumerate(Sub_Fault_dataframe['id']):
            ##初始化变量
            Point_name = []
            Point_Current_value = []
            Point_Current_name = []
            Pre_condition_degree = []
            Compute_point_degree = []
            High = []
            Low = []
            VH = []
            VL = []
            ##记录故障相关信息
            Device_num = Sub_Fault_dataframe['device'][iter3]

            FaultID = Sub_Fault_dataframe['id'][iter3]

            Fault_name = Sub_Fault_dataframe['fault_name'][iter3]

            Pre_conclusion_degree = Sub_Fault_dataframe['pre_conc_degree'][iter3]
            Pre_conclusion_degree = np.array(Pre_conclusion_degree,dtype='float64')

            Match_index = Fault_dataframe['match_index'][iter3]

            ##记录故障所需测点kks
            for iter2, point_name in enumerate(Sub_Symptom_dataframe['kks']):

                if Sub_Symptom_dataframe['related_fault_id'][iter2] == fault_id_ :

                    Point_name.append(point_name)

                    Pre_condition_degree.append(Sub_Symptom_dataframe['pre_cond_degree'][iter2])
            ########################################################################################### 
            ##查看当前故障的征兆是否涉及到指令与反馈的偏差
            
            #for deviation_list in [Config.special_kks_list1,Config.special_kks_list2]:##可添加新的一对指令与反馈
            if len(kks_special)!=0:
                for deviation_list in kks_special:##可添加新的一对指令与反馈
                
                    if (deviation_list[0] in Point_name) & (deviation_list[1] in Point_name) :
                        ##记录指令与反馈的信息
                        ##关键点
                        for iter8 in deviation_list:
                            for iter9,iter9_name in enumerate(Full_Point_name):
                                if iter9_name == iter8 :
                                    Point_Current_value.append(Current_Point_values[iter9])
                                    Point_Current_name.append(Full_Point_name[iter9])             
                        ##计算偏差值
                        deviation_ = (Point_Current_value[0] - Point_Current_value[1])/(Point_Current_value[1] + 0.001)
                        ##获取偏差的上下限值
                        for iter10 ,iter10_name in enumerate(Sub_Threshold_dataframe['kks']):

                            if iter10_name == deviation_list[0] :

                                High.append(Sub_Threshold_dataframe['normal_high'][iter10])

                                Low.append(Sub_Threshold_dataframe['normal_low'][iter10])

                                VH.append(Sub_Threshold_dataframe['limit_highest'][iter10])

                                VL.append(Sub_Threshold_dataframe['limit_lowest'][iter10])
                        ##计算偏差的置信度
                        if  (deviation_ > High[0]) & (deviation_ < VH[0]):

                            Compute_=(deviation_ - High[0])/(VH[0] - High[0])
                            Compute_point_degree.append(Compute_)

                        elif (deviation_ > VL[0]) & (deviation_ < Low[0]):

                            Compute_=(deviation_ - Low[0])/(VL - Low[0])
                            Compute_point_degree.append(Compute_)

                        elif  (deviation_ >= VH[0]) | (deviation_ <= VL[0]) :

                            Compute_point_degree.append(1)

                        elif  (deviation_ <= High[0]) & (deviation_ >= Low[0]) :

                            Compute_point_degree.append(0)
                        ##计算偏差匹配情况、故障置信度
                        X = max((Pre_condition_degree[0] - Compute_point_degree[0]) , 0)
                        ##计算结论匹配度
                        Conc_degree_ = 1.0
                        Conc_degree = 0 
                        Conc_degree_ = Conc_degree_ * (1 - max(Pre_condition_degree[0] - Compute_point_degree[0] ,0))
                        ##判断匹配度是否达到门槛
                        if  X <= Match_index :
                            Conc_degree =  Conc_degree_ * Pre_conclusion_degree  #计算结论置信度

                            return  [FaultID, Fault_name,  Point_name, Conc_degree, Device_num, Timestamp]
                            break
                        else:
                            continue
            ################################################################################################
            ##通用计算
            ##记录各个测点上下限值      
            for point_name in Point_name :

                for iter3 ,iter3_name in enumerate(Sub_Threshold_dataframe['kks']):

                    if iter3_name == point_name :

                        High.append(Sub_Threshold_dataframe['normal_high'][iter3])

                        Low.append(Sub_Threshold_dataframe['normal_low'][iter3])

                        VH.append(Sub_Threshold_dataframe['limit_highest'][iter3])

                        VL.append(Sub_Threshold_dataframe['limit_lowest'][iter3])

            ## 获取KKS当前值:Point_Current_value 
            ## 关键点
            for P_name in Point_name:
                for iter7,iter7_name in enumerate(Full_Point_name):
                    if iter7_name == P_name :
                        Point_Current_value.append(Current_Point_values[iter7])
                        Point_Current_name.append(Full_Point_name[iter7])

            ##计算征兆的证据置信度
            for iter4 in  range(len(Point_name)) :
                ##判断kks是否一致
                if Point_name[iter4] == Point_Current_name[iter4] :

                    if  (Point_Current_value[iter4] > High[iter4]) & (Point_Current_value[iter4] < VH[iter4]):

                        Compute_=(Point_Current_value[iter4]-High[iter4])/(VH[iter4]-High[iter4])
                        Compute_point_degree.append(Compute_)

                    elif (Point_Current_value[iter4] > VL[iter4]) & (Point_Current_value[iter4] < Low[iter4]):

                        Compute_=(Point_Current_value[iter4]-Low[iter4])/(VL[iter4]-Low[iter4])
                        Compute_point_degree.append(Compute_)

                    elif  (Point_Current_value[iter4] >= VH[iter4]) | (Point_Current_value[iter4] <= VL[iter4]) :

                        Compute_point_degree.append(1)

                    elif  (Point_Current_value[iter4] <= High[iter4]) & (Point_Current_value[iter4] >= Low[iter4]) :

                        Compute_point_degree.append(0)
                else :
                    print("kks不一致！")

            #计算匹配情况、故障置信度
            X = 0
            Conc_degree_ = 1.0
            Conc_degree = 0
            
            for iter5  in range(len(Point_name)) :
                ##计算匹配度
                X = X + max((Pre_condition_degree[iter5] - Compute_point_degree[iter5]) , 0)
                ##计算结论匹配度
                Conc_degree_ = Conc_degree_ * (1 - max(Pre_condition_degree[iter5] - Compute_point_degree[iter5],0))
                ##判断匹配度是否达到门槛
            if  X <= Match_index :

                Conc_degree =  Conc_degree_ * Pre_conclusion_degree  #计算结论置信度

    #             print("故障名称：%s" %Fault_name ,'\n' "置信度：%f" %Conc_degree)               
    #             break
                print("诊断有故障！")
                
                Diagnosis_list.append([FaultID, Fault_name,  Point_name, Conc_degree, Device_num, Timestamp])
#                 return  [FaultID, Fault_name,  Point_name, Conc_degree, Device_num, Timestamp]
                break
        ########################################################################################################
        ##for循环结束后，运行至此
        if  X > Match_index :
            print('诊断无故障！')

            Diagnosis_list.append([0, "无", "无", 0, Device_num, Timestamp])
#             return  [0, "无", "无", 0, Device_num, Timestamp]
        ########################################################################################################

    return Diagnosis_list



def start_diagnosis_history(Config,device_name,system_id,kks_special,start_row,end_row):
    #warn_id = 1#sys.argv[1]
    #diagnose_id = 1#sys.argv[2]
    #kind_id = 1#sys.argv[3]

    # diag_result = Fault_diagnosis(Config,device_name,system_id,kks_special,start_row,end_row,
    #                     warn_id=warn_id,diagnose_id=diagnose_id,kind_id=kind_id)
    
    # Write_mysql(Config, device_name,system_id,Host = Config.mysql_host
    #            ,User = Config.mysql_user
    #            ,Password = Config.mysql_password
    #            ,DB = Config.mysql_database
    #            ,result_list = diag_result,warn_id=warn_id,diagnose_id=diagnose_id,kind_id=kind_id)


    ##循行诊断子程序
    diag_result = Fault_diagnosis(Config,device_name,system_id,kks_special,start_row,end_row)
    ##获取故障出现时间
    fault_continue_counts = 0
    for i in range(len(diag_result)) :
        if  diag_result[i][0] != 0:
            Config.fault_datetime = diag_result[i][5]
            # print(fault_datetime)
            break

    for i in range(len(diag_result)) :
        if  diag_result[i][0] != 0:
            fault_continue_counts += 1       
    #fault_endtime = (datetime.datetime.strptime(Config.fault_datetime,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=fault_continue_counts*Config.time_interval)).strftime("%Y-%m-%d %H:%M:%S")
    # print(fault_endtime)

    # print(len(diag_result))
    # for i in range(len(diag_result)):   
    #     print(diag_result[i])

    ##for循环 将每个时间戳的诊断结果写入MySQL
    for i in range(len(diag_result)): 
        Write_mysql(Config, device_name,system_id,Host = Config.mysql_host
                   ,User = Config.mysql_user
                   ,Password = Config.mysql_password
                   ,DB = Config.mysql_database
                   ,port = Config.mysql_port
                   ,result_list = diag_result[i])
    print("诊断结果：\n",diag_result)



# In[125]:
if __name__ =='__main__' :
    ##循行诊断子程序
    diag_result = Fault_diagnosis()
    ##获取故障出现时间
    fault_continue_counts = 0
    for i in range(len(diag_result)) :
        if  diag_result[i][0] != 0:
            Config.fault_datetime = diag_result[i][5]
            # print(fault_datetime)
            break

    for i in range(len(diag_result)) :
        if  diag_result[i][0] != 0:
            fault_continue_counts += 1       
    fault_endtime = (datetime.datetime.strptime(Config.fault_datetime,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=fault_continue_counts*Config.time_interval)).strftime("%Y-%m-%d %H:%M:%S")
    # print(fault_endtime)

    # print(len(diag_result))
    # for i in range(len(diag_result)):   
    #     print(diag_result[i])

    ##for循环 将每个时间戳的诊断结果写入MySQL
    for i in range(len(diag_result)): 
        Write_mysql(Host = Config.mysql_host
                   ,User = Config.mysql_user
                   ,Password = Config.mysql_password
                   ,DB = Config.mysql_db
                   ,result_list = diag_result[i])
#     print("诊断结果：\n",diag_result)




  

