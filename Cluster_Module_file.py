from cluster_function import *
from database import *
import numpy as np
import warnings
import datetime

from qianconfig import MyLogging

myLogger = MyLogging()





class Config:
    # 输入设备名称

    
    device_name = '4号机组3A高压加热器'
    system_id = 63
    # 输入测点名称
    # #'40LCH61CT001','30LAB21CP001','30LAA10CP011','40LAB21CT002'
    kks = ('40LAB21CT001', '40LAD61CL001',
            '40LAD61CP001', '40LBQ60CT002',
            '40LBQ61CP001', '40LBQ61CT001', '40LCH61CG101XQ01',
            'D04:HPHTR3AL',  '40LAB21CT002','40LCH61CT001','30LAB21CP001','30LAA10CP011')
    # '40LCH61CT001','30LAB21CP001'
    # 这两个目前没有
    # '30LAA10CP011',没有
    # kks = ('40LAB21CT001', '40LAD61CL001',
    #         '40LAD61CP001', '40LBQ60CT002',
    #      '40LBQ61CP001', '40LBQ61CT001', '40LCH61CG101XQ01',
    #            'D04:HPHTR3AL',  '40LAB21CT002')

    # kks_1 = ('40LAB21CT001',)
    # MYSQL数据库参数
    #限值表 故障诊断表
    mysql_host = 'localhost'
    mysql_port = 3306
    mysql_user = 'root'
    mysql_password = '187950'
    mysql_database = 'test'
    
    mysql_table = 'limit_evaluation'

    mysql_sentence = ('system_id','mean','normal_high','normal_low','limit_high','limit_low','limit_highest','limit_lowest')
    mysql_insert_sentence = 'system_id,kks,mean,normal_high,normal_low,limit_high,limit_low,limit_highest,limit_lowest'
    # Hbase数据库参数  实时 历史数据
    # hbase_host = '192.168.10.209'
    # hbase_port = 9090
    # hbase_table = 'gaojia'

    # hbase_host = '172.17.224.171'
    # hbase_port = 9000
    # hbase_table = 'history_point_new'
    # start_row = '2021-10-18 16:11:25'
    # end_row = '2021-10-24 10:05:20'

    # start_row = '2020-08-02 06:11:25'
    # end_row = '2020-08-02 10:05:20'

    # hbase_table = 'history_point'
    #start_row = (datetime.datetime.now()-datetime.timedelta(days=7)).strftime(f'%Y-%m-%d %H:%M:%S')
    #end_row = (datetime.datetime.now()-datetime.timedelta(days=17)).strftime(f'%Y-%m-%d %H:%M:%S')
    

    #tart_row = (datetime.datetime.now()-datetime.timedelta(days=100)).strftime(f'%Y-%m-%d %H:%M:%S')
    #end_row = (datetime.datetime.now()-datetime.timedelta(days=99)).strftime(f'%Y-%m-%d %H:%M:%S')


    # end_row
    # 高斯聚类参数
    n_components = 2
    # 密度聚类参数
    eps = 0.5
    min_samples = 10
    level_2_coeff = 0.05
    level_3_coeff = 0.1
    # 数据采集的间隔
    interval = 12


def interval_get(interval, data):
    counts = data.size
    scope = int(counts/interval)
    data_deal = []
    for i in range(scope):
        data_deal.append(data[i])
        i *= interval
    data_deal = np.array(data_deal).ravel()
    return data_deal


class ClusterModulefile:

    def __init__(self,Config,system_id,kks,interval,table,local_path_data):

        self.conf = Config
        self.mysql = MySQL(self.conf.mysql_host, self.conf.mysql_port, self.conf.mysql_user, self.conf.mysql_password,
                        self.conf.mysql_database)

        # self.hbase = Hbase()
        # self.hbase.connect(self.conf.hbase_host, self.conf.hbase_port)
        
        self.cluster = Cluster()

        self.system_id = system_id
        self.kks=kks
        self.interval=interval
        # self.start_row=start_row
        # self.end_row=end_row
        self.file_path = local_path_data
        self.table = table

    def run(self):
        data_dict = {}
        cluster_result = {}
        if self.file_path:
            if self.kks:
                # for i in self.kks:
                data_get = pd.read_csv(self.file_path)
                # print(data_get)
                # print(data_get)
                # 时间列
                # time = data_get.iloc[:, 0]
                # # 在时间列找到输入参数的位置
                # index_start = np.where(time == self.start_row)[0][0]
                # index_end = np.where(time == self.end_row)[0][0]
                # print(index_start, index_end)
                # try:
                #     for i in self.kks:
                #         print('1:', i)
                #         index_kks = np.where(kks == i)[0][0]
                #         print(index_kks)[0][0]
                #         data = data_get.iloc[index_start:index_end, index_kks]
                #         data = np.array(data).astype(float)
                #         if data.size > 50000:
                #             data = data[-50000:-1]
                #             data_dict[i] = data
                #         else:
                #             data_dict[i] = data
                #     # self.hbase.close()
                # except:
                #     # print('数据未提取成功!')
                #     myLogger.write_logger('聚类hbase数据未提取成功!')
                #     data_dict = {}
                for i in self.kks:
                    print('1:', i)
                    data = data_get[i]
                    data = data.iloc[1:]
                    # data = data.iloc[index_start:index_end]
                    data = np.array(data).astype(float)
                    data = interval_get(self.interval, data)
                    print(data.size)
                    if data.size > 50000:
                        data = data[-50000:-1]
                        data_dict[i] = data
                    else:
                        data_dict[i] = data

                if data_dict:
                    for m in self.kks:
                        cluster_result[m] = self.cluster.dbscancluster(self.conf.eps, self.conf.min_samples, data_dict[m],
                                                                    self.conf.level_2_coeff, self.conf.level_3_coeff)

                    if cluster_result:
                        # self.mysql.delete(Config.mysql_table, Config.system_id)
                        for i in self.kks:
                            value = (self.system_id, i, cluster_result[i][0], cluster_result[i][1], cluster_result[i][2],
                                    cluster_result[i][3], cluster_result[i][4], cluster_result[i][5], cluster_result[i][6], 0)
                            # kks_name = self.mysql.get_data('kks',self.table, 'where system_id={}'.format(self.system_id))
                            flag = self.mysql.get_data('flag', self.table, 'where system_id={} and kks={}'.format(self.system_id, i))
                            if flag == None or flag == 0:
                                self.mysql.delete_kks(self.table, self.system_id,i)
                                self.mysql.insert_data(self.table, self.conf.mysql_insert_sentence, value)
                            # if flag == 1:
                            
                        self.mysql.cursor.close()
                        # self.hbase.close()

                    else:
                        print('聚类失败!!!')
                        myLogger.write_logger('聚类失败!!!')
                else:
                    print('数据提取失败!!!')
                    myLogger.write_logger('数据提取失败!!!')
            else:
                print('请输入kks参数!!!')
                myLogger.write_logger('请输入kks参数!!!')
        else:
            myLogger.write_logger('请输入文件地址!!!')
            print('请输入文件地址!!!')


if __name__ == '__main__':
    cluster = ClusterModule(Config(), 63, ['40LAB21CT001', '40LAD61CL001', '40LAD61CP001', '40LBQ60CT002', '40LBQ61CP001', 
                                '40LBQ61CT001', '40LCH61CG101XQ01', 'D04:HPHTR3AL', '40LAB21CT002', '40LCH61CT001', 
                                '30LAB21CP001', '30LAA10CP011'], 12,  
                            'test_12.csv')
    cluster.run()  