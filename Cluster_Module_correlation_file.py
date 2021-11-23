from cluster_function import *
from database import *
import numpy as np
import warnings

from qianconfig import MyLogging

myLogger = MyLogging()


class Config:
    # 输入设备名称
    device_name = '#4E磨煤机'
    system_id = 130
    # 输入测点名称，线性相关的参数以元组的形式输入,('a', 'b'), 'a'自变量 负荷, 'b'为因变量
    kks_correlation = (())

    # kks_1 = ('40LAB21CT001',)
    # MYSQL数据库参数

    mysql_host = '172.17.224.171'
    mysql_port = 3306
    mysql_user = 'root'
    mysql_password = 'Qwe123!!'
    mysql_database = 'yuhuan_monitor_prd3'

    mysql_table = 'limit_evaluation'
    mysql_sentence = ('system_id', 'kks', 'mean', 'normal_high', 'normal_low', 'limit_high', 'limit_low',
                    'limit_highest', 'limit_lowest')
    mysql_insert_sentence = 'system_id,kks,mean,normal_high,normal_low,limit_high,limit_low,limit_highest,limit_lowest'
    # Hbase数据库参数
    # hbase_host = 'localhost'
    # hbase_port = 9090
    # hbase_table = 'gaojia'
    # start_row = '2021-07-01 06:11:25'
    # end_row = '2021-07-08 10:05:20'
    # end_row = datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')
    # start_row = (datetime.datetime.now() -  datetime.timedelta(days=90)).strftime(f'%Y-%m-%d %H:%M:%S')

    # 高斯聚类参数
    n_components = 2
    # 密度聚类参数
    eps = 1
    min_samples = 10
    level_2_coeff = 0.05
    level_3_coeff = 0.1
    # 数据采集的间隔
    interval = 6


def interval_get(interval, data):
    counts = data.size
    scope = int(counts/interval)
    data_deal = []
    for i in range(scope):
        data_deal.append(data[i])
        i *= interval
    data_deal = np.array(data_deal).ravel()
    return data_deal


class ClusterModulelrfile:
    def __init__(self,config,system_id,kks,interval,table, filepath):

        self.conf = config

        self.mysql = MySQL(self.conf.mysql_host, self.conf.mysql_port, self.conf.mysql_user, self.conf.mysql_password,
                        self.conf.mysql_database)

        # self.hbase = Hbase()
        # self.hbase.connect(self.conf.hbase_host, self.conf.hbase_port)
        self.cluster = Cluster()
        self.correlation = LoadRelated()

        self.system_id = system_id
        self.kks_correlation=kks
        self.interval=interval
        self.file_path = filepath
        self.table = table

    def run(self):
        data_dict = {}
        cluster_result = {}
        correlation_dict = {}
        coex_dict = {}
        fit_value = {}
        
        load_data_dict = {}
        if self.file_path:
            data_get = pd.read_csv(self.file_path)
            if self.kks_correlation:
                # print(len(self.kks_correlation))
                for n in self.kks_correlation:
                    correlation_dict[n[0]] = []
                for i in correlation_dict.keys():
                    kks_name = correlation_dict[i]
                    for n in self.kks_correlation:
                        if i in n[0]:
                            correlation_dict[i].append(n[1])
    
                try:
                    for i in correlation_dict.keys():
                        print(i)
                        load_data = data_get[i]
                        load_data = interval_get(self.interval, load_data)
                        if load_data.size > 50000:
                            load_data = load_data[-50000:-1]
                            load_data_dict[i] = load_data
                        else:
                            load_data_dict[i] = load_data
                        kks_name = correlation_dict[i]
                        print(kks_name)
                        for kks in kks_name:
                            print('1:', kks)
                            data = data_get[kks]
                            data = interval_get(self.interval, data)
                            if data.size > 50000:
                                data = data[-50000:-1]
                                data_dict[kks] = data
                            else:
                                data_dict[kks] = data
                    #print(data_dict)
                    #print(load_data_dict)
                    # self.hbase.close()
                except:
                    #print('数据未提取成功!')
                    myLogger.write_logger('数据未提取成功!!!')
                    data_dict = {}

                if data_dict:
                    for keys in correlation_dict.keys():
                        kks_name = correlation_dict[keys]
                        for kks in kks_name:
                            fit_result = self.correlation.linear_fit(load_data_dict[keys], data_dict[kks], 1)
                            coex_dict[kks] = fit_result
                            # fit_value[correlation_dict[keys]] =
                            fit_value[kks] = load_data_dict[keys]*fit_result[0]+fit_result[1]
                    #print(coex_dict)


                    for m in fit_value.keys():
                        cluster_result[m] = self.cluster.dbscancluster(self.conf.eps, self.conf.min_samples, fit_value[m],
                                                                    self.conf.level_2_coeff, self.conf.level_3_coeff)
                        #print(cluster_result)

                    if cluster_result:
                        #self.mysql.delete(self.conf.mysql_table, self.system_id)
                        for i in fit_value.keys():
                            
                            value = (self.system_id, i, cluster_result[i][0], cluster_result[i][1], cluster_result[i][2],
                                    cluster_result[i][3], cluster_result[i][4], cluster_result[i][5], cluster_result[i][6], 0)
                            # kks_name = self.mysql.get_data('kks',self.table, 'where system_id={}'.format(self.system_id))
                            flag = self.mysql.get_data('flag', self.table, 'where system_id={} and kks={}'.format(self.system_id, i))
                            if flag == None or flag == 0:
                                self.mysql.delete_kks(self.table, self.system_id,i)
                                self.mysql.insert_data(self.table, self.conf.mysql_insert_sentence, value)
                            # if flag == 1:

                    else:
                        print('聚类失败!!!')
                        myLogger.write_logger('聚类失败!!!')
                else:
                    print('数据提取失败!!!')
                    myLogger.write_logger('数据提取失败!!!')
            else:
                print('请输入线性相关的kks参数!!!')
                myLogger.write_logger('请输入线性相关的kks参数!!!')
        else:
            print('该设备没有负荷相关测点!!!')


if __name__ == '__main__':
    cluster = ClusterModulelr(Config(), 63, (('D04:SELMW', '30LAA10CP011'), ('D04:SELMW', '40LCH61CT001')), 6, 'test_12.csv')
    cluster.run()