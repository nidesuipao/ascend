import socket
import cv2
import numpy
import time

class client:
    def __init__(self):
        self.address = ('192.168.8.213', 9999)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect(self.address)

    def disconnect(self):
        self.sock.close()

    def SendVideo(self,frame):
        # 压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 15]
        # cv2.imencode将图片格式转换(编码)成流数据，赋值到内存缓存中;主要用于图像数据格式的压缩，方便网络传输
        # '.jpg'表示将图片按照jpg格式编码。
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        # 建立矩阵
        data = numpy.array(imgencode)
        # 将numpy矩阵转换成字符形式，以便在网络中传输
        stringData = data.tostring()
        # 先发送要发送的数据的长度
        # ljust() 方法返回一个原字符串左对齐,并使用空格填充至指定长度的新字符串
        self.sock.send(str.encode(str(len(stringData)).ljust(16)))
        # 发送数据
        self.sock.send(stringData)
        # 读取服务器返回值
        receive = self.sock.recv(1024)
        #if len(receive):
            #print(str(receive, encoding='utf-8'))
