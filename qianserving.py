# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np 
from flask import Flask, jsonify, request
import pickle
import statsmodels
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from matplotlib import pyplot as plt
import statsmodels.api as sm 
from statsmodels.formula.api import ols 
import wget
import json
import requests
import subprocess
from enum import Enum
import redis 
import happybase
from concurrent.futures import ThreadPoolExecutor
import traceback
from qianconfig import Config,Qushi,MyLogging
import math
import time
import itertools
from sklearn.mixture import GaussianMixture as GMM 
#from sklearn.externals import joblib
import joblib
from wsgiref.simple_server import make_server
from cluster_function import *
from database import *
import numpy as np
import warnings
import datetime

from Cluster_Module import ClusterModule
from Cluster_Module_correlation import ClusterModulelr
from Model_fit_Module import ModelFIT
from Data_classify import DataClassify
from Predict_Module_gaojia_diagnose  import  Predict
from Gaojia_Fault_Diagnosis_web import start_diagnosis


from Cluster_Module_file import ClusterModulefile
from Data_classify_file import DataClassifyfile
from Cluster_Module_correlation_file import ClusterModulelrfile
from Model_fit_Module_file import ModelFITfile
from Predict_Module_gaojia_diagnose_hbase  import  Predicthbase

from Gaojia_Fault_Diagnosis_hbase_web import start_diagnosis_history

executor = ThreadPoolExecutor(16)

pathcwd = os.path.dirname(__file__)
app = Flask(__name__)

#logpath = 'log/serving.qian.std.out'
#logging.basicConfig(filename=logpath,filemode='a',format='%(asctime)s %(name)s:%(levelname)s:%(message)s',datefmt="%d-%m-%Y \
    #%H:%M:%S",level=logging.DEBUG)


header = {'Content-Type': 'application/json','Accept': 'application/json'} 

local_path_data =''
cancel_diagnosis = {}
cancel_predict = {}


myLogger = MyLogging()

@app.route('/train_db', methods=['POST'])
def train_db():
    try:
        
        request_json = request.get_json()
        
        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        kks = request_json["kks"]
        interval = request_json["interval"]
        start_row = request_json["start_row"]
        end_row =  request_json["end_row"]
        
        train_future = executor.submit(train_db_task,model_id,versionid,system_id,kks,interval,start_row,end_row)
        
        myLogger.write_logger("******trainingdb 模型DB开始训练modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型DB开始训练',
                "address":"train_db"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******trainingdb modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练DB预处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_db"

        }
        requests.post(Config.java_host_train_db, \
                    data = json.dumps(message),\
                    headers= header)



def train_db_task(model_id,versionid,system_id,kks,interval,start_row,end_row):
    
    try:
        
        cluster = ClusterModule(Config,system_id,kks,interval,start_row,end_row,'limit_list')
        cluster.run()
        
        message = {
            'status': True,
            'message': "python训练DB完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"train_db"
        }
        myLogger.write_logger("******train_task db finished modelid {} ".format(model_id))

        requests.post(Config.java_host_train_db, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******training db modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练DB异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_db"

        }
        requests.post(Config.java_host_train_db, \
                    data = json.dumps(message),\
                    headers= header)

@app.route('/train_lrdb', methods=['POST'])
def train_lrdb():

    try:
        
        request_json = request.get_json()
        

        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        kks = request_json["kks"]
        interval = request_json["interval"]
        #start_row = '2021-10-18 16:11:25'
        #end_row = '2021-10-24 10:05:20'
        start_row = request_json["start_row"]
        end_row =  request_json["end_row"]


        path_model = './model/trainlrdb/' + str(model_id)+'/'+ str(versionid)+'/'
        if not os.path.exists(path_model):    os.makedirs( path_model )  
        local_path_model = os.path.join(pathcwd,'model/trainlrdb/' + str(model_id)+'/'+ str(versionid)+'/') 

        filepath = local_path_model+'model.pkl'
        # with open(filepath, 'wb') as f:
        #     joblib.dump(gmm,f)


        
        train_future = executor.submit(train_lrdb_task,model_id,versionid,system_id,kks,interval,start_row,end_row)
        
        myLogger.write_logger("******training lrdb modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型LRDB开始训练',
                "address":"train_lrdb"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******training lrdb modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练LRDB预处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lrdb"

        }
        requests.post(Config.java_host_train_lrdb, \
                    data = json.dumps(message),\
                    headers= header)



def train_lrdb_task(model_id,versionid,system_id,kks,interval,start_row,end_row):
    
    try:

        cluster = ClusterModulelr(Config,system_id,kks,interval,start_row,end_row,'limit_list')
        cluster.run()
        
        message = {
            'status': True,
            'message': "python训练LRDB完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"train_lrdb"
        }
        myLogger.write_logger("******train task_lrdb finished modelid {} ".format(model_id))

        requests.post(Config.java_host_train_lrdb, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******trainingEM modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练LRDB处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lrdb"

        }
        requests.post(Config.java_host_train_lrdb, \
                    data = json.dumps(message),\
                    headers= header)




@app.route('/train_lstm_kks', methods=['POST'])
def train_lstm_kks():

    try:
        
        request_json = request.get_json()
        
        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        kks = request_json["kks"]
        interval = request_json["interval"]
        #start_row = '2021-10-18 16:11:25'
        #end_row = '2021-10-24 10:05:20'
        start_row = request_json["start_row"]
        end_row =  request_json["end_row"]

        
        train_future = executor.submit(train_lstm_kks_task,model_id,versionid,system_id,kks,interval,start_row,end_row)
        
        myLogger.write_logger("******training lstm_kks modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型lstm_kks开始区分',
                "address":"train_lstm_kks"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******training lstm_kks modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练lstm_kks处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lstm_kks"

        }
        requests.post(Config.java_host_train_lstm_kks, \
                    data = json.dumps(message),\
                    headers= header)



def train_lstm_kks_task(model_id,versionid,system_id,kks,interval,start_row,end_row):
    
    try:

        cluster = DataClassify(Config,model_id,versionid,system_id,kks,interval,start_row,end_row)
        cluster.run()
        
        message = {
            'status': True,
            'message': "python训练lstm_kks完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"train_lstm_kks"
        }
        myLogger.write_logger("******train_task lstm_kks finished modelid {} ".format(model_id))

        requests.post(Config.java_host_train_lstm_kks, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******training lstm_kks modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练lstm_kks异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lstm_kks"

        }
        requests.post(Config.java_host_train_lstm_kks, \
                    data = json.dumps(message),\
                    headers= header)




@app.route('/train_lstm', methods=['POST'])
def train_lstm():
    try:
        request_json = request.get_json()

        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        #kks = request_json["kks"]
        #start_row = '2021-10-18 16:11:25'
        #end_row = '2021-10-19 10:05:20'
        interval = request_json["interval"]
        start_row = request_json["start_row"]
        end_row =  request_json["end_row"]
        #linux
        conn = redis.StrictRedis(host='127.0.0.1',port=6379,db=2,password=123456,charset='utf-8',decode_responses=True)
 
        keys_redis = "lstmkks_"+ str(system_id)+"_"+str(model_id) +"_"+ str(versionid) 
        gv = conn.get(keys_redis)
        getv = json.loads(gv)

        kks =getv["lstm"]
        var_parameters = getv["var"]

        train_future = executor.submit(train_lstm_task,model_id,versionid,system_id,kks,start_row,end_row)
        
        myLogger.write_logger("******training lstm modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型LSTM开始训练',
                "address":"train_lstm"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******training lstm modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练LSTM预处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lstm"

        }
        requests.post(Config.java_host_train_lstm, \
                    data = json.dumps(message),\
                    headers= header)



def train_lstm_task(model_id,versionid,system_id,kks,start_row,end_row):
    
    try:

        lstm = ModelFIT(Config,system_id,kks,start_row,end_row)
        lstm.run()
        
        message = {
            'status': True,
            'message': "python训练LSTM完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"train_lstm"
        }
        myLogger.write_logger("******train_task lstm finished modelid {} ".format(model_id))

        requests.post(Config.java_host_train_lstm, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******training lstm modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练Dlstm异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lstm"

        }
        requests.post(Config.java_host_train_lstm, \
                    data = json.dumps(message),\
                    headers= header)






@app.route('/train_db_file', methods=['POST'])
def train_db_file():
    try:
        
        request_json = request.get_json()

        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        kks = request_json["kks"]
        interval = request_json["interval"]

        dataUrl =  request_json["dataUrl"]

        path_model = './model/traindbfile/' + str(model_id)+'/'+ str(versionid)+'/'
        if not os.path.exists(path_model):    os.makedirs( path_model )  
        local_path_model = os.path.join(pathcwd,'model/traindb_file/' + str(model_id)+'/'+ str(versionid)+'/') 

        filepath = local_path_model+'model.pkl'
        # with open(filepath, 'wb') as f:
        #     joblib.dump(gmm,f)

        path_data = os.path.join(pathcwd,'dataset/train_db/' + str(model_id)+'/')
        if not os.path.exists(path_data): os.makedirs( path_data )
        
        #linux
        #exitfiles = os.popen("ls {} | wc -l".format(path_data)).read() 
        #if eval(exitfiles) !=0:os.system("rm {}".format(path_data + "*"))
            
        filename = dataUrl[dataUrl.rindex('/') +1:-4]     
        
        local_path = path_data+filename +'.csv'
        filename_ = wget.download(dataUrl, out=local_path)
        
        #linux
        global local_path_data
        local_path_data = os.path.join(pathcwd,'dataset/train_db/' + str(model_id)+'/'+filename + '.csv')
        #win
        #local_path_data = os.path.join(pathcwd,'dataset\\train_db\\' + str(model_id)+'\\'+filename + '.csv')


        #data = pd.read_csv(local_path_data)
        
        train_future = executor.submit(train_db_file_task,local_path_data,model_id,versionid,system_id,kks,interval)
        
        myLogger.write_logger("******trainingdb_file 模型DB开始训练modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型DB_file开始训练',
                "address":"train_db_file"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******trainingdb_file modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练DB_file预处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_db_file"

        }
        requests.post(Config.java_host_train_db_file, \
                    data = json.dumps(message),\
                    headers= header)



def train_db_file_task(local_path_data,model_id,versionid,system_id,kks,interval):
    
    try:
        
        
        cluster = ClusterModulefile(Config,system_id,kks,interval,'limit_list',local_path_data)
        cluster.run()
        
        message = {
            'status': True,
            'message': "python训练DB_file完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"train_db"
        }
        myLogger.write_logger("******train_file_task db finished modelid {} ".format(model_id))

        requests.post(Config.java_host_train_db_file, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******training db_file modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练DB_file异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_db_file"

        }
        requests.post(Config.java_host_train_db_file, \
                    data = json.dumps(message),\
                    headers= header)

@app.route('/train_lrdb_file', methods=['POST'])
def train_lrdb_file():

    try:
        
        request_json = request.get_json()

        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        kks = request_json["kks"]
        interval = request_json["interval"]
        dataUrl =  request_json["dataUrl"]


        path_model = './model/trainlrdb_file/' + str(model_id)+'/'+ str(versionid)+'/'
        if not os.path.exists(path_model):    os.makedirs( path_model )  
        local_path_model = os.path.join(pathcwd,'model/trainlrdb_file/' + str(model_id)+'/'+ str(versionid)+'/') 

        filepath = local_path_model+'model.pkl'
        # with open(filepath, 'wb') as f:
        #     joblib.dump(gmm,f)

        global local_path_data
        train_future = executor.submit(train_lrdb_file_task,local_path_data,model_id,versionid,system_id,kks,interval)
        
        myLogger.write_logger("******training lrdb_file modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型LRDB开始训练',
                "address":"train_lrdb_file"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******training lrdb_file modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练LRDB_file预处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lrdb_file"

        }
        requests.post(Config.java_host_train_lrdb_file, \
                    data = json.dumps(message),\
                    headers= header)



def train_lrdb_file_task(local_path_data,model_id,versionid,system_id,kks,interval):
    
    try:

        cluster = ClusterModulelrfile(Config,system_id,kks,interval,'limit_list',local_path_data)
        cluster.run()
        
        message = {
            'status': True,
            'message': "python训练LRDB完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"train_lrdb_file"
        }
        myLogger.write_logger("******train task_lrdb finished modelid {} ".format(model_id))

        requests.post(Config.java_host_train_lrdb_file, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******traininglrdb_file modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练LRDB处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lrdb_file"

        }
        requests.post(Config.java_host_train_lrdb_file, \
                    data = json.dumps(message),\
                    headers= header)




@app.route('/train_lstm_kks_file', methods=['POST'])
def train_lstm_kks_file():

    try:
        
        request_json = request.get_json()
        
        #模型id 和系统id区别，设备id  
        #设备的模型，
        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        kks = request_json["kks"]
        interval = request_json["interval"]
        dataUrl =  request_json["dataUrl"]


        global local_path_data
        train_future = executor.submit(train_lstm_kks_file_task,model_id,versionid,system_id,kks,interval,local_path_data)
        
        myLogger.write_logger("******training lstm_kks_file modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型lstm_kks_file开始区分',
                "address":"train_lstm_kks_file"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******training lstm_kks_file modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练lstm_kks_file处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lstm_kks_file"

        }
        requests.post(Config.java_host_train_lstm_kks_file, \
                    data = json.dumps(message),\
                    headers= header)



def train_lstm_kks_file_task(model_id,versionid,system_id,kks,interval,local_path_data):
    
    try:

        cluster = DataClassifyfile(Config,model_id,versionid,system_id,kks,interval,local_path_data)
        cluster.run()
        
        message = {
            'status': True,
            'message': "python训练lstm_kks_file完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"train_lstm_kks_file"
        }
        myLogger.write_logger("******train_task lstm_kks_file finished modelid {} ".format(model_id))

        requests.post(Config.java_host_train_lstm_kks_file, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******training lstm_kks_file modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练lstm_kks_file异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lstm_kks_file"

        }
        requests.post(Config.java_host_train_lstm_kks_file, \
                    data = json.dumps(message),\
                    headers= header)




@app.route('/train_lstm_file', methods=['POST'])
def train_lstm_file():
    try:
        request_json = request.get_json()

        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        #kks = request_json["kks"]

        interval = request_json["interval"]
        dataUrl =  request_json["dataUrl"]

        #linux
        conn = redis.StrictRedis(host='127.0.0.1',port=6379,db=2,password=123456,charset='utf-8',decode_responses=True)
        #win
        #conn = redis.StrictRedis(host='127.0.0.1',port=6379,db=1,charset='utf-8',decode_responses=True)
        
        keys_redis = "lstmkks_"+ str(system_id)+"_"+str(model_id) +"_"+ str(versionid) 
        gv = conn.get(keys_redis)
        getv = json.loads(gv)

        kks =getv["lstm"]
        var_parameters = getv["var"]

        global local_path_data
        train_future = executor.submit(train_lstm_task_file,local_path_data,model_id,versionid,system_id,kks)
        
        myLogger.write_logger("******training lstm_file modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型LSTM开始训练',
                "address":"train_lstm_file"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******training lstm_file modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练LSTM_file预处理异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lstm_file"

        }
        requests.post(Config.java_host_train_lstm_file, \
                    data = json.dumps(message),\
                    headers= header)



def train_lstm_task_file(local_path_data,model_id,versionid,system_id,kks):
    
    try:

        lstm = ModelFITfile(Config,system_id,kks,local_path_data)
        lstm.run()
        
        message = {
            'status': True,
            'message': "python训练LSTM_file完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"train_lstm_file"
        }
        myLogger.write_logger("******train_task lstm_file finished modelid {} ".format(model_id))

        requests.post(Config.java_host_train_lstm_file, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******training lstm_file modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python训练Dlstm_file异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"train_lstm_file"

        }
        requests.post(Config.java_host_train_lstm_file, \
                    data = json.dumps(message),\
                    headers= header)





@app.route('/predict', methods=['POST'])
def predict_lstm_var():
    try:
        request_json = request.get_json()
        

        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        kks = request_json["kks"]
        kks_all = request_json["kks_all"]
        
        kks_special = request_json["kks_special"]


        #start_row = request_json["start_row"]
        #end_row =  request_json["end_row"]

        start_row = (datetime.datetime.now()-datetime.timedelta(minutes=35)).strftime(f'%Y-%m-%d %H:%M:%S')
        end_row = (datetime.datetime.now()).strftime(f'%Y-%m-%d %H:%M:%S')
        
        conn = redis.StrictRedis(host='127.0.0.1',port=6379,db=2,password=123456,charset='utf-8',decode_responses=True)
    
        keys_redis = "lstmkks_"+ str(system_id)+"_"+str(model_id) +"_"+ str(versionid) 
        gv = conn.get(keys_redis)
        getv = json.loads(gv)

        lstm_kks =getv["lstm"]
        var_kks = getv["var"]
        
        global cancel_predict
        cancel_predict[str(system_id)] =False

        train_future = executor.submit(predict_lstm_var_task,kks_special,device_name,model_id,versionid,system_id,kks_all,kks,var_kks,start_row,end_row)
        
        myLogger.write_logger("******predict lstm var modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型LSTMvar开始预测',
                "address":"predict"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******predict lstm var modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python预测LSTMvar预测异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"predict"

        }
        requests.post(Config.java_host_predict_lstm_var, \
                    data = json.dumps(message),\
                    headers= header)



def predict_lstm_var_task(kks_special,device_name,model_id,versionid,system_id,kks_all,kks,var_kks,start_row,end_row):
    
    try:
        #周期调度：预警模型点击发布，即进入预警模型的周期调度，会一直预警下去，每5s，时间戳会依次推加更新，当点击取消，即取消预警。
        global cancel_predict
        while(not cancel_predict[str(system_id)] ):
            
            lstmvar = Predict(Config,kks_special,device_name,system_id,kks_all,kks,var_kks,start_row,end_row)
            lstmvar.run()
            
            start_row = (datetime.datetime.now()-datetime.timedelta(minutes=35)).strftime(f'%Y-%m-%d %H:%M:%S')
            end_row = (datetime.datetime.now()).strftime(f'%Y-%m-%d %H:%M:%S')
            time.sleep(5)
        
        message = {
            'status': True,
            'message': "python预测LSTMvar完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"predict"
        }
        myLogger.write_logger("******predict—_task lstm var finished modelid {} ".format(model_id))

        requests.post(Config.java_host_predict_lstm_var, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******predict—_task lstm modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python预测Dlstmvar异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"predict"

        }
        requests.post(Config.java_host_predict_lstm_var, \
                    data = json.dumps(message),\
                    headers= header)


@app.route('/predict_cancel', methods=['POST'])
def predict_cancel():
    try:
        request_json = request.get_json()
        
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]

        global cancel_predict
        cancel_predict["device_id"] =True

        myLogger.write_logger("******predict_cancel system_id {}".format(system_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型predict_cancel完成',
                "system_id": system_id,
                "address":"predict_cancel"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******predict_cancel modelid {},excep:{}".format(system_id,e))
        message = {
        'status': False,
        'message': "python诊断predict_cancel异常",
        "system_id": system_id,
        "address":"predict_cancel"

        }
        requests.post(Config.java_host_predict_lstm_var, \
                    data = json.dumps(message),\
                    headers= header)




@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        request_json = request.get_json()
        
        
        model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        versionid = request_json["model_version"]
        #db聚类
        kks = request_json["kks"]
        #lrdb聚类
        kks_fuhe = request_json["kks_fuhe"]
        #预测，加载已有模型
        kks_all = request_json["kks_all"]
        start_row = request_json["start_row"]
        end_row =  request_json["end_row"]
        interval = request_json["interval"]

        
        conn = redis.StrictRedis(host='127.0.0.1',port=6379,db=2,password=123456,charset='utf-8',decode_responses=True)

        keys_redis = "lstmkks_"+ str(system_id)+"_"+str(model_id) +"_"+ str(versionid) 
        gv = conn.get(keys_redis)
        getv = json.loads(gv)

        lstm_kks =getv["lstm"]
        var_kks = getv["var"]

        train_future = executor.submit(evaluate_task,device_name,model_id,versionid,system_id,kks_all,kks_fuhe,kks,var_kks,start_row,end_row,interval)
        
        myLogger.write_logger("******yujing evaluate modelid {}".format(model_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型预警开始评估',
                "address":"evaluate"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******yujing evaluate modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python模型预警评估异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"evaluate"

        }
        requests.post(Config.java_host_evaluate, \
                    data = json.dumps(message),\
                    headers= header)



def evaluate_task(device_name,model_id,versionid,system_id,kks_all,kks_fuhe,kks,var_kks,start_row,end_row,interval):
    
    try:

        cluster1 = ClusterModule(Config,system_id,kks,interval,start_row,end_row,'limit_list_evaluate')
        cluster1.run()
        
        myLogger.write_logger("******yujing evaluate  ClusterModule finished modelid {} ".format(model_id))

        cluster = ClusterModulelr(Config,system_id,kks_fuhe,interval,start_row,end_row,'limit_list_evaluate')
        cluster.run()
        
        myLogger.write_logger("******yujing evaluate  ClusterModulelr finished modelid {} ".format(model_id))

        lstmvar = Predicthbase(Config,device_name,system_id,kks_all,kks,var_kks,start_row,end_row,interval)
        lstmvar.run()

        message = {
            'status': True,
            'message': "python模型预警评估完成",
            "modelId": model_id,
            "modelVersion":versionid,
            "address":"evaluate"
        }
        myLogger.write_logger("******yujing evaluate Predicthbase finished modelid {} ".format(model_id))

        requests.post(Config.java_host_evaluate, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******yujing evaluate modelid {},excep:{}".format(model_id,e))
        message = {
        'status': False,
        'message': "python预警评估异常",
        "modelId": model_id,
        "modelVersion":versionid,
        "address":"evaluate"

        }
        requests.post(Config.java_host_evaluate, \
                    data = json.dumps(message),\
                    headers= header)



@app.route('/diagnosis', methods=['POST'])
def diagnosis():
    try:
        request_json = request.get_json()
        

        #model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        #versionid = request_json["model_version"]
        kks = request_json["kks"]
        
        
        #start_row = '2021-10-18 16:11:25'
        #end_row = '2021-10-18 19:05:20'
        global cancel_diagnosis
        cancel_diagnosis[str(system_id)] =False

        warn_id = request_json["warn_id"]
        diagnose_id = request_json["diagnose_id"]
        kind_id  = request_json["kind_id"]

        fault_id = request_json["fault_id"]

        if kind_id==1:
            train_future = executor.submit(diagnosis_task_kind1,device_name,system_id,kks,warn_id,diagnose_id,kind_id,fault_id)
        else:
            train_future = executor.submit(diagnosis_task,device_name,system_id,kks,warn_id,diagnose_id,kind_id,fault_id)
        
        myLogger.write_logger("******diagnosis system_id {}".format(system_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型diagnosis开始诊断',
                "system_id": system_id,
                "address":"diagnosis",
                "fault_id":fault_id
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******diagnosis modelid {},excep:{}".format(system_id,e))
        message = {
        'status': False,
        'message': "python诊断diagnosis诊断异常",
        "system_id": system_id,
        "address":"diagnosis",
        "fault_id":fault_id

        }
        requests.post(Config.java_host_diagnosis, \
                    data = json.dumps(message),\
                    headers= header)



def diagnosis_task(device_name,system_id,kks_special,warn_id,diagnose_id,kind_id,fault_id):
    
    try:
        #周期调度：只要点击发布，会一直诊断下去，每5s，当点击取消发布，即关闭周期调度。
        global cancel_diagnosis
        while(not cancel_diagnosis[str(system_id)] ):
        
            start_diagnosis(Config,device_name,system_id,kks_special,warn_id,diagnose_id,kind_id)
            time.sleep(5)

        message = {
            'status': True,
            'message': "python诊断diagnosis完成",
            "system_id": system_id,
            "address":"diagnosis",
            "fault_id":fault_id
        }
        myLogger.write_logger("******diagnosis finished system_id {} ".format(system_id))

        requests.post(Config.java_host_diagnosis, \
                        data = json.dumps(message),\
                        headers= header)
            

    except Exception as e:
        myLogger.write_logger("******diagnosis system_id {},excep:{}".format(system_id,e))
        message = {
        'status': False,
        'message': "python诊断diagnosis异常,请检查fault_list,systom_list,limit_list是否正确存表",
        "system_id": system_id,
        "address":"diagnosis",
        "fault_id":fault_id

        }
        requests.post(Config.java_host_diagnosis, \
                    data = json.dumps(message),\
                    headers= header)

def diagnosis_task_kind1(device_name,system_id,kks_special,warn_id,diagnose_id,kind_id,fault_id):
    #事件调度：若设备异常报警，则触发诊断接口，即在预警代码里调用诊断接口，10分钟，每5s诊断一次。
    try:
        i=0
        while(i<120):
        
            start_diagnosis(Config,device_name,system_id,kks_special,warn_id,diagnose_id,kind_id)
            time.sleep(5) 
            i=+1 

        message = {
            'status': True,
            'message': "python诊断diagnosis完成",
            "system_id": system_id,
            "address":"diagnosis",
            "fault_id":fault_id
        }
        myLogger.write_logger("******diagnosis finished system_id {} ".format(system_id))

        requests.post(Config.java_host_diagnosis, \
                        data = json.dumps(message),\
                        headers= header)
            

    except Exception as e:
        myLogger.write_logger("******diagnosis system_id {},excep:{}".format(system_id,e))
        message = {
        'status': False,
        'message': "python诊断diagnosis异常,请检查fault_list,systom_list,limit_list是否正确存表",
        "system_id": system_id,
        "address":"diagnosis",
        "fault_id":fault_id

        }
        requests.post(Config.java_host_diagnosis, \
                    data = json.dumps(message),\
                    headers= header)




@app.route('/diagnosis_cancel', methods=['POST'])
def diagnosis_cancel():
    try:
        request_json = request.get_json()
        
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]

        global cancel_diagnosis
        cancel_diagnosis[str(system_id)] =True

        myLogger.write_logger("******diagnosis_cancel system_id {}".format(system_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型diagnosis_cancel完成',
                "system_id": system_id,
                "address":"diagnosis_cancel"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******diagnosis_cancel modelid {},excep:{}".format(system_id,e))
        message = {
        'status': False,
        'message': "python诊断diagnosis_cancel异常",
        "system_id": system_id,
        "address":"diagnosis_cancel"

        }
        requests.post(Config.java_host_diagnosis, \
                    data = json.dumps(message),\
                    headers= header)




@app.route('/diagnosis_result_diagnosis', methods=['POST'])
def diagnosis_result_diag():
    try:
        request_json = request.get_json()
        

        #model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        #versionid = request_json["model_version"]
        kks = request_json["kks"]
        
        warn_id = request_json["warn_id"]
        diagnose_id = request_json["diagnose_id"]
        kind_id  = request_json["kind_id"]
        
        #start_row = '2021-10-18 16:11:25'
        #end_row = '2021-10-18 19:05:20'
        #global cancel_diagnosis
        #cancel_diagnosis["device_id"] =False

        

        train_future = executor.submit(diagnosis_result_diag_task,device_name,system_id,kks,warn_id,diagnose_id,kind_id)
        
        myLogger.write_logger("******diagnosis_result_diagnosis system_id {}".format(system_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型diagnosis_result_diagnosis开始诊断',
                "system_id": system_id,
                "address":"diagnosis_result_diagnosis"
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******diagnosis modelid {},excep:{}".format(system_id,e))
        message = {
        'status': False,
        'message': "python诊断diagnosis_result_diagnosis诊断异常",
        "system_id": system_id,
        "address":"diagnosis_result_diagnosis"

        }
        requests.post(Config.java_host_diagnosis_result_diag, \
                    data = json.dumps(message),\
                    headers= header)



def diagnosis_result_diag_task(device_name,system_id,kks_special,warn_id,diagnose_id,kind_id):
    

        
    try:
        #事件调度：即页面按钮诊断调度，10分钟，每5s
        i=0
        while(i<120):
        
            start_diagnosis(Config,device_name,system_id,kks_special,warn_id,diagnose_id,kind_id)
            time.sleep(5) 
            i=+1 

        message = {
            'status': True,
            'message': "python诊断diagnosis_result_diagnosis完成",
            "system_id": system_id,
            "address":"diagnosis_result_diagnosis"
        }
        myLogger.write_logger("******diagnosis finished system_id {} ".format(system_id))

        requests.post(Config.java_host_diagnosis_result_diag, \
                        data = json.dumps(message),\
                        headers= header)
           

    except Exception as e:
        myLogger.write_logger("******diagnosis_result_diagnosis system_id {},excep:{}".format(system_id,e))
        message = {
        'status': False,
        'message': "python诊断diagnosis_result_diagnosis异常,请检查fault_list,systom_list,limit_list是否正确存表",
        "system_id": system_id,
        "address":"diagnosis_result_diagnosis"

        }
        requests.post(Config.java_host_diagnosis_result_diag, \
                    data = json.dumps(message),\
                    headers= header)




@app.route('/diagnosis_history', methods=['POST'])
def diagnosis_history():
    try:
        request_json = request.get_json()
        

        #model_id = request_json["model_id"]
        device_name = request_json["device_name"]
        system_id = request_json["device_id"]
        #versionid = request_json["model_version"]
        kks = request_json["kks"]
        start_row = request_json["start_row"]
        end_row =  request_json["end_row"]
        interval = request_json["interval"]
        #start_row = '2021-10-18 16:11:25'
        #end_row = '2021-10-18 19:05:20'
        
        fault_id = request_json["fault_id"]

        train_future = executor.submit(diagnosis_history_task,device_name,system_id,kks,start_row,end_row,fault_id)
        
        myLogger.write_logger("******diagnosis_history system_id {}".format(system_id))
        
        resp = jsonify({
                'status': True,
                'message': '-->模型diagnosis_history开始诊断',
                "system_id": system_id,
                "address":"diagnosis_history",
                "fault_id":fault_id
        })
        resp.status_code = 200
        return resp


    except Exception as e:
        myLogger.write_logger("******diagnosis_history modelid {},excep:{}".format(system_id,e))
        message = {
        'status': False,
        'message': "python诊断diagnosis_history诊断异常",
        "system_id": system_id,
        "address":"diagnosis_history",
        "fault_id":fault_id

        }
        requests.post(Config.java_host_diagnosis_history, \
                    data = json.dumps(message),\
                    headers= header)



def diagnosis_history_task(device_name,system_id,kks_special,start_row,end_row,fault_id):
    
    try:

        
        start_diagnosis_history(Config,device_name,system_id,kks_special,start_row,end_row)

        message = {
            'status': True,
            'message': "python诊断diagnosis完成",
            "system_id": system_id,
            "address":"diagnosis_history",
            "fault_id":fault_id
        }
        myLogger.write_logger("******diagnosis_history finished system_id {} ".format(system_id))

        requests.post(Config.java_host_diagnosis_history, \
                        data = json.dumps(message),\
                        headers= header)

    except Exception as e:
        myLogger.write_logger("******diagnosis_history system_id {},excep:{}".format(system_id,e))
        message = {
        'status': False,
        'message': "python诊断diagnosis_history异常,请检查fault_list,systom_list,limit_list是否正确存表",
        "system_id": system_id,
        "address":"diagnosis_history",
        "fault_id":fault_id

        }
        requests.post(Config.java_host_diagnosis_history, \
                    data = json.dumps(message),\
                    headers= header)





if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8484)#, debug=True)
    #server = make_server("127.0.0.1",app)
    #server.serve_forever()
