# -*- coding: utf-8 -*-
"""
Created on Tue May 16 11:28:09 2023

@author: 3rdEYE
"""
import paho.mqtt.client as mqtt
import threading
import cv2
import numpy as np
import math
import requests
import time 
from keras.models import Sequential,load_model,save_model
import random

class Mqtt_Publisher:
    '''
        mqtt消息通讯接口
    '''
    def __init__(self,central_ip='120.55.75.212',port=1883,node_name='bci_',anonymous=True,timeout=60):
        '''
        :param central_ip: Broker的地址
        :param port:  端口号
        :param timeout:  连接延时
        :param node_name: 节点名称
        :param anonymous: 是否同时允许多个节点
        '''
        self.broker_ip=central_ip
        self.broker_port=port
        self.timeout=timeout
        self.connected=False
        self.node_name=node_name
        if anonymous:
            self.node_name=self.node_name+str(random.randint(100000,999999))
        self.Start()
    def Start(self):
        '''
        开启publisher
        :return:
        '''
        self.client = mqtt.Client(self.node_name)     #创建客户端
        self.client.on_connect = self.on_connect  # 指定回调函数
        self.client.connect(self.broker_ip, self.broker_port, self.timeout)     #开始连接
        self.client.loop_start()    #开启一个独立的循环通讯线程。
    def Publish(self,topic,payload,qos=0,retain=False):
        '''
            发送一个mqtt消息
            :param topic: 消息名称，string类型
            :param payload: 消息内容，string类型
            :param qos: 消息等级
            :retain: 状态机消息
            :return:
        '''
        if self.connected:
            return self.client.publish(topic,payload=payload,qos=qos,retain=retain)
        else:
            raise Exception("mqtt server not connected! you may use .Start() function to connect to server firstly.")

    '''
                回调函数
    '''
    def on_connect(self,client, userdata, flags, rc):
        '''
            连接到broker的回调函数
        '''
        if rc==0:
            self.connected=True

        else:
            raise Exception("Failed to connect mqtt server.")




file = "param.txt"



cap = cv2.VideoCapture("http://192.168.43.29:81/stream")

last_time = time.time()

while cap.isOpened():

    ret, frame = cap.read()

    # 在计时器的间隔时间内跳过读取画面的步骤
    if time.time() - last_time < 2:
        continue
    else:
        last_time = time.time()

    # Recolor image to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    image = cv2.resize(image,(32,32))
 
    # cv2.imwrite("./corn_image/{}.jpg".format(random.randint(1,100)),image)
    
    image = image[None,:]/255

    
    model = load_model("./model.hdf5")
    # 预测
    p = np.argmax(model.predict(image))
    if p == 0:
        str_content = '0'
    if p == 1:
        str_content = '1'
    if p == 2:
        str_content = '2'
    if p == 3:
        str_content = '3'
    
    
    # 打开文件
    with open(file, "w", encoding='utf-8') as f:
        # write()：将内容写入文件，默认不换行
        text = "{}".format(str_content)
        f.write(text)
    
    
    print(model.predict(image))
    print("result:",p)
    

    
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
    


cap.release()
cv2.destroyAllWindows()