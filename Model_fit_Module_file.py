from numpy import e
from predict_function import *
from database import *
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
from scipy.signal._savitzky_golay import savgol_filter
from sklearn.preprocessing import MinMaxScaler
import pickle
import datetime
import redis
import json


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
    kks = ('40LCH61CG101XQ01', '40LAD61CL001', 'D04:HPHTR3AL')
    # hbase数据库参数设置
    hbase_host = '172.17.224.171'
    hbase_port = 9000
    hbase_table = 'history_point_new'
    #start_row = '2021-07-01 06:11:25'
    #end_row = '2021-07-08 10:05:20'

    start_row = '2020-10-18 06:11:25'
    end_row = '2020-10-19 06:11:25'
    #start_row = (datetime.datetime.now()-datetime.timedelta(days=7)).strftime(f'%Y-%m-%d %H:%M:%S')

    #start_row = datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')
    #end_row = (datetime.datetime.now()-datetime.timedelta(minutes=18)).strftime(f'%Y-%m-%d %H:%M:%S')
    
    # 模型参数
    model_length = 200
    model_inputshape = (model_length, 1)
    # 模型保存路径
    model_save_path = ''
    # 文件路径

    file_path = '{}_lstm_model_dict.pkl'.format(system_id)
    # lstm模型参数
    layers = 1
    # 数据采集间隔
    interval = 5



class ModelFITfile:
    # filepath为csv文件的路径  
    def __init__(self,config, system_id, kks, filepath):
        self.conf = config
        # self.hbase = Hbase()
        # self.hbase.connect(Config.hbase_host, Config.hbase_port)
        self.lstm = LstmFunction()

        self.system_id = system_id
    
        self.kks=kks
        self.interval=self.conf.interval
        self.file_path = filepath

        self.file_path_model = '{}_lstm_model_dict.pkl'.format(self.system_id)

    def run(self):
        data_dict = {}
        data_fit_dict = {}
        minmax_dict = {}
        lstm_model_dict = {}
        lstm_model_dir = {}
        if self.file_path:
            
            data_get = pd.read_csv(self.file_path)
            
            # var_parameters = getv["var"]

            # try:
            #     for i in self.kks:
            #         print(i)
            #         minmax_dict[i] = MinMaxScaler()
            #         data_get = self.hbase.get_data(self.conf.hbase_table, self.start_row, self.end_row, i)
            #         if data_get.size > 10000:
            #             data_get = data_get[-10000:-1]
            #         else:
            #             data_get = data_get
            #         data_dict[i] = savgol_filter(data_get, 13, 3)
            #         data_dict[i] = minmax_dict[i].fit_transform(data_dict[i].reshape(-1, 1))
            #     self.hbase.close()
            # except:
            #     print('数据未提取成功!')
            #     data_dict = {}
            for i in self.kks:
                print('1:', i)
                minmax_dict[i] = MinMaxScaler()
                data = data_get[i]
                # data = data.iloc[index_start:index_end]
                data = np.array(data).astype(float)
                data = interval_get(self.interval, data)
                print(data.size)
                if data.size > 10000:
                    data = data[-10000:-1]
                    # data_dict[i] = data
                else:
                    data = data
                data_dict[i] = savgol_filter(data, 13, 3)
                data_dict[i] = minmax_dict[i].fit_transform(data_dict[i].reshape(-1, 1))

            if data_dict:
                for i in data_dict.keys():
                    # data = savgol_filter(data_dict[i], 13, 3)
                    data = data_dict[i]
                    data = data.reshape(-1, 1)
                    data_fit = TimeseriesGenerator(data, data, length=self.conf.model_length, batch_size=1)
                    data_fit_dict[i] = data_fit

                if data_fit_dict:
                    for i in data_fit_dict.keys():
                        print(i)
                        self.lstm.build_model(self.conf.model_inputshape, self.conf.layers)
                        lstm_model_dict[i] = self.lstm.fit(data_fit_dict[i])

                    count = 0

                    #模型路径 多级
                    path_data = './model/' + str(self.system_id)+'/'
                    if not os.path.exists(path_data):  os.makedirs( path_data )
                    pathcwd = os.path.dirname(__file__)

                    if lstm_model_dict:
                        for i in lstm_model_dict.keys():
                            # print(i)
                            filepath = 'model_{}.h5'.format(count)
                            #linux
                            local_path_data = os.path.join(pathcwd,'model/' + str(self.system_id)+'/'+ filepath)
                            #win
                            #local_path_data = os.path.join(pathcwd,'model'+'\\' + str(Config.system_id)+'\\'+ filepath)  
                            print(local_path_data)
                            lstm_model_dir[i] = local_path_data
                            lstm_model_dict[i].save(local_path_data)
                            count += 1
                        # 模型路径的保存
                        model_save = open(self.file_path_model, 'wb')
                        pickle.dump(lstm_model_dir, model_save)
                        model_save.close()
                    else:
                        print('模型训练失败!!!')
                else:
                    print('未生成训练数据!!!')
            else:
                print('数据未提取成功!!!')
            
        else:
            print('未设置CSV文件路径!!!')

        return lstm_model_dict


if __name__ == '__main__':
    model_fit = ModelFIT(Config(), 1, 2, 63,'test_12.csv')
    print(model_fit.run()) 