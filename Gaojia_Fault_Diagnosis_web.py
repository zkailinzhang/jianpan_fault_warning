#!/usr/bin/env python
# coding: utf-8

# In[11]:


import numpy as np
from numpy.lib.function_base import insert
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
from database import *
import uuid
import sys 
from qianconfig import MyLogging

myLogger = MyLogging()

class Conf:
    device_name = '4号机组3A高压加热器'

    mysql_host = '172.17.224.171'
    mysql_port = 3306
    mysql_user = 'root'
    mysql_password = 'Qwe123!!'
    mysql_db = 'yuhuan_monitor_prd3'

    redis_host = '172.17.224.172'
    redis_port = 6379
    redis_db = 5 #ceshi
    redis_password = '123456'


    fault_list = "fault_list"
    symptom_list = "symptom_list"
    threshold_list = "limit_list" ##该限值列表是高斯聚类的结果表
    sys_id = 63
    
    ##涉及到指令与反馈的偏差 ：反馈在前，指令在后
    special_kks_list1 = ["40CXA50020CRP01R","40CXA50006CRP01R"] ## special_kks_list1[0] 为反馈
    special_kks_list2 = ["40HFE50CG110XQ01","40HFE50AA110XQ01"] ## special_kks_list2[0] 为反馈
    
    special_kks_array = [special_kks_list1,special_kks_list2]
    
    mysql_insert_table_1 = 'device_warning_history'
    mysql_insert_table_1_sentence = 'system_id,time,device_name,warning,end_time,status,warn_id,fault_id'
    mysql_insert_table_2 = 'diagnosis_history'

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
                myLogger.write_logger('读取Redis失败！未连接')
                break
    
    point_current_info = []
    for spot_name_ in spot_name :
        print("REAL_TIME_VALUE:" + spot_name_)
        data  = conn.get("REAL_TIME_VALUE:" + spot_name_)
        if(data == None):
            continue
        data_ = eval(data)

        point_current_info.append(data_)
        
    conn.connection_pool.disconnect()
    
    return point_current_info



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
                myLogger.write_logger('读取MySQL失败！未连接')
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


def Write_mysql(Config, device_name,system_id,Host,User,Password,DB, port,result_list,warn_id,diagnose_id,kind_id) :
    
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
                myLogger.write_logger('写入MySQL失败！未连接')
                break

    diagnosis_list = str("diagnosis_list")
    diagnosis_history = str("diagnosis_history")

    ##如果故障id为0，表示未诊断出故障，不写入诊断历史储存表，只写入诊断结果表
    if ID_fault != 0 :

        #报警写入表
        mysql_bj = MySQL(Config.mysql_host, Config.mysql_port, Config.mysql_user, Config.mysql_password,
                            Config.mysql_database)
        count = mysql_bj.search_warn_fault(Config.dia_mysql_insert_table_1,system_id,ID_fault)
        count_diag = mysql_bj.search_warn_diag(Config.dia_mysql_insert_table_2,diagnose_id)
        
        #kind=1 自动调用，
        print("warn_id {},diagnose_id {},kind_id {}".format( warn_id,diagnose_id,kind_id))
        myLogger.write_logger(" 诊断结果入库  warn_id {},diagnose_id {},kind_id {}".format( warn_id,diagnose_id,kind_id))
        
        if  (count[0][0]==0 and kind_id==1):
            print("自动诊断调用")
            warn_id = warn_id
            values_1 = (system_id, str(time.time()), device_name, '异常','NULL','NULL',warn_id,'NULL')
            #设备报警历史表device_warning_history
            sql_bj = "INSERT INTO %s (system_id,time,device_name,warning,warn_id,fault_id,status) VALUES(%s,'%s','%s','%s','%s',%s,%s);" %(
                                                                                                Config.dia_mysql_insert_table_1
                                                                                                ,system_id
                                                                                                ,timestamp
                                                                                                ,device_name
                                                                                                ,'异常',
                                                                                                warn_id,ID_fault,1)
            mysql_bj.insert_data2(sql_bj) 


            ## UPDATE 语句,写入诊断结果表
            sql = "UPDATE %s set fault_id=%s,fault_name='%s',degree=%s,related_symptoms='%s',datetime='%s',device='%s' WHERE system_id=%s;" %(diagnosis_list,ID_fault,name_fault,conc_deg,Name_symptom
                                ,timestamp
                                ,device_num
                                ,system_id) 

            # 执行新增或更新数据操作,返回受影响的行数
            cursor = con.cursor()
            res_row = cursor.execute(sql)
            # 提交事务
            con.commit()

            
            #INSERT语句，写入诊断历史储存表
            sql = "INSERT INTO %s (system_id,device,fault_name,degree,datetime,fault_id,warn_id,related_symptoms) VALUES(%s,'%s','%s',%s,'%s',%s,'%s','%s');" %(
                                                                                                diagnosis_history
                                                                                                ,system_id
                                                                                                ,device_num
                                                                                                ,name_fault
                                                                                                ,conc_deg
                                                                                                ,timestamp,
                                                                                                ID_fault,
                                                                                                warn_id,
                                                                                                Name_symptom
                                                                                                )
        
            cursor = con.cursor()
            res_row = cursor.execute(sql)
            # 提交事务
            con.commit()
            # 关闭链接
            con.close()
            print(" 自动诊断调用 写入成功！")
            myLogger.write_logger('诊断结果 写入成功！设备id {} ,故障id {}'.format(system_id,ID_fault))

        elif(kind_id==0 and count_diag[0][0]==0):
            print("java诊断调用")
            diag_id = diagnose_id
            #INSERT语句，写入诊断历史储存表
            sql = "INSERT INTO %s (system_id,device,fault_name,degree,datetime,fault_id,related_symptoms) VALUES(%s,'%s','%s',%s,'%s',%s,'%s');" %(
                                                                                                diagnosis_history
                                                                                                ,system_id
                                                                                                ,device_num
                                                                                                ,name_fault
                                                                                                ,conc_deg
                                                                                                ,timestamp,
                                                                                                ID_fault,
                                                                                                Name_symptom
                                                                                                )
           
            

            cursor = con.cursor()
            res_row = cursor.execute(sql)
            # 提交事务
            con.commit()
            # 关闭链接
            con.close()
            print("写入成功！")
            myLogger.write_logger('诊断结果 写入成功！设备id {} ,故障id {}'.format(system_id,ID_fault))
        
        elif(kind_id==2):

            sql = 'select COUNT(*) from {} where system_id={} and fault_id ={} and endtime is NULL'.format(diagnosis_history, system_id,ID_fault)
            cursor = con.cursor()
            count3 = cursor.execute(sql)
            # 提交事务
            con.commit()
            
                
            if  (count3[0][0]==0):
                sql = "INSERT INTO %s (system_id,device,fault_name,degree,datetime,fault_id,warn_id,related_symptoms,kind_id) VALUES(%s,'%s','%s',%s,'%s',%s,'%s','%s',%s);" %(
                                                                                                diagnosis_history
                                                                                                ,system_id
                                                                                                ,device_num
                                                                                                ,name_fault
                                                                                                ,conc_deg
                                                                                                ,timestamp,
                                                                                                ID_fault,
                                                                                                warn_id,
                                                                                                Name_symptom,
                                                                                                kind_id
                                                                                                )
                
                Config.fault_datetime_kind2 = timestamp

                cursor = con.cursor()
                res_row = cursor.execute(sql)
                # 提交事务
                con.commit()
               
            else:

                sql = "UPDATE %s set endtime='%s' WHERE system_id=%s and device='%s' and kind_id=%s and fault_id=%s and datetime='%s';" %(diagnosis_history,timestamp
                                                                                            ,system_id
                                                                                            ,device_num
                                                                                            ,kind_id
                                                                                            ,ID_fault
                                                                                            ,Config.fault_datetime_kind2) 

                # 执行新增或更新数据操作,返回受影响的行数
                cursor = con.cursor()
                res_row = cursor.execute(sql)
                con.commit()

            
            con.close()
        else:
            myLogger.write_logger('诊断有结果 不用存表，已存在，设备id {} ,故障id {}'.format(system_id,ID_fault))


    else :
        ## UPDATE 语句,写入诊断结果表
        sql = "UPDATE %s set fault_id=%s,fault_name='%s',degree=%s,related_symptoms='%s',datetime='%s',device='%s' WHERE system_id = %s;" %(diagnosis_list,ID_fault,name_fault,conc_deg,Name_symptom
                               ,timestamp
                               ,device_num
                               ,system_id) 

        # 执行新增或更新数据操作,返回受影响的行数
        cursor = con.cursor()
        res_row = cursor.execute(sql)
        # 提交事务
        con.commit()
    
        # 关闭链接
       
        print("写入成功！")
        
        diag_id = diagnose_id
        #INSERT语句，写入诊断历史储存表
        sql = "INSERT INTO %s (system_id,device,fault_name,degree,datetime,fault_id,related_symptoms) VALUES(%s,'%s','%s',%s,'%s',%s,'%s');" %(
                                                                                            diagnosis_history
                                                                                            ,system_id
                                                                                            ,device_num
                                                                                            ,name_fault
                                                                                            ,conc_deg
                                                                                            ,timestamp,
                                                                                            ID_fault,
                                                                                            Name_symptom
                                                                                            )
    
        cursor = con.cursor()
        res_row = cursor.execute(sql)
        # 提交事务
        con.commit()
        # 关闭链接
        con.close()
        print("写入成功！")
        myLogger.write_logger('诊断结果 正常 写入成功！设备id {} ,故障id {}'.format(system_id,ID_fault))


def Fault_diagnosis(Config,device_name,sys_id,special_kks_array):
    
    Fault_dataframe,Symptom_dataframe,Threshold_dataframe = Read_mysql(Config,Host = Config.mysql_host
                                                                   ,Port = Config.mysql_port
                                                                   ,User = Config.mysql_user
                                                                   ,Password = Config.mysql_password
                                                                   ,DB = Config.mysql_database)
    
   
    ##筛选同一系统的故障表，放在Sub_Fault_dataframe内
    record_num = []
    for iter0 in  range(Fault_dataframe.shape[0]):
        if Fault_dataframe.iloc[iter0]["system_id"] == sys_id:
            record_num.append(iter0)      
    record_start = record_num[0]
    record_end = record_num[-1] + 1
    Sub_Fault_dataframe = Fault_dataframe.iloc[record_start:record_end]
    Sub_Fault_dataframe = Sub_Fault_dataframe.reset_index(drop=True)
    
    ##筛选同一系统的征兆表，放在Sub_Symptom_dataframe内
    record_num = []
    for iter0 in  range(Symptom_dataframe.shape[0]):
        if Symptom_dataframe.iloc[iter0]["system_id"] == sys_id:
            record_num.append(iter0)      
    record_start = record_num[0]
    record_end = record_num[-1] + 1
    Sub_Symptom_dataframe = Symptom_dataframe.iloc[record_start:record_end]
    Sub_Symptom_dataframe = Sub_Symptom_dataframe.reset_index(drop=True)
    
    ##筛选同一系统的限值表，放在Sub_Threshold_dataframe内
    record_num = []
    for iter0 in  range(Threshold_dataframe.shape[0]):
        if Threshold_dataframe.iloc[iter0]["system_id"] == sys_id:
            record_num.append(iter0)      
    record_start = record_num[0]
    record_end = record_num[-1] + 1
    Sub_Threshold_dataframe = Threshold_dataframe.iloc[record_start:record_end]
    Sub_Threshold_dataframe = Sub_Threshold_dataframe.reset_index(drop=True)
    
    ##记录同一系统故障对应的所有KKS
    Full_Point_name = list(np.unique(Sub_Symptom_dataframe["kks"]))

    ##从redis数据库读取KKS,Full_Point_Current_info包括 KKS名、value、时间戳
    Full_Point_Current_info = Read_Redis(pointname = Full_Point_name
                                         ,Host = Config.redis_host
                                         ,Port = Config.redis_port
                                         ,Password = Config.redis_password
                                         ,DB = Config.redis_db)
                                         
    Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #####################################################################################################
    ##依次诊断当前系统所有故障
    for iter1, fault_id_ in enumerate(Sub_Fault_dataframe['id']):
        
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
        Device_num = Sub_Fault_dataframe['device'][iter1]
    
        FaultID = Sub_Fault_dataframe['id'][iter1]
        
        Fault_name = Sub_Fault_dataframe['fault_name'][iter1]
        
        Pre_conclusion_degree = Sub_Fault_dataframe['pre_conc_degree'][iter1]
        Pre_conclusion_degree = np.array(Pre_conclusion_degree,dtype='float64')
        
        Match_index = Fault_dataframe['match_index'][iter1]
        
        ##记录故障所需测点kks  Point_name
        for iter2, point_name in enumerate(Sub_Symptom_dataframe['kks']):
    
            if Sub_Symptom_dataframe['related_fault_id'][iter2] == fault_id_ :
                
                Point_name.append(point_name)
                
                Pre_condition_degree.append(Sub_Symptom_dataframe['pre_cond_degree'][iter2])
                
        ########################################################################################### 
        ##查看当前故障的征兆是否涉及到指令与反馈的偏差
        #for deviation_list in [Config.special_kks_list1,Config.special_kks_list2]:##可添加新的一对指令与反馈
        #for deviation_list in Config.special_kks_array:##可添加新的一对指令与反馈
        if len(special_kks_array)!=0:
            for deviation_list in special_kks_array:

                if (deviation_list[0] in Point_name) & (deviation_list[1] in Point_name) :
                    ##记录指令与反馈的信息
                    for iter8 in deviation_list:
                        for iter9 in Full_Point_Current_info:
                            iter9 = eval(iter9)
                            if iter9["kks"] == iter8 :
                                Point_Current_value.append(eval(iter9["value"]))
                                Point_Current_name.append(iter9["kks"])

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
        #关键点
        for iter6 in Point_name:

            for iter7 in Full_Point_Current_info:
                iter7 = eval(iter7)
                if iter7["kks"] == iter6 :
                    Point_Current_value.append(eval(iter7["value"]))
                    Point_Current_name.append(iter7["kks"])

        ##计算征兆的证据置信度
        for iter4 in  range(len(Point_name)) :
            ##判断kks是否一致  从myslq 故障库拿，与从实时redis拿，，要不要盖出hbase历史
            if Point_name[iter4] == Point_Current_name[iter4]:

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
                myLogger.write_logger('kks不一致！核对kks及limit表')

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
            myLogger.write_logger("故障名称：{} 置信度：{} ".format(Fault_name ,Conc_degree))

            return  [FaultID, Fault_name,  Point_name, Conc_degree, Device_num, Timestamp]
            break
    ########################################################################################################
    ##for循环结束后，运行至此
    if  X > Match_index :
        print('未诊断出故障！')
        myLogger.write_logger('未诊断出故障！')
        return  [0, "无", "无", 0, Device_num, Timestamp]
    ########################################################################################################


def start_diagnosis(Config,device_name,system_id,kks_special,warn_id,diagnose_id,kind_id):
    #warn_id = 1 #sys.argv[1]
    #diagnose_id = 1 #sys.argv[2]
    #kind_id = 2 #sys.argv[3]

    diag_result = Fault_diagnosis(Config,device_name,system_id,kks_special)
    
    Write_mysql(Config, device_name,system_id,Host = Config.mysql_host
               ,User = Config.mysql_user
               ,Password = Config.mysql_password
               ,DB = Config.mysql_database
               ,port = Config.mysql_port
               ,result_list = diag_result,warn_id=warn_id,diagnose_id=diagnose_id,kind_id=kind_id)
    
    print("诊断结果：\n",diag_result)
# 预警发布，添加 kks_sepcial,参数，
# 不用脚本，改用代码，调用，kind=1,





if __name__ =='__main__' :
    import argparse

    # parser = argparse.ArgumentParser(description='manual to this script')
    # parser.add_argument('--warn_id', type=int, default=1)
    # #parser.add_argument('--int-input', type=int, default=32)
    # #parser.add_argument('--list-input', type=list, default=[1,2,3])
    # args = parser.parse_args()
    
    #qq = sys.argv[0]
    warn_id = 1#sys.argv[1]
    diagnose_id = 1#sys.argv[2]
    kind_id = 1#sys.argv[3]

    diag_result = Fault_diagnosis(Conf.sys_id)
    
    Write_mysql( Host = Conf.mysql_host
               ,User = Conf.mysql_user
               ,Password = Conf.mysql_password
               ,DB = Conf.mysql_db
               ,result_list = diag_result,warn_id=warn_id,diagnose_id=diagnose_id,kind_id=kind_id)

    print("诊断结果：\n",diag_result)
    





