import socket
from robot_cmd import UPComBotCommand


#client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#print(data)
'''
server_address = ("192.168.4.1", 9999)  # 接收方 服务器的ip地址和端口号
client_socket.sendto(data, server_address)
rec = client_socket.recv(1024)
print(rec)
client_socket.sendto(data2, server_address)
client_socket.close()
'''
class client(object):
    def __init__(self):
        self.isOpen = True
        self.server_address = ("192.168.8.221",9999)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rec = ""

    def senddata(self,data):
        if self.isOpen:
            self.client_socket.sendto(data, self.server_address)
            return True
        return False

    def rec_data(self):
        if self.isOpen:
            self.rec = self.client_socket.recv(1024)
            return self.rec
        return False

    def socket_close(self):
        if self.isOpen:
            self.client_socket.close()
            return True
        return False



