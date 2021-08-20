import sys

sys.path.append("../../../../common")
sys.path.append("../")
import os
import numpy as np
import acl
import cv2 as cv
from PIL import Image
import time
import glob
import socket

import atlas_utils.constants as const
from atlas_utils.acl_model import Model
from atlas_utils.acl_resource import AclResource
from atlas_utils.camera import Camera
from atlas_utils import presenteragent
from vgg_ssd import VggSsd
from atlas_utils.acl_dvpp import Dvpp
from acl_image import AclImage
import acl
from box_client import client

labels = ["yellow", "green", "red"]

INPUT_DIR = '../data/'
OUTPUT_DIR = '../out/'
MODEL_PATH = "../model/box.om"
MODEL_WIDTH = 416
MODEL_HEIGHT = 416
class_num = 3
stride_list = [8, 16, 32]

anchors_1 = np.array([[27, 39], [38, 57], [45, 69]]) / stride_list[0]
anchors_2 = np.array([[48, 68], [54, 78], [68, 85]]) / stride_list[1]
anchors_3 = np.array([[68, 96], [91, 115], [110, 155]]) / stride_list[2]
anchor_list = [anchors_1, anchors_2, anchors_3]

conf_threshold = 0.4
iou_threshold = 0.7

FACE_DETEC_CONF = "../scripts/face_detection.conf"
CAMERA_FRAME_WIDTH = 1280
CAMERA_FRAME_HEIGHT = 720

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 255), (255, 255, 0)]

class detect:
    def __init__(self):
        self.cl = client()
        self.acl_resource = AclResource()
        self.acl_resource.init()
        self._dvpp = Dvpp(self.acl_resource)
        self.model = Model(MODEL_PATH)
        self.cap = Camera(0)
        self.cl.connect()
        if not os.path.exists(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)

    def post_process(self,infer_output, origin_img):
        # print("post process")
        result_return = dict()
        img_h = origin_img.size[1]
        img_w = origin_img.size[0]
        scale = min(float(MODEL_WIDTH) / float(img_w), float(MODEL_HEIGHT) / float(img_h))
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        shift_x_ratio = (MODEL_WIDTH - new_w) / 2.0 / MODEL_WIDTH
        shift_y_ratio = (MODEL_HEIGHT - new_h) / 2.0 / MODEL_HEIGHT
        class_number = len(labels)
        num_channel = 3 * (class_number + 5)
        x_scale = MODEL_WIDTH / float(new_w)
        y_scale = MODEL_HEIGHT / float(new_h)
        all_boxes = [[] for ix in range(class_number)]
        for ix in range(3):
            pred = infer_output[2 - ix].reshape((MODEL_HEIGHT // stride_list[ix], \
                                                 MODEL_WIDTH // stride_list[ix], num_channel))
            anchors = anchor_list[ix]
            boxes = self.decode_bbox(pred, anchors, img_w, img_h, x_scale, y_scale, shift_x_ratio, shift_y_ratio)
            all_boxes = [all_boxes[iy] + boxes[iy] for iy in range(class_number)]

        res = self.apply_nms(all_boxes, iou_threshold)
        if not res:
            result_return['detection_classes'] = []
            result_return['detection_boxes'] = []
            result_return['detection_scores'] = []
            return result_return
        else:
            new_res = np.array(res)
            picked_boxes = new_res[:, 0:4]
            picked_boxes = picked_boxes[:, [1, 0, 3, 2]]
            picked_classes = self.convert_labels(new_res[:, 4])
            picked_score = new_res[:, 5]
            result_return['detection_classes'] = picked_classes
            result_return['detection_boxes'] = picked_boxes.tolist()
            result_return['detection_scores'] = picked_score.tolist()
            return result_return

    def convert_labels(self,label_list):
        if isinstance(label_list, np.ndarray):
            label_list = label_list.tolist()
            label_names = [labels[int(index)] for index in label_list]
        return label_names

    def decode_bbox(self,conv_output, anchors, img_w, img_h, x_scale, y_scale, shift_x_ratio, shift_y_ratio):
        def _sigmoid(x):
            s = 1 / (1 + np.exp(-x))
            return s

        h, w, _ = conv_output.shape

        pred = conv_output.reshape((h * w, 3, 5 + class_num))

        pred[..., 4:] = _sigmoid(pred[..., 4:])
        pred[..., 0] = (_sigmoid(pred[..., 0]) + np.tile(range(w), (3, h)).transpose((1, 0))) / w
        pred[..., 1] = (_sigmoid(pred[..., 1]) + np.tile(np.repeat(range(h), w), (3, 1)).transpose((1, 0))) / h
        pred[..., 2] = np.exp(pred[..., 2]) * anchors[:, 0:1].transpose((1, 0)) / w
        pred[..., 3] = np.exp(pred[..., 3]) * anchors[:, 1:2].transpose((1, 0)) / h

        bbox = np.zeros((h * w, 3, 4))
        bbox[..., 0] = np.maximum((pred[..., 0] - pred[..., 2] / 2.0 - shift_x_ratio) * x_scale * img_w, 0)  # x_min
        bbox[..., 1] = np.maximum((pred[..., 1] - pred[..., 3] / 2.0 - shift_y_ratio) * y_scale * img_h, 0)  # y_min
        bbox[..., 2] = np.minimum((pred[..., 0] + pred[..., 2] / 2.0 - shift_x_ratio) * x_scale * img_w, img_w)  # x_max
        bbox[..., 3] = np.minimum((pred[..., 1] + pred[..., 3] / 2.0 - shift_y_ratio) * y_scale * img_h, img_h)  # y_max

        pred[..., :4] = bbox
        pred = pred.reshape((-1, 5 + class_num))
        pred[:, 4] = pred[:, 4] * pred[:, 5:].max(1)
        pred = pred[pred[:, 4] >= conf_threshold]
        pred[:, 5] = np.argmax(pred[:, 5:], axis=-1)

        all_boxes = [[] for ix in range(class_num)]
        for ix in range(pred.shape[0]):
            box = [int(pred[ix, iy]) for iy in range(4)]
            box.append(int(pred[ix, 5]))
            box.append(pred[ix, 4])
            all_boxes[box[4] - 1].append(box)

        return all_boxes

    def apply_nms(self,all_boxes, thres):
        res = []

        for cls in range(class_num):
            cls_bboxes = all_boxes[cls]
            sorted_boxes = sorted(cls_bboxes, key=lambda d: d[5])[::-1]

            p = dict()
            for i in range(len(sorted_boxes)):
                if i in p:
                    continue

                truth = sorted_boxes[i]
                for j in range(i + 1, len(sorted_boxes)):
                    if j in p:
                        continue
                    box = sorted_boxes[j]
                    iou = self.cal_iou(box, truth)
                    if iou >= thres:
                        p[j] = 1

            for i in range(len(sorted_boxes)):
                if i not in p:
                    res.append(sorted_boxes[i])
        return res

    def preprocess(self,image):
        img_h = image.size[1]
        img_w = image.size[0]
        net_h = MODEL_HEIGHT
        net_w = MODEL_WIDTH

        scale = min(float(net_w) / float(img_w), float(net_h) / float(img_h))
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        shift_x = (net_w - new_w) // 2
        shift_y = (net_h - new_h) // 2
        shift_x_ratio = (net_w - new_w) / 2.0 / net_w
        shift_y_ratio = (net_h - new_h) / 2.0 / net_h

        image_ = image.resize((new_w, new_h))
        new_image = np.zeros((net_h, net_w, 3), np.uint8)
        new_image[shift_y: new_h + shift_y, shift_x: new_w + shift_x, :] = np.array(image_)
        new_image = new_image.astype(np.float32)
        new_image = new_image / 255

        return new_image, image

    def overlap(self,x1, x2, x3, x4):
        left = max(x1, x3)
        right = min(x2, x4)
        return right - left

    def cal_iou(self,box, truth):
        w = self.overlap(box[0], box[2], truth[0], truth[2])
        h = self.overlap(box[1], box[3], truth[1], truth[3])
        if w <= 0 or h <= 0:
            return 0
        inter_area = w * h
        union_area = (box[2] - box[0]) * (box[3] - box[1]) + (truth[2] - truth[0]) * (truth[3] - truth[1]) - inter_area
        return inter_area * 1.0 / union_area

    def excute(self):
        time_start = time.time()
        image = self.cap.read()
        
        np_image = image.nparray()
        np_image = np_image.reshape((1080, 1280)).copy()
        np_image = np_image.astype(np.uint8)
        pic = cv.cvtColor(np_image, cv.COLOR_YUV420sp2RGB)
        pic = cv.flip(pic, -1)
        bgr_img = pic
        pic = Image.fromarray(cv.cvtColor(pic,cv.COLOR_BGR2RGB))
        
        
        # preprocess
        data, orig = self.preprocess(pic)
        # data, orig = preprocess(bgr_img)
        # Send into model inference
        result_list = self.model.execute([data, ])
        # Process inference results
        result_return = self.post_process(result_list, orig)
        current_class = []
        result_box = []
        for i in range(len(result_return['detection_classes'])-1,-1,-1):
            #current_class = []
            class_name = result_return['detection_classes'][i]
            if class_name in current_class:
              continue
            current_class.append(class_name)
            box = result_return['detection_boxes'][i]
            result_box.append([class_name,box])
            confidence = result_return['detection_scores'][i]
            cv.rectangle(bgr_img, (int(box[1]), int(box[0])), (int(box[3]), int(box[2])), colors[0], 5)
            p3 = (max(int(box[1]), 15), max(int(box[0]), 15))
            out_label = str(i) + str(class_name)+str('%.2f'%confidence)
            cv.putText(bgr_img, out_label, (int(box[1]), int(box[0])), cv.FONT_ITALIC, 1, colors[2], 2)
            #print(str(out_label), (int(box[1]), int(box[0])), (int(box[3]), int(box[2])))

        time_end = time.time()
        fps = 1 / (time_end - time_start)
        label = "fps:" + str('%.3f' % fps)
        cv.putText(bgr_img, str(label), (50, 50), cv.FONT_ITALIC, 1, (255, 255, 255), 2)
        self.cl.SendVideo(bgr_img)
        return result_box

    def end(self):
        self.cl.disconnect()

if __name__ == '__main__':
    detect = detect()
    while 1:
        res=detect.excute()
        print(res)
    detect.end()
        





