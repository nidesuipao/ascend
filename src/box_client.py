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
        # ѹ������������cv2.imencode�����õ�������jpeg��˵��15����ͼ��������Խ�ߴ���ͼ������Խ��Ϊ 0-100��Ĭ��95
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 15]
        # cv2.imencode��ͼƬ��ʽת��(����)�������ݣ���ֵ���ڴ滺����;��Ҫ����ͼ�����ݸ�ʽ��ѹ�����������紫��
        # '.jpg'��ʾ��ͼƬ����jpg��ʽ���롣
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        # ��������
        data = numpy.array(imgencode)
        # ��numpy����ת�����ַ���ʽ���Ա��������д���
        stringData = data.tostring()
        # �ȷ���Ҫ���͵����ݵĳ���
        # ljust() ��������һ��ԭ�ַ��������,��ʹ�ÿո������ָ�����ȵ����ַ���
        self.sock.send(str.encode(str(len(stringData)).ljust(16)))
        # ��������
        self.sock.send(stringData)
        # ��ȡ����������ֵ
        receive = self.sock.recv(1024)
        #if len(receive):
            #print(str(receive, encoding='utf-8'))
