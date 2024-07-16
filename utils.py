import numpy as np
import cv2
import random

# 공통 유틸리티 함수
def resize_image(img, shape):
    return cv2.resize(img, (shape[1], shape[0]), interpolation=cv2.INTER_LINEAR)

def text_to_image(text, img_shape, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=3, thickness=5):
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (img_shape[1] - text_size[0]) // 2
    text_y = (img_shape[0] + text_size[1]) // 2

    img_wm = np.zeros(img_shape, dtype=np.uint8)
    cv2.putText(img_wm, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)

    return img_wm
