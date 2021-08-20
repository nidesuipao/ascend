# from color_detector import ColorBounding
# coding=gbk
from detect import detect
import threading
from collections import deque
from Movement import Movement
from detect import detect
import cv2
import time
import random
import os

# 640*480
MID_WIDTH = 640
MID_HEIGHT = 360
ALL_AREA = 1280 * 720
lock = threading.Lock()
detect = detect()

class AutoMoveThread(threading.Thread):
    def __init__(self,input):
        # self.cb = ColorBounding()
        super(AutoMoveThread).__init__()
        self._jobq = input
        self.buffer = list()
        self.mv = Movement()
        threading.Thread.__init__(self)
        
        # 是否找到三个物体中有正确人脸的目标物体，在找到目标人脸后置为True
        self.isFind = True
        # 整体搬运流程结束，退出循环
        self.test_flag = 0
        self.num = 0

    def run(self):
        # 定义随机寻找顺序:红 绿 黄
        color = ['green', 'red', 'yellow']
        while 1:
            print("2")
            time.sleep(1)
        # random.shuffle(color)
        
        while not self.isFinal and color:
            self.res = list()
            color_now = color[0]
            color.pop(0)
            self.implement(color_now)
        

    def implement(self, color):
        flag = False
        circle_flag = False
        signal = True
        self.mv.take_action(1)
        time.sleep(3)
        banyun = False
        print("Now color: ", color)
        while True:
            if len(self._jobq) != 0:
                # 取一帧
                lock.acquire()
                frame_new = self._jobq.pop()
                lock.release()
                flag = True

                """
                    找color物体
                """
                if not circle_flag:
                    if self.get_box_Position(frame_new, color) == (-1, -1):
                        self.mv.turn_left(10, 200)
                        time.sleep(0.5)
                    """
                        通过小幅度左右移使机器人位于X轴正中 
                        X轴正中：280 - 360
    
                    """
                    x_now, y_now = self.get_box_Position(frame_new, color)
                    if self.get_box_Position(frame_new, color) != (-1, -1):
                        if x_now >= 680:
                            # 偏右往右
                            self.mv.turn_right(10, 50)
                            time.sleep(0.3)
                        elif x_now <= 600:
                            # 偏左往左
                            self.mv.turn_left(10, 50)
                            time.sleep(0.3)
                        else:
                            """
                                这一步之前是已经移正图像，然后向前走到一定的距离
                                round = 450mm
                            """
                            self.mv.move_forward(10, 500)
                            distance = 10
                            print('distance: ', distance)
                            if distance < 450 or self.getColorArea() / ALL_AREA >= 0.22:
                                print("Come On!")
                                circle_flag = True
                
                else:
                    """
                        转圈 + 找人脸
                    """
                    if not signal:
                        x_fa, y_fa = self.fa.face_find(frame_new)
                        if self.fa.face_find(frame_new) == (-1, -1):
                            """
                                Face not found, turn around
                            """
                            self.mv.left_ward()
                            self.mv.left_ward()
                            time.sleep(0.5)
                        else:
                            """
                                Find face and turn left/right
                                320 * 240
                            """
                            print('face x: ', x_fa, 'face y:', y_fa)
                            if x_fa >= 210:
                                # 偏右往右
                                self.mv.move_right(5, 100)
                                time.sleep(0.5)
                            elif x_fa <= 110:
                                # 偏左往左
                                self.mv.move_left(5, 100)
                                time.sleep(0.5)
                            else:
                                signal = True

                    else:
                        """
                            此处人脸已经对正，开始人脸识别
                            人脸识别正确：返回1, face_x, face_y, 执行物体搬运过程
                            人脸识别错误：返回0， -1， -1
                        """
                        print("开始人脸识别")
                        ret, posx, posy = self.fad.face_rec(frame_new)
                        if len(self.res) <= 10:
                            self.res.append(ret)
                        if len(self.res) >= 6:
                            for r in self.res:
                                if r:
                                    banyun = True
                            if banyun:
                                print("搬运")
                                self.moveObject()
                                self.isFind = True
                                break
                            else:
                                print("不搬运，撤退")
                                self.leaveObject()
                                break
                

            elif flag and len(self._jobq) == 0:
                break
        

        if self.isFind:
            # 已经搬到想要的物体，执行搬到终点操作，同时isFinal置为True
            print("朝着终点搬运！")
            self.isFinal = True
            terminal_flag = False

            while True:
                if len(self._jobq) != 0:
                    lock.acquire()
                    frame = self._jobq.pop()
                    lock.release()
                    flag = True

                    x_now, y_now = self.getColorObjectPosition(frame, 'black')
                    if self.getColorObjectPosition(frame, 'black') == (-1, -1) and not terminal_flag:
                        self.mv.turn_left(10, 200)
                        time.sleep(0.3)
                        """
                通过小幅度左右移使机器人位于X轴正中 
                X轴正中：280 - 360
  
            """

                    if self.getColorObjectPosition(frame, 'black') != (-1, -1) and not terminal_flag:
                        if x_now >= 380:
                            # 偏右往右
                            self.mv.turn_right(10, 50)
                            time.sleep(0.4)
                        elif x_now <= 260:
                            # 偏左往左
                            self.mv.turn_left(10, 50)
                            time.sleep(0.4)
                        else:
                            terminal_flag = True
                    """
                        前进，抵达终点，放下物体
                    """
                    x_now, y_now = self.getColorObjectPosition(frame, 'black')
                    if terminal_flag and self.getColorArea() / ALL_AREA <= 0.01:
                        self.mv.move_forward(15, 500)
                        terminal_flag = False

                    if terminal_flag:
                        """
                            self.mv.move_forward(15, 500)
              
                        if self.getColorArea() / ALL_AREA >= 0.05:
                            self.mv.move_forward(40, 2000)
                            time.sleep(10)
                            self.mv.move_forward(20, 4000)
                            time.sleep(10)
                            print("Terminal!")
                            self.mv.take_action(1)  # todo
                            time.sleep(10)
                            break
                        """
                        """
                            一种激进的策略
                        """
                        self.mv.move_forward(30, 8000)
                        time.sleep(10)
                        print("Terminal!")
                        self.mv.take_action(2)
                        time.sleep(10)
                        break

                elif flag and len(self._jobq) == 0:
                    break

    def get_box_Position(self, frame, color):
        x, y = self.cb.bounding(frame, color)
        print("x:", x, "y:", y)
        return x, y

    def get_box_Area(self):
        area = self.cb.red_area
        print('color_area ', area)
        return area

    def circleMove(self):
        self.mv.left_ward()

    def moveObject(self):
        self.mv.take_action(1)
        time.sleep(5)
        self.mv.move_forward(20, 2500)
        time.sleep(10)
        self.mv.take_action(0)
        time.sleep(10)

    def leaveObject(self):
        self.mv.move_backward(20, 2000)
        time.sleep(5)


if __name__ == "__main__":
    q = deque([], 10)
    th2 = AutoMoveThread(q)
    th2.start()  # 开启两个线程
    while 1:
        res = detect.excute()
        lock.acquire()
        if len(q) == 10:
            q.popleft()
        else:
            q.append(res)
        lock.release()

        




