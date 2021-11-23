step1 


启动：/etc/init.d/cron start ( service cron start )
重启：/etc/init.d/cron restart ( service cron restart )
关闭：/etc/init.d/cron stop ( service cron stop )


*/1 * * * *   nohup python3 -u /home/jp/jianpanqian/test_crontab.py  >>  /home/zkl/Desktop/jianpanjianpan/online.log 2>&1 &

*/1 * * * *  /bin/bash /home/zkl/Desktop/jianpanjianpan/test_cron.sh  >>  /home/zkl/Desktop/jianpanjianpan/online2.log 2>&1 &



*/1 * * * *   nohup python3 -u /home/zkl/Desktop/jianpanjianpan/test_crontab.py  >>  /home/zkl/Desktop/jianpanjianpan/online.log 2>&1 &
*/1 * * * *  /bin/bash /home/zkl/Desktop/jianpanjianpan/test_cron.sh


#测试 1min
*/1 * * * *  /bin/bash /home/jp/jianpanqian/start_train.sh





#聚类 3个月  2021-10-28 23:00:00  2022-01-28 23:00:00
0 22 28 */3 *  /bin/bash /home/jp/jianpanqian/start_cluster.sh
0 1 28 */3 *  /bin/bash /home/jp/jianpanqian/start_cluster_mill.sh


#训练 3天   2021-10-22 01:01:00  2021-10-25 01:01:00
1 1 */3 * *  /bin/bash /home/jp/jianpanqian/start_train.sh
1 3 */3 * *  /bin/bash /home/jp/jianpanqian/start_train_mill.sh

#预警 5s
#0 23 28 */3 *  /bin/bash /home/jp/jianpanqian/start_predict.sh
*  * * * * /bin/bash /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 5;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 10;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 15;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 20;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 25;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 30;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 35;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 40;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 45;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 50;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 55;/bin/bash   /home/jp/jianpanqian/start_predict.sh
*  * * * * root sleep 59;/bin/bash   /home/jp/jianpanqian/start_predict.sh


#预警 5s
#0 23 28 */3 *  /bin/bash /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * /bin/bash /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 5;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 10;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 15;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 20;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 25;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 30;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 35;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 40;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 45;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 50;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 55;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh
*  * * * * root sleep 59;/bin/bash   /home/jp/jianpanqian/start_predict_mill.sh


#诊断 5s
#0 23 28 */3 *  /bin/bash /home/jp/jianpanqian/start_diagnose.sh













import os
os.system('./script.sh')




online mysql

mysql
172.17.224.171 
root 
Qwe123!!
yuhuan_moniotr_test_python
db :yuhuan_moniotr_test_python


redis:
database: 6
# host: 172.17.224.172
lettuce:
pool:
max-active: 8 #最大连接数据库连接数,设 0 为没有限制
max-idle: 8 #最大等待连接中的数量,设 0 为没有限制
max-wait: -1ms #最大建立连接等待时间。如果超过此时间将接到异常。设为-1表示无限制。
min-idle: 0 #最小等待连接中的数量,设 0 为没有限制
shutdown-timeout: 100ms
password: '123456'
port: 6379
#哨兵模式 redis 集群
sentinel:
#哨兵的 ip 和端口
nodes: 172.17.224.172:26379,172.17.224.171:26379,172.17.224.172:26380
master: mymaster



hase  

hbase:
ip: 172.17.224.171
#集群模式使用
master: master:9000

历史表  history_point

port  9000  2181




y: {'40LAB21CT001': 178.52615275778024, '40LAD61CP001': 1.653138946192305, '40LBQ61CP001': 1.6562522660359988, '40LBQ60CT002': 463.93915952006483, '40LBQ61CT001': 464.5151437236962, '40LCH61CG101XQ01': 60.20973205566406, '40LAD61CL001': -96.46820831298828, 'D04:HPHTR3AL': -45.836204528808594}




chmod a+x start_diagnose_dingshi_gaojia_63.sh


(tf12) jp@jp-PowerEdge-R740:~/jianpanqian$ ps -ef | grep bash
jp       40447 40446  0 14:54 pts/0    00:00:00 -bash
jp       40586 40585  0 14:55 pts/1    00:00:00 -bash
jp       40789 40788  0 14:56 pts/2    00:00:00 -bash
jp       43009 43008  0 15:52 pts/3    00:00:00 -bash
jp       43256 43255  0 16:14 pts/4    00:00:00 -bash
jp       45543     1  0 19:22 ?        00:00:00 /bin/bash /home/jp/jianpanqian/start_diagnose_dingshi_gaojia_63.sh
jp       50854 40789  0 19:28 pts/2    00:00:00 grep --color=auto bash
(tf12) jp@jp-PowerEdge-R740:~/jianpanqian$ 
(tf12) jp@jp-PowerEdge-R740:~/jianpanqian$ 
(tf12) jp@jp-PowerEdge-R740:~/jianpanqian$ kill -9 45543
(tf12) jp@jp-PowerEdge-R740:~/jianpanqian$ ps -ef | grep bash
jp       40447 40446  0 14:54 pts/0    00:00:00 -bash
jp       40586 40585  0 14:55 pts/1    00:00:00 -bash
jp       40789 40788  0 14:56 pts/2    00:00:00 -bash
jp       43009 43008  0 15:52 pts/3    00:00:00 -bash
jp       43256 43255  0 16:14 pts/4    00:00:00 -bash
jp       51130 40789  0 19:29 pts/2    00:00:00 grep --color=auto bash



训练轮次
训练很慢，

预测很慢，预测调度 改为20s  也不行，

每个代码的hbase时间戳 设定

每个代码的运行时间

每个代码的hbase 采样频率


训练的

预警
聚类训练 最近3个月的的数据
Lstm训练  半个月的数据，
Var训练 一周的数据
 
Lstm和var预测  一天的数据  预测下一秒



4号机组3A高压加热器
4号机组磨煤机E




url=http://c.biancheng.net
echo $url
name='C语言中文网'
echo $name
author="严长生"
echo $author


#!/bin/bash
echo "脚本$0"
echo "第一个参数$1"
echo "第二个参数$2"



$ ./test.sh 1 2
 
#shell中将会输出：
脚本./test.sh
第一个参数1
第二个参数2

for i in {0…100}; do python onepara_SVM.py $i; done


报警，生成id   表，写入报警id
传给故障，结果故障1   写入报警id，诊断id 

第二次报警，生成id，

定时调用


java调用，传诊断id，
传 报警id， count，



Use tf.where in 2.0, which has the same broadcast rule as np.where
2021-10-24 18:58:00.672379: F tensorflow/stream_executor/cuda/cuda_driver.cc:175] Check failed: err == cudaSuccess || err == cudaErrorInvalidValue Unexpected CUDA error: out of memory


就起5个脚本
start cluster.sh
start train.sh
start train mill.sh  和上个间隔1h  
start predict.sh  运行预警以及诊断，代码执行start_diagnose_dingshi_gaojia_63.sh
start predict_mill.sh 。。。。。   和上个间隔1h

彭康调用也是 这两个脚本
start_diagnose_dingshi_gaojia_63.sh  每5s循环执行 诊断代码，
start_diagnose_dingshi_mill_130.sh


一定要分开了，不然gpu不够，

crontab 里配置
聚类1   3个月10点

聚类2  3个月 12点

训练1   半个月  1点
训练2   半个月  2点


预测1   5s   若启动诊断，，，第二次5s  和第一次 重叠了，，目前是   不报警 不诊断   
预测2   

这个就不用配置到crontab了
诊断1
诊断2



python 起shell  要后台运行


聚类 存mysql  该设备下测点kks 均值 一二三级上下限   指令和反馈kks不参与聚类
预测值 存redis 存hbase  相关度高的var，其他lstm
预警 存redis  存mysql   设备报警需要均值， kks报警 需要 正常高限
诊断 存mysql  需要一三级报警区间，需要实时值





warn_id  自动调度 需要，java调用  值null

diagnosis_id 诊断结果id  java传入，存数据，回调返回该id，，自动调度，值null

这三个字段 若java诊断，全部接受，回写到表
若自己调度，设为空，

在诊断代码里 insert那里，


kind 手动诊断 固定为1
前三个字段 放入数据库 最后一个字段用于算法判断是自动诊断还是手动诊断

kind 自己调度 设为0  shell脚本里if判断，自己调度不回调java， 手动诊断  回调java


id顺序  传入参数顺序   str  int  int
os.system('warn_id  diagnoseid  kindid')

自动调度   warn_id 生成str，diagnoseid 传1  kindid 传1
java调度   warn_id 'know'  diagnoseid 传20位的数字，  kindid 传0


shell脚本：

if kind==1:
diagnosis_id  不插入  值null
warn_id 传入  报警代码生成的

不回调java

kind==0:
diagnosis_id  java传，写库，回调，
warn_id 不插入  值null

回调java 只传入diagnosis_id




if[ $weight -le $idealweight ] ; then
echo"You should eat a bit more fat."
else
echo"You should eat a bit more fruit."
fi

    mysql_host = '172.17.224.171'
    mysql_port = 3306
    mysql_user = 'root'
    mysql_password = 'Qwe123!!'
    mysql_db = 'yuhuan_moniotr_test_python'

    mysql_host = '172.17.231.59'
    mysql_port = 3306
    mysql_user = 'root'
    mysql_password = 'root'
    mysql_db = 'yuhuan_monitor_dev'




凝结水系统
给水泵系统


第一步

页面传参，所有kks  若有与负荷相关的，
聚类下
分测点
1 正常测点  直接聚类代码
2 相关的    线性拟合 聚类代码
3 开关量   0000 1 -1存表
4  指令反馈  0000  0.05  -0.05

村表时 delete 系统下kks，再insert  保证唯一

聚类 时间戳 往前一周
lstm训练 时间戳 往前一天
db训练完，启动lstm训练
db什么时候完呢，回调java ，java调动lstm训练



所有接口梳理

log日志


聚类和线性回归，所有测点的区间，


预警模型 
 训练 评估 都是针对聚类来说的
 训练 时间段  
 训练 文件夹  添加代码
 
 区间调优 彭康再加个表吧，这个表一栋，诊断也动

 发布 预测代码，lstm  var训练 预测

 只要有预警，入库，有异常，，java调用诊断接口，5s一次

故障模型
  评估  历史数据库 hbase
  推演  什么接口  什么能能能  hbase
  发布  redis 每5s

中间的表结构


把配置文件全部导出

任务清单：


1.聚类模型训练，设备测点分组  
1.1 正常测点  直接聚类代码 
从hbase指定时间段，现有代码 添加web服务代码    0.5
从文件读数据，新功能，需要代码开发，然后再添加web服务   1 

1.2 相关测点    线性拟合 聚类代码，添加web服务代码  0.5
1.3 开关量   0000 1 -1存表
1.4 指令反馈  0000  0.05  -0.05


采样频率，参数，

2.lstm训练   0.5天
聚类完成回调java后，java后台发起lstm训练，时间戳为 聚类时间戳的往前一天，


3 区间调优
复制表，limit_list ,然后添加字段，不要直接在原表改变


4 模型评估， 三对线 还有预测值，这个很重， 3天
从历史数据评估，
从文件评估，

除了limit_list  还需要，

模型评估的，指令反馈，都为0，但是有些还是有值的啊

预测值，的时间戳，


5.预警关闭功能   0.5天


5.故障
发布，调用故障web服务
限值 三级；设备故障上升趋势，三级上限
阈值 均值，
提前置信度 0.9

  5.1评估  历史数据库 hbase，新功能  1天
  新功能，需要从hbase读
  需要添加故障报警，关闭功能，

  5.2 推演  什么接口   hbas  1天
  往前添加一段时间，

  5.3发布  redis 每5s   0.5天

  5.4 关闭诊断功能   0.5天






调度函数  接口，传入参数 周期
现场部署情况 沟通，




        #模型id 和系统id区别，设备id  
        #设备的模型，


三个传文件接口     也是四个接口

db   全部行

lrdb   全部行

lstmkks   

 lstm  倒数10k




预测 三类预测 下一时间步的预测 
时间段内的预测
文件的预测

调度接口，这个是要改 crontab文件的，怎么java 写个定时程序吧，时间戳 都推移，3个月的话，


关闭报警接口

关闭诊断接口

之前的两个 复位 诊断 web服务


故障

从历史数据 训练
从文件，训练，db lrdb kks区分 lstm  四个

模型评估  只有从历史数据
接口1.1 1.2 1.3  1.4 再跑一边，存新表 limit_list_evalute
预测值，从hbase 批量预测，存hbase   history_predict_result_test 

评估就不是包括训练的呀，所以 1.1 1.2  然后 预测代码

复制一张表除了 

limit_list_evalute



部署，
1. redis '127.0.0.1'检索
2. 诊断 redis key  预测 redis key   

复制表 limit_list_evaluate


评估结果页面只有 预测 三界，没有设备故障诊断可以屏蔽， 也不用

文件写完了  要测
评估写完了，要测



现涛 诊断 hbase  要测

张俊 lrdb文件  


调度接口，这个是要改 crontab文件的，怎么java 写个定时程序吧，时间戳 都推移，3个月的话，


4个文件的，测试 
评估的 测试
诊断 hbase 的测试

自己搭建个minio

diagnosis_history  

在写两个取消接口
取消训练 接口扔给后端


预警发布，
while bool 取消发布

预测
sleep()

预警 取消发布，
bool true


诊断发布 
一直诊断
sleep()

诊断取消发布，


诊断历史 diagnosis_history  添加字段 endtime
limit_list  加个flag  人工修改后 为1  人工没修改的测点为0

复制表 limit_list_evaluate


预测 hbase
更改 读时间戳， 更改为最新的，
并且 while 循环


故障评估 加个fault_id字段

故障配置后 发布，while 诊断，id   


自动调度   warn_id 生成str，diagnoseid 传1  kindid 传1
java调度   warn_id 'know'  diagnoseid 传20位的数字，  kindid 传0


shell脚本：

if kind==1:
diagnosis_id  不插入  值null
warn_id 传入  报警代码生成的

不回调java

kind==0:
diagnosis_id  java传，写库，回调，
warn_id 不插入  值null

回调java 只传入diagnosis_id


报警关闭功能迁移到诊断 插入表那里了，

诊断 四个部分

设备规则库 知识库配置好后
诊断模型发布，Predict_Module_gaojia_diagnose  warn_id kind_id diagnoid_id
取消发布，

发布应该是最原始的，最开头的，
一直循环，一直诊断，  要避免一直插入，这个没解决？ 
取消发布，关闭循环，  但是已经一直插入了
所以这个地方避免两个地方，避免device_warn_history 一直插入
避免 diagonal_history 一直插入
定义第三个kind的，预警触发，手动触发，java触发，

之前没有手动触发，手动的改为预警触发了，

kind=2 warn_id null  diag_null
select count kind=2 sys=63  guzhangid= 
datatime =

endtime更新

预警代码里的触发诊断代码 改为自动调用，传参不变，
传参不变，就要添加字段了呀

发布代码再添三个字段


设备模型 评估和推演，从hbase
ok 这个已经解决了，原始时间是 datetime， 通过添加end_time ,
不借助 warnid kindid 等等。

诊断结果页面的 复位和诊断按钮
诊断按钮，
复位按钮，




之前的代码，不用改，还是脚本，传入参数，3个，，调用的ifmain下的，，
发布接口，调用ifmanin上的函数，



部署线上，
有些win下的代码  改成linux的下的代码
-redis 
-模型路径

表是不是都要复制一份
字段


评估，

预测 发布，

诊断发布

返回结果

hbase

scan 'history_poin',{LIMIT=>1,REVERSED=>true,FILTER=>"QualifierFilter(=,'binary:D04:SELMW') OR QualifierFilter(=,'binary:D04:SELMW')"}

scan 'history_warn_predict_test',{LIMIT => 10, STARTROW => '2021-10-29 00:00:00' ENDROW => '2021-10-30 00:00:00'}

重启 
supervisorctl stop all
supervisorctl start all

二、更新新的配置到supervisord    

supervisorctl update

nginx重启
jp@jp-PowerEdge-R740:/usr/local/nginx$ sudo ./sbin/nginx -s reload


jp@jp-PowerEdge-R740:~/jianpanqianqian$ netstat -ap | grep 8484
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
tcp        0      0 0.0.0.0:8484            0.0.0.0:*               LISTEN      -                   
tcp        0      0 jp-PowerEdge-R740:8484  172.17.231.66:63274     ESTABLISHED -                   
jp@jp-PowerEdge-R740:~/jianpanqianqian$ netstat -ap | grep 8383
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
tcp        0      0 0.0.0.0:8383            0.0.0.0:*               LISTEN      -                   
tcp        0      0 jp-PowerEdge-R740:8383  172.17.224.171:37450    ESTABLISHED -                   
tcp        0      0 jp-PowerEdge-R740:8383  172.17.224.171:37728    ESTABLISHED -                   
tcp        0      0 jp-PowerEdge-R740:8383  172.17.224.171:37726    ESTABLISHED -                   
tcp        0      0 jp-PowerEdge-R740:8383  172.17.224.171:37950    ESTABLISHED -        



加载模型失败，install hdf5==1.10.4
lstm_model_dict[i] = tf.keras.models.load_model(model_dir_dict[i])
一会报错 一会不报错，，哎
2021-11-15 15:34:35 qianconfig.py[line:179] INFO:  ******yujing evaluate modelid 1458749438045007874,excep:Cannot interpret feed_dict key as Tensor: Tensor Tensor("Placeholder:0", shape=(1, 384), dtype=float32) is not an element of this graph.


******training lstm modelid 1458749438045007874,excep:Fetch argument <tf.Variable 'gru/kernel:0' shape=(1, 384) dtype=float32> cannot be interpreted as a Tensor. (Tensor Tensor("gru/kernel/Read/ReadVariableOp:0", shape=(1, 384), dtype=float32) is not an element of this graph.)

全车膜，全包围脚垫，尾箱垫，行车记录仪，抱枕，挡泥板，方向套，后备箱垫，

这个是性能问题，
资源不够

******diagnosis_history system_id 1013,excep:list index out of range
表不统一 


train db报错
Found array with 0 sample(s) (shape=(0, 1)) while a minimum of 1 is required.


科技项目 
示范

海淡车间  巡检机器人
室外 下雪 防水 光编码  做低，做重，四个轮子， 全天候  激光扫描地图，
室内 为主



电汽柜
无线测温 测正
配电室

重庆松藻电厂  配电


转机的巡检  比较看重，一直在变，，振动 温度， 

云深知

英伟达得nx  深度相机
无人车底盘四轮两驱差速移动机器人ROS雷达导航英伟达xavier nx

三端同步，视频 语音 图片
六托一 
6哥机器人，

四个
检测结果模块，
报警模块 规则可配
报警处理模块
和其他系统联动


全检修 

整个场景得全覆盖，
