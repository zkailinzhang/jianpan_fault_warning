import matplotlib
matplotlib.use('Agg')
import numpy as np
from predict_function import *
from database import *
import pickle
import tensorflow as tf
from scipy.spatial import distance
from scipy.spatial.distance import cdist
import time
import os
import datetime

import uuid
from concurrent.futures import ThreadPoolExecutor
import json
import requests
import subprocess
from matplotlib import pyplot as plt
#import matplotlib.pyplot as plt

executor = ThreadPoolExecutor(4)
from qianconfig import MyLogging

myLogger = MyLogging()

def interval_get(interval, data):
    counts = data.size
    scope = int(counts/interval)
    data_deal = []
    for i in range(scope):
        data_deal.append(data[i])
        i *= interval
    data_deal = np.array(data_deal).ravel()
    return data_deal

class Config:
    device_name = '4号机组3A高压加热器'
    system_id = 63

    #'40LCH61CT001'3A高加疏水出口温度 PI有 hbase没有 ,30LAB21CP001 3A高加给水出口压力 PI有 hbase没有,
    kks = ('40LAB21CT001', '40LAD61CL001', '40LAD61CP001', '40LBQ60CT002',
           '40LBQ61CP001', '40LBQ61CT001', '40LCH61CG101XQ01',
           '30LAA10CP011', '30LAB21CP001', 'D04:HPHTR3AL', '40LCH61CT001', '40LAB21CT002')

    var_parameters = [('40LAB21CT001', '40LAD61CP001', '40LBQ61CP001', '40LCH61CT001'),
                      ('40LBQ60CT002', '40LBQ61CT001'), ('30LAA10CP011', '30LAB21CP001')]

    #('40LCH61CG101XQ01', '40LAD61CL001', 'D04:HPHTR3AL')
    #
    # kks = ('40LAB21CT001', '40LAD61CL001', '40LAD61CP001', '40LBQ60CT002',
    #        '40LBQ61CP001', '40LBQ61CT001', '40LCH61CG101XQ01',
    #         'D04:HPHTR3AL','40LAB21CT002')

    kks_all = ('40LAB21CT001', '40LAD61CL001', '40LAD61CP001', '40LBQ60CT002',
           '40LBQ61CP001', '40LBQ61CT001', '40LCH61CG101XQ01',
            'D04:HPHTR3AL','40LAB21CT002','30LAB21CP001','40LCH61CT001','30LAA10CP011')

    # var_parameters = [('40LAB21CT001', '40LAD61CP001', '40LBQ61CP001'),
    #                   ('40LBQ60CT002', '40LBQ61CT001')]


    # '40LCH61CT001','30LAB21CP001'
    # 这两个目前没有
    # '30LAA10CP011',没有

    # MYSQL数据库参数

    mysql_host = '172.17.224.171'
    mysql_port = 3306
    mysql_user = 'root'
    mysql_password = 'Qwe123!!'
    mysql_database = 'yuhuan_monitor_prd3'

    mysql_table = 'limit_list'
    mysql_sentence_1 = 'kks'
    mysql_sentence_2 = 'normal_high'
    mysql_sentence_3 = 'mean'
    # 设备预警历史状态表
    mysql_insert_table_1 = 'device_warning_history'
    mysql_insert_table_1_sentence = 'system_id,time,device_name,warning,end_time,status,warn_id,fault_id'
    # kks测点预警历史状态表
    mysql_insert_table_2 = 'kks_warning_history'
    mysql_insert_table_2_sentence = 'system_id,time,device_name,kks,warning'
    # Hbase数据库参数

    #start_row = '2021-07-04 17:47:55'
    #end_row = '2021-07-04 18:04:35'
    #start_row = datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')
    #end_row = (datetime.datetime.now()-datetime.timedelta(minutes=18)).strftime(f'%Y-%m-%d %H:%M:%S')


    hbase_host = '172.17.224.171'
    hbase_port = 9000
    hbase_table = 'history_point_new'
    start_row = '2021-10-19 09:12:50'
    end_row = '2021-10-19 09:29:30'
    # start_row = '2020-08-02 06:11:25'
    # end_row = '2020-08-02 10:05:20'


    # start_row = end_row-{}
    # end_row = time.time()
    hbase_insert_cf = 'default'
    hbase_insert_table = 'history_predict_result_test'

    # redis数据库参数
    redis_host = '172.17.224.172'
    redis_port = 6379
    redis_database = 0
    redis_password = '123456'


    # 模型路径
    model_path_dir = '{}_lstm_model_dict.pkl'.format(system_id)
    # 数据采集间隔
    interval = 1


header = {'Content-Type': 'application/json','Accept': 'application/json'} 



def diagnose_task(url,warn_id,system_id,device_name ,kks_special):
    print("设备异常开始诊断\n")
    #os.system('./start_diagnose_dingshi_gaojia_63.sh {} {} {}'.format(warn_id,1,1))

    #调用诊断接口
    #url = 'http://localhost:8383/diagnosis'
    i =0
    datad = {
   
    "device_name": device_name,
    "device_id": system_id,
    "kks" : kks_special,
    "warn_id":warn_id,
    "diagnose_id":1,
    "kind_id":1,
    "fault_id":10010

    }
    #事件调度：若设备异常报警，则触发诊断接口，即在预警代码里调用诊断接口，10分钟，每5s诊断一次。
    r = requests.post(url, data=json.dumps(datad),headers=header)
    print(r.text)
        



class Predict:
    def __init__(self,config,kks_special,device_name,system_id,kks_all,kks,var_kks,start_row,end_row):
        # start_1 = time.time()

        self.conf = config


        self.hbase = Hbase()
        self.hbase.connect(self.conf.hbase_host, self.conf.hbase_port)
        self.redis = RedisControl(self.conf.redis_host, self.conf.redis_port, self.conf.redis_db,self.conf.redis_password)
        self.mysql = MySQL(self.conf.mysql_host, self.conf.mysql_port, self.conf.mysql_user, self.conf.mysql_password,
                           self.conf.mysql_database)
        self.lstm = LstmFunction()
        self.var = VarFunction()
        # end_2 = time.time()
        # print(end_2 - start_1)
        
        self.system_id = system_id
        self.device_name = device_name
        self.kks_all=kks_all
        self.kks=kks
        self.var_parameters=var_kks

        self.start_row=start_row
        self.end_row=end_row

        self.kks_special=kks_special

        self.model_path_dir = '{}_lstm_model_dict.pkl'.format(self.system_id)

        self.url = self.conf.url

    def run(self):
        start = time.time()
        # f = open(Config.model_path_dir, 'rb')
        # model_dir_dict = pickle.load(f)
        # print(model_dir_dict)
        data_predict_dict = {}
        lstm_model_dict = {}
        minmax_dict = {}
        y_predicted_lstm = {}
        y_predicted_var = {}
        # 判断是否模型训练完成
        if os.path.exists(self.model_path_dir):
            f = open(self.model_path_dir, 'rb')
            model_dir_dict = pickle.load(f)
            if self.kks and self.var_parameters:
                # 判断是否获取到路径
                if model_dir_dict:
                    for i in model_dir_dict.keys():
                        time.sleep(3)
                        lstm_model_dict[i] = tf.keras.models.load_model(model_dir_dict[i])
                    print(lstm_model_dict)
                    print('lstm模型加载成功！')
                    myLogger.write_logger('lstm模型加载成功！')
                else:
                    print('lstm模型未加载或模型未训练完成!!')
                    myLogger.write_logger('lstm模型未加载或模型未训练完成!!')

                if lstm_model_dict:
                    # 从hbase中取出数据
                    for i in self.kks:
                        data = self.hbase.get_data(self.conf.hbase_table, self.start_row, self.end_row, i)
                        #data = interval_get(self.conf.pre_interval, data)
                        if data.size > 200:
                            #data = data[-1, -200]
                            data = data[-200:]
                        else:
                            pass
                        data_predict_dict[i] = data

                    if data_predict_dict:
                        for i in lstm_model_dict.keys():
                            minmax_dict[i] = MinMaxScaler()

                        # lstm模型预测
                        for i in lstm_model_dict.keys():
                            data_predict = savgol_filter(data_predict_dict[i], 13, 3)
                            data_predict = minmax_dict[i].fit_transform(data_predict.reshape(-1, 1))
                            # data_predict = data_predict.reshape(-1, 1)
                            data_predict = data_predict.reshape(1, 200, 1)
                            y_predicted_lstm[i] = float(
                                minmax_dict[i].inverse_transform(self.lstm.predict(lstm_model_dict[i],
                                                                                   data_predict)).ravel())
                        #print(y_predicted_lstm)
                        # var模型预测
                        y_predicted_var = self.var.forecast(self.var_parameters, data_predict_dict)
                        #print(y_predicted_var)

                        y_predicted_var.update(y_predicted_lstm)
                        print('y:', y_predicted_var)

                        # 将预测值存入到hbase与redis中
                        #now = str(time.time())
                        Timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        for i in y_predicted_var.keys():
                            self.redis.set_string('{}:{}_predicted_value'.format(self.device_name,i), '设备名称:{}  kks:{}  预测值:{}'.
                                                  format(self.device_name, i, y_predicted_var[i]))
                            cf = self.conf.pre_hbase_insert_cf + ':' +str(self.system_id)+ ':' + i
                            value = float(y_predicted_var[i])
                            value_1 = np.str(value)
                            self.hbase.insert_data(self.conf.pre_hbase_insert_table, Timestamp, cf, value_1)
                        end_1 = time.time()

                        # 与限值对比
                        limit_dict = {}
                        mean_dict = {}
                        normal_dict = {}
                        limit = self.mysql.get_data(self.conf.pre_mysql_sentence_2, self.conf.pre_mysql_table,
                                                    'where system_id={}'.format(self.system_id))
                        kks_name = self.mysql.get_data(self.conf.pre_mysql_sentence_1, self.conf.pre_mysql_table,
                                                       'where system_id={}'.format(self.system_id))
                        mean = self.mysql.get_data(self.conf.pre_mysql_sentence_3, self.conf.pre_mysql_table,
                                                   'where system_id={}'.format(self.system_id))
                        # normal_limit = self.mysql.get_data('normal_high', Config.mysql_table, len(Config.kks))
                        #print(kks_name)
                        #print(mean)
                        #print(limit)             

                        if kks_name:
                            for i in range(len(self.kks_all)):
                                # print(kks_name)
                                mean_dict[kks_name[i][0]] = mean[i][0]
                                limit_dict[kks_name[i][0]] = limit[i][0]
                                # normal_dict[kks_name[i][0]] = normal_limit[i][0]
                            #print('lm:', limit_dict)

                            limit_point = []
                            predict_point = []
                            mean_point = []
                            for i in y_predicted_var.keys():
                                predict_point.append(y_predicted_var[i])
                                limit_point.append(limit_dict[i])
                                mean_point.append(mean_dict[i])
                                if y_predicted_var[i] > limit_dict[i]:
                                    self.redis.set_string('{}:{}_predicted_value'.format(self.device_name,i),
                                                          '设备名称:{}  kks:{} 状态:超一级高限!'.
                                                          format(self.device_name, i, ))
                                    Timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    insert_values = (self.system_id, Timestamp, self.device_name, str(i), '超二级高限')
                                    #self.mysql.insert_data(Config.mysql_insert_table_2,
                                    #                       Config.mysql_insert_table_2_sentence, insert_values)
                                else:
                                    self.redis.set_string('{}:{}_predicted_value'.format(self.device_name,i),
                                                          '设备名称:{}  kks:{} 状态:正常!'.
                                                          format(self.device_name, i, ))

                            mark_dist = distance.euclidean(limit_point, mean_point)
                            real_dist = distance.euclidean(predict_point, mean_point)
                            if real_dist - mark_dist > 5:

                                print('设备异常!!!')
                                myLogger.write_logger('预警设备异常!!!')
                                warn_id = str(uuid.uuid1())

                                #values_1 = (Config.system_id, str(time.time()), Config.device_name, '异常',None,None,warn_id,None)
                                
                                #count = self.mysql.search_warn_fault(Config.mysql_insert_table_1, Config.system_id,
                                                       #warn_id)
                                #if(count==0):
                                    #self.mysql.insert_data(Config.mysql_insert_table_1, Config.mysql_insert_table_1_sentence,
                                    #                   values_1)
                                self.redis.set_string('device_situation', '{}状态: 异常'.format(self.device_name))

                                #设备报警，开始诊断代码 每间隔5s，10mins
                                #os.system('./start_diagnose_dingshi_gaojia_63.sh {}'.format(warn_id))
                                
                                executor.submit(diagnose_task,self.url,warn_id,self.system_id,self.device_name ,self.kks_special)

                            else:
                                self.redis.set_string('device_situation', '{}状态: 正常'.format(self.device_name))
                        else:
                            print('未聚类完成!!!')
            end = time.time()
            self.hbase.close()
            print(end - start)
        else:
            print('模型未训练完成！！')
        
        return y_predicted_var

if __name__ == '__main__':
    predict = Predict()
    predict.run() 

    """
    predict_y = {}
    for m in Config.kks:
        predict_y[m] = []

    start = (datetime.datetime.strptime(Config.end_row, "%Y-%m-%d %H:%M:%S") +
                            datetime.timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")
    end = (datetime.datetime.strptime(Config.end_row, "%Y-%m-%d %H:%M:%S") +
                            datetime.timedelta(seconds=80)).strftime("%Y-%m-%d %H:%M:%S")
    for i in range(15):
        print("多少次 {} \n".format(i))
        predict = Predict()
        y = predict.run()
        for kks in y.keys():
            predict_y[kks].append(y[kks])

        Config.start_row = (datetime.datetime.strptime(Config.start_row, "%Y-%m-%d %H:%M:%S") +
                            datetime.timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")
        Config.end_row = (datetime.datetime.strptime(Config.start_row, "%Y-%m-%d %H:%M:%S") +
                            datetime.timedelta(seconds=1000)).strftime("%Y-%m-%d %H:%M:%S")

    # hbase_data = Hbase()
    # hbase_data.connect('localhost', 9090)

    for k in Config.kks[0:9]:
        hbase_data = Hbase()
        hbase_data.connect(Config.hbase_host, Config.hbase_port)
        data = hbase_data.get_data(Config.hbase_table, start, end, k)
        hbase_data.close()
        print("huatu\n")
        print(data)
        print('\n')
        print(predict_y[k])
        plt.plot(data, label='real')
        plt.plot(predict_y[k], label='predict')
        plt.title(k)
        plt.legend()
        plt.show()
        ss = "save/"+str(k)+"_.png"
        plt.savefig(ss)
        plt.close()

    print(predict_y[Config.kks[0]])
    """