import numpy as np
from cluster_function import *
from database import *
import redis
import json

class Config:
    kks = ('40LAB21CT001', '40LAD61CL001', '40LAD61CP001', '40LBQ60CT002',
           '40LBQ61CP001', '40LBQ61CT001', '40LCH61CG101XQ01',
           '30LAA10CP011', '30LAB21CP001', 'D04:HPHTR3AL', '40LCH61CT001')

    # Hbase数据库参数
    hbase_host = 'localhost'
    hbase_port = 9090
    hbase_table = 'mill'
    start_row = '2021-10-18 06:11:25'
    end_row = '2021-10-18 10:05:20'

    coeff_limit = 0.9


class DataClassify:
    def __init__(self,config,model_id,versionid,system_id,kks,interval,start_row,end_row):

        self.conf = config

        self.hbase = Hbase()
        self.hbase.connect(self.conf.hbase_host, self.conf.hbase_port)

        self.system_id = system_id
        self.kks=kks
        self.interval=interval
        self.start_row=start_row
        self.end_row=end_row
        self.model_id=model_id
        self.versionid=versionid

    def run(self):
        data_dict = {}
        var_parameters = []
        kks_name = []

        if self.conf.kks:
            for n in self.conf.kks:
                kks_name.append(n)

            print(kks_name)
            try:
                for i in self.conf.kks:
                    data = self.hbase.get_data(self.conf.hbase_table, self.start_row, self.end_row, i)
                    data_dict[i] = data
                
            except:
                print('数据未提取成功!')
                data_dict = {}

            if data_dict:
                # print('2:', kks_name)
                for kks in kks_name:
                    # print('2:', kks_name)
                    high_correlation = []
                    high_correlation.append(kks)
                    for m in kks_name:
                        coef = np.corrcoef(data_dict[kks], data_dict[m])[1][0]
                        # print(coef)
                        if coef > self.conf.coeff_limit:
                            if kks == m:
                                pass
                            else:
                                high_correlation.append(m)
                    if len(high_correlation) == 1:
                        high_correlation = []
                    else:
                        var_parameters.append(tuple(high_correlation))

                    # print('1:', high_correlation)
                    kks_name = [x for x in kks_name if x not in high_correlation]

                print(var_parameters)
                lstm_parameters = tuple(kks_name)
                print(lstm_parameters)
                
                #linux
                conn = redis.StrictRedis(host='127.0.0.1',port=6379,db=2,password=123456,charset='utf-8',decode_responses=True)
                #win
                #conn = redis.StrictRedis(host='127.0.0.1',port=6379,db=1,charset='utf-8',decode_responses=True)
                
                val = {}
                val["lstm"]=kks_name
                val["var"]=var_parameters
                keys_redis = "lstmkks_"+ str(self.system_id)+"_"+str(self.model_id) +"_"+ str(self.versionid) 
                conn.set(keys_redis,json.dumps(val))

                return var_parameters, lstm_parameters

            else:
                print('数据未提取成功！！')

        else:
            print('未设定参数')


if __name__ == '__main__':
    d = DataClassify()
    d.run()