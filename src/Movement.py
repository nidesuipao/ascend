"""
    @author: Yuan Yi Fu
"""
from robot_cmd import UPComBotCommand
from client import client
import time
import os

class Movement(object):
    def __init__(self):
        self.isOpen = True
        self.cmd = UPComBotCommand()
        self.client = client()

    def start(self):
        if self.isOpen:
            command = self.cmd.start()
            self.client.senddata(command)
            rec = self.client.rec_data()
            res = b'\xfe\xef\x00\x00\x04\nq\x01\x01~'
            if res == rec:
                return True
            return False
        return False
    # _______________move_______________
    # (direction, speed, turn_speed, time)
    # move_forward(0, 10, 0, 500)  对应↑ 40 1000
    # move_left(90, 10, 0, 500)  对应←
    # move_right(270, 10, 0, 500)  对应→
    # move_backward(180, 10, 0, 500)  对应↓
    # turn_left(0, 0, 100, 500)  对应↙
    # turn_right(0, 0, -100, 500)  对应↘
    # _______________action______________
    # (index) 0-5

    def stop(self, speed=0, times=0):
        if self.isOpen:
            command = self.cmd.Command(0, speed, 0, times)
            self.client.senddata(command)
            return True
        return False

    def move_forward(self, speed=40, times=1000):
        if self.isOpen:
            command = self.cmd.Command(0, speed, 0, times)
            self.client.senddata(command)
            return True
        return False

    def move_left(self, speed=40, times=1000):
        if self.isOpen:
            command = self.cmd.Command(90, speed, 0, times)
            self.client.senddata(command)
            return True
        return False

    def move_right(self, speed=40, times=1000):
        if self.isOpen:
            command = self.cmd.Command(270, speed, 0, times)
            self.client.senddata(command)
            return True
        return False

    def move_backward(self, speed=40, times=1000):
        if self.isOpen:
            command = self.cmd.Command(180, speed, 0, times)
            self.client.senddata(command)
            return True
        return False

    def turn_left(self, speed=10, times=500):
        if self.isOpen:
            command = self.cmd.Command(0, 0, speed * 10, times)
            self.client.senddata(command)
            return True
        return False

    def turn_right(self, speed=10, times=500):
        if self.isOpen:
            command = self.cmd.Command(0, 0, -speed * 10, times)
            self.client.senddata(command)
            return True
        return False

    def left_ward(self):
        if self.isOpen:
            command = self.cmd.Command(270, 11, 20, 400)
            self.client.senddata(command)
            return True
        return False

    def right_ward(self):
        if self.isOpen:
            command = self.cmd.Command(90, 11, -20, 400)
            self.client.senddata(command)
            return True
        return False

    def low_speed_left_ward(self):
        if self.isOpen:
            command = self.cmd.Command(270, 11, 20, 100)
            self.client.senddata(command)
            return True
        return False

    def low_speed_right_ward(self):
        if self.isOpen:
            command = self.cmd.Command(90, 11, -20, 100)
            self.client.senddata(command)
            return True
        return False

    def take_action(self, index):
        # 共设置6个可选动作
        # 0  普通攻击
        # 1
        # 2  宁王竞速
        # 3  种水稻
        # 4  下饭嘲讽
        # 5  肉蛋冲击
        if self.isOpen:
            data = [0] * 1
            data[0] = index & 0xFF
            buffer = self.cmd.GenerateCmd(0x04,0x07, 0x55, 0x01, data)
            self.client.senddata(buffer)
            return True
        return False

    def set_volume(self, vol):
        data = [0] * 1
        data[0] = vol & 0xFF

        buffer = self.cmd.GenerateCmd(0x01, 0x08, 0x01, data)
        self.client.senddata(buffer)

    def robotModeSet(self):
        data = [0] * 1
        data[0] = 2 & 0xFF

        buffer = self.cmd.GenerateCmd(0x09, 0x01, 0x01, data)
        self.client.senddata(buffer)

    def play_sounds(self, filename):
        b_name = filename.encode("GBK")
        l = len(b_name) & 0xFF
        data = [0] * l

        for i in range(l):
            data[i] = b_name[i]
        buffer= self.cmd.GenerateCmd(0x01, 0x70, l, data)
        self.client.senddata(buffer)
'''
    def control_movement(self, command):
	if command == '111\n':
		self.move_forward(speed=40, times=200)
        elif command == '222\n':
            	self.move_left(speed=40, times=200)
        elif command == '333\n':
            	self.move_right(speed=40, times=200)
        elif command == '444\n':
           	self.move_backward(speed=40, times=200)
        elif command == '555\n':
            	self.turn_left(speed=20, times=300)
        elif command == '666\n':
            	self.turn_right(speed=20, times=300)
        elif command == '0\n':
            	self.take_action(0)
        elif command == '1\n':
            	self.take_action(1)
        elif command == '2\n':
            	self.take_action(2)
        elif command == '3\n':
            	self.take_action(3)
        elif command == '4\n':
            	self.take_action(4)
        elif command == '5\n':
            	self.take_action(5)
        else:
            	pass
'''
def writePose(path, pose):
	with open(path, "w") as f:
		f.write(str(pose)+"\n")

def readPose(path):
	while(True):
		if os.access(path, os.F_OK):
			break
		else:
			time.sleep(1)
	with open(path, "r") as f:  # 打开文件
		pose = f.readlines()  #去掉列表中每一个元素的换行符
		for line in pose:
			line = line.replace('\n','')
	return pose

def action(pose):
    if pose == '111':
        mv.move_forward(speed=40, times=200)
    elif pose == '222':		
        mv.move_left(speed=40, times=200)
    elif pose == '333':
        mv.move_right(speed=40, times=200)
    elif pose == '444':
        mv.move_backward(speed=40, times=200)
    elif pose == '555':        	
        mv.turn_left(speed=20, times=300)
    elif pose == '666':
        mv.turn_right(speed=20, times=300)
    elif pose == '0':
        mv.take_action(0)
    elif pose == '1':
        mv.take_action(1)
    elif pose == '2':
        mv.left_ward()
    elif pose == '3':
        mv.right_ward()
    elif pose == '4':
        mv.take_action(4)
    elif pose == '5':
        mv.take_action(5)
    else:
        pass
		


mv = Movement()
mv.start()
i=350
if __name__ == '__main__':
  mv.take_action(1)
  time.sleep(2)
  mv.start()
  
  while(i):
    mv.turn_left(speed=2, times=200)
    time.sleep(0.03)
    i = i - 1
    print(i)
    
  i=200
  while(i):
    mv.start()
    mv.move_forward(speed=8, times=100)
    #mv.move_backward(5,100)
    time.sleep(0.03)
    i = i - 1
    print(i)
  mv.take_action(0)


