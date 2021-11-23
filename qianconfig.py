# -*- coding: utf-8 -*-

import os 
from enum import Enum
import logging 

class Config:
    


    #要考虑所有系统的，通用性，
    mysql_host = '172.17.224.171'
    mysql_port = 3306
    mysql_user = 'root'
    mysql_password = 'Qwe123!!'
    #mysql_database = 'yuhuan_monitor_prd3'
    mysql_database = 'yuhuan_monitor_test'

    # mysql_host = 'www.bccat.top'
    # mysql_port = 4407
    # mysql_password = 'XzNNkUAxYXk8NYpU'
    # mysql_database = 'yuhuan_monitor_dev'
    # mysql_user = 'root'

    hbase_host = '172.17.224.171'
    hbase_port = 9000
    hbase_table = 'history_point_new'

    hbase2_port = 9090

    redis_host = '172.17.224.172'
    redis_port = 6379
    redis_db = 6 #ceshi
    #redis_db = 0 #zhengshi
    redis_password = '123456'
    
    #1 普通测点，，聚类训练，出三个区间 从hbase 5w点，存mysql
    mysql_table = 'limit_list'
    mysql_sentence = ('system_id','mean','normal_high','normal_low','limit_high','limit_low','limit_highest','limit_lowest')
    mysql_insert_sentence = 'system_id,kks,mean,normal_high,normal_low,limit_high,limit_low,limit_highest,limit_lowest,flag'
    
    #这个时间戳从页面拿了是吧，每个模型还不一样呢
    start_row = '2021-10-18 16:11:25'
    end_row = '2021-10-24 10:05:20'

    #添加模型名称，模型id   这下面三个要传进来
    device_name = '4号机组3A高压加热器'
    system_id = 63
    # 输入测点名称
    # #'40LCH61CT001','30LAB21CP001','30LAA10CP011','40LAB21CT002'
    kks = ('40LAB21CT001', '40LAD61CL001',
            '40LAD61CP001', '40LBQ60CT002',
            '40LBQ61CP001', '40LBQ61CT001', '40LCH61CG101XQ01',
              'D04:HPHTR3AL',  '40LAB21CT002','40LCH61CT001','30LAB21CP001','30LAA10CP011')


    # 高斯聚类参数
    n_components = 2
    # 密度聚类参数
    eps = 3
    min_samples = 10
    level_2_coeff = 0.05
    level_3_coeff = 0.1
    interval = 6
    java_host_train_db = "http://172.17.224.171:40069/smartModel/trainCall"
    #java_host_train_db = "http://192.168.18.28:40069/modelTrain/getModelTrainResult"

    #每个模型的时间戳不一样，每个模型的表语句不一样，村表，查询表，  训练版本 模型

    #1.1 线性拟合测点 +db
    #和上面参数一致
    java_host_train_lrdb = "http://172.17.224.171:40069/smartModel/trainCall"

    #2.0 lstm var 所有常规kks ，测点分组 存redis
    coeff_limit = 0.9
    java_host_train_lstm_kks = "http://172.17.224.171:40069/smartModel/trainCall"


    #2.1 lstm训练 保存文件 从hbase 1w点  存本地
    model_length = 200
    model_inputshape = (model_length, 1)

    #file_path_model = '{}_lstm_model_dict.pkl'.format(system_id)
    # lstm模型参数
    layers = 1
    # 数据采集间隔
    interavl_lstm = 5

    java_host_train_lstm = "http://172.17.224.171:40069/smartModel/trainCall"


    java_host_train_db_file = "http://172.17.224.171:40069/smartModel/trainCall"
    java_host_train_lrdb_file = "http://172.17.224.171:40069/smartModel/trainCall"
    java_host_train_lstm_kks_file = "http://172.17.224.171:40069/smartModel/trainCall"
    java_host_train_lstm_file = "http://172.17.224.171:40069/smartModel/trainCall"

    #3 var训练 预测，lstm预测，从hbase  200个，存redis 存hbase，需要均值判断设备异常
    java_host_predict_lstm_var= "http://172.17.224.171:40069/smartModel/releasedCall"
    

    pre_mysql_table = 'limit_list'
    pre_mysql_sentence_1 = 'kks'
    pre_mysql_sentence_2 = 'normal_high'
    pre_mysql_sentence_3 = 'mean'
    # 设备预警历史状态表
    pre_mysql_insert_table_1 = 'device_warning_history'
    pre_mysql_insert_table_1_sentence = 'system_id,time,device_name,warning,end_time,status,warn_id,fault_id'
    # kks测点预警历史状态表
    pre_mysql_insert_table_2 = 'kks_warning_history'
    pre_mysql_insert_table_2_sentence = 'system_id,time,device_name,kks,warning'
    pre_interval =5

    pre_hbase_insert_cf = 'default'
    pre_hbase_insert_table = 'history_predict_result_test'
    
    #预警报警，触发诊断，调自己诊断接口，  不用调java回调
    url = 'http://localhost:8484/diagnosis'
    


    #预警评估
    java_host_evaluate= "http://172.17.224.171:40069/smartModel/evaluateCall"
    pre_hbase_insert_table2 =  'history_warn_predict_test'
    
    #4.0 故障，从redis 实时值，从mysql 一三级，存mysql
    dia_mysql_insert_table_1 = pre_mysql_insert_table_1
    dia_mysql_insert_table_1_sentence = pre_mysql_insert_table_1_sentence
    dia_mysql_insert_table_2 = 'diagnosis_history'

    fault_list = "fault_list"
    symptom_list = "symptom_list"
    threshold_list = "limit_list" 
    
    fault_datetime_kind2= "0000-00-00 00:00:00"
    
    java_host_diagnosis= "http://172.17.224.171:40069/fault/model/getReleaseResult"

    #4.1 诊断历史hbase
    fault_datetime = "0000-00-00 00:00:00"
    time_interval =5

    java_host_diagnosis_history= "http://172.17.224.171:40069/fault/model/getEvaluationResult"

    #4.2 诊断结果页面，诊断
    java_host_diagnosis_result_diag= "http://172.17.224.171:40069/equipment/equipmentDiagnosisCall"



class Qushi(Enum):
    
    CHIXU_PING = 1
    CHIXU_SHENG = 2
    
    CHIXU_JIANG = 3
    TUBIAN_SHENG = 4
    TUBIAN_JIANG= 5 
    TUBIAN_PING = 6 



class MyLogging:
    # 初始化日志
    def __init__(self):
        #self.logPath = r'D:/Company_Code/All_Python_Code/日期排序/十月/多个文件使用logging/'
        #self.logName = 'xxx.log'
        #self.logFile = self.logPath + self.logName
        self.logFile = 'log/serving.qian.std.out'
        # 日志的输出格式
        fh = logging.FileHandler("test.log",encoding="utf-8",mode="a")
        logging.basicConfig(
            level=logging.DEBUG,  # 级别：CRITICAL > ERROR > WARNING > INFO > DEBUG，默认级别为 WARNING
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s:  %(message)s',
            # format='%(asctime)s %(name)s:%(levelname)s:%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=self.logFile,
            filemode='a',
            )

    def write_logger(self, content):
        #logging.debug(content)
        logging.info(content)
        # 可以写其他的函数,使用其他级别的log  
        
    def error_logger(self,content):
        logging.error(content)

    # @staticmethod
    # def write_logger(content):
    #     logging.debug(content)

    # @staticmethod
    # def error_logger(content):
    #     logging.error(content)