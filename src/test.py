import socket
sk = socket.socket(type=socket.SOCK_DGRAM)
while 1:
    s = input('>>>').encode('utf-8')
    sk.sendto(s,('192.168.8.186',8888))
sk.close()