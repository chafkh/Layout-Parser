# -*- coding: utf-8 -*-
"""Chafi yeees

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GH6huWW1QzjxF-VXHxnl-K7aznf7i0OR

**Installation**
"""

!pip install pdf2image
!apt-get update
!apt-get install poppler-utils

"""**Conversion (facultatif)**"""

from pdf2image import convert_from_path

images = convert_from_path('/content/ANTIOQUIA (1) (1).pdf')

!mkdir pages

for i in range(len(images)):
  images[i].save('pages/page'+str(i)+'.jpg', 'JPEG')

!wget https://paddleocr.bj.bcebos.com/whl/layoutparser-0.0.0-py3-none-any.whl
!pip install -U layoutparser-0.0.0-py3-none-any.whl

!python3 -m pip install paddlepaddle-gpu
!pip install "paddleocr>=2.0.1"
!pip install protobuf==3.20.0
!git clone https://github.com/PaddlePaddle/PaddleOCR.git

!wget http://nz2.archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb

!sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb

"""**Modèle**"""

import cv2
import layoutparser as lp
image = cv2.imread("/content/Capture d’écran 2023-08-07 223407.jpg")

image = image[..., ::-1]

# load model
model = lp.PaddleDetectionLayoutModel(config_path="lp://PubLayNet/ppyolov2_r50vd_dcn_365e_publaynet/config",
                                threshold=0.5,
                                label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"},
                                enforce_cpu=True,
                                enable_mkldnn=True)#math kernel library
# detect
layout = model.detect(image)

layout

x_1=0
y_1=0
x_2=0
y_2=0

for l in layout:
  #print(l)
  if l.type == 'Table':
    x_1 = int(l.block.x_1)
    print(l.block.x_1)
    y_1 = int(l.block.y_1)
    x_2 = int(l.block.x_2)
    y_2 = int(l.block.y_2)

    break

print(x_1,y_1,x_2,y_2)

im = cv2.imread('/content/Capture d’écran 2023-08-07 223407.jpg')

cv2.imwrite('ext_im.jpg', im[y_1:y_2,x_1:x_2])

"""Reconnaissance et detection du tableau"""

from paddleocr import PaddleOCR, draw_ocr

ocr = PaddleOCR(lang='en', use_gpu=False)
image_path = '/content/ext_im.jpg'
image_cv = cv2.imread(image_path)
image_height = image_cv.shape[0]
image_width = image_cv.shape[1]
output = ocr.ocr(image_path)[0]

print(output)

boxes = [line[0] for line in output]
texts = [line[1][0] for line in output]
probabilities = [line[1][1] for line in output]

image_boxes = image_cv.copy()

for box,text in zip(boxes,texts):
  cv2.rectangle(image_boxes, (int(box[0][0]),int(box[0][1])), (int(box[2][0]),int(box[2][1])),(0,0,255),1)
  cv2.putText(image_boxes, text,(int(box[0][0]),int(box[0][1])),cv2.FONT_HERSHEY_SIMPLEX,1,(222,0,0),1)

cv2.imwrite('detections.jpg', image_boxes)

"""**Trait verticale et horizontal**"""

im = image_cv.copy()

horiz_boxes = []
vert_boxes = []

for box in boxes:
  x_h, x_v = 0,int(box[0][0])
  y_h, y_v = int(box[0][1]),0
  width_h,width_v = image_width, int(box[2][0]-box[0][0])
  height_h,height_v = int(box[2][1]-box[0][1]),image_height

  horiz_boxes.append([x_h,y_h,x_h+width_h,y_h+height_h])
  vert_boxes.append([x_v,y_v,x_v+width_v,y_v+height_v])

  cv2.rectangle(im,(x_h,y_h), (x_h+width_h,y_h+height_h),(0,0,255),1)
  cv2.rectangle(im,(x_v,y_v), (x_v+width_v,y_v+height_v),(0,255,0),1)

cv2.imwrite('horiz_vert.jpg',im)

import tensorflow as tf
import numpy as np

horiz_out = tf.image.non_max_suppression(
    horiz_boxes,
    probabilities,
    max_output_size = 1000,
    iou_threshold=0.1,
    score_threshold=float('-inf'),
    name=None
)

horiz_lines = np.sort(np.array(horiz_out))
print(horiz_lines)

im_nms = image_cv.copy()

for val in horiz_lines:
  cv2.rectangle(im_nms, (int(horiz_boxes[val][0]),int(horiz_boxes[val][1])), (int(horiz_boxes[val][2]),int(horiz_boxes[val][3])),(0,0,255),1)

cv2.imwrite('im_nms.jpg',im_nms)

vert_out = tf.image.non_max_suppression(
    vert_boxes,
    probabilities,
    max_output_size = 1000,
    iou_threshold=0.1,
    score_threshold=float('-inf'),
    name=None
)

print(vert_out)

vert_lines = np.sort(np.array(vert_out))
print(vert_lines)

for val in vert_lines:
  cv2.rectangle(im_nms, (int(vert_boxes[val][0]),int(vert_boxes[val][1])), (int(vert_boxes[val][2]),int(vert_boxes[val][3])),(255,0,0),1)

cv2.imwrite('im_nms.jpg',im_nms)

"""**Conversion sous format excel**"""

out_array = [["" for i in range(len(vert_lines))] for j in range(len(horiz_lines))]
print(np.array(out_array).shape)
print(out_array)

unordered_boxes = []

for i in vert_lines:
  print(vert_boxes[i])
  unordered_boxes.append(vert_boxes[i][0])

ordered_boxes = np.argsort(unordered_boxes)
print(ordered_boxes)

def intersection(box_1, box_2):
  return [box_2[0], box_1[1],box_2[2], box_1[3]]

def iou(box_1, box_2):

  x_1 = max(box_1[0], box_2[0])
  y_1 = max(box_1[1], box_2[1])
  x_2 = min(box_1[2], box_2[2])
  y_2 = min(box_1[3], box_2[3])

  inter = abs(max((x_2 - x_1, 0)) * max((y_2 - y_1), 0))
  if inter == 0:
      return 0

  box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
  box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))

  return inter / float(box_1_area + box_2_area - inter)

for i in range(len(horiz_lines)):
  for j in range(len(vert_lines)):
    resultant = intersection(horiz_boxes[horiz_lines[i]], vert_boxes[vert_lines[ordered_boxes[j]]] )

    for b in range(len(boxes)):
      the_box = [boxes[b][0][0],boxes[b][0][1],boxes[b][2][0],boxes[b][2][1]]
      if(iou(resultant,the_box)>0.1):
        out_array[i][j] = texts[b]

out_array=np.array(out_array)

out_array

import pandas as pd

current_bank=['']*len(out_array[0,:])
print(current_bank)

def empty(arr):
  for i in arr:
    if i=='':
      return True
  return False

cleaned_array=[]

for i in range(len(out_array)):
  if not empty(out_array[i]):
    current_bank=[out_array[i][j] for j in range(len(out_array[i]))]
    cleaned_array.append(current_bank)
    not_empty=True
  else:
    for j in range(len(out_array[i])):
      current_bank[j]+=' '+out_array[i][j]
    print('-->',current_bank)
cleaned_array=np.array(cleaned_array)
print(cleaned_array)

pd.DataFrame(out_array).to_excel('sample.xlsx', sheet_name='Sheet1', index=False)