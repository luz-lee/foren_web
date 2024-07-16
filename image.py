import numpy as np
import cv2
import os
import random
from utils import resize_image, text_to_image

def apply_watermark(img, text_or_image_path, alpha=5, use_image=False):
    height, width = img.shape[:2]
    if use_image and os.path.exists(text_or_image_path):
        img_wm = cv2.imread(text_or_image_path, cv2.IMREAD_GRAYSCALE)
        img_wm = resize_image(img_wm, (height, width))
    else:
        img_wm = text_to_image(text_or_image_path, (height, width))

    img_f = np.fft.fft2(img)
    
    y_random_indices, x_random_indices = list(range(height)), list(range(width))
    random.seed(2021)
    random.shuffle(x_random_indices)
    random.shuffle(y_random_indices)
    
    random_wm = np.zeros(img.shape, dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            random_wm[y_random_indices[y], x_random_indices[x]] = img_wm[y, x]
    
    result_f = img_f + alpha * random_wm
    
    result = np.fft.ifft2(result_f)
    result = np.real(result)
    result = result.astype(np.uint8)
    
    return result

def extract_watermark(img_ori, img_input, alpha=5):
    height, width = img_ori.shape[:2]
    
    img_input = resize_image(img_input, (height, width))
    
    img_ori_f = np.fft.fft2(img_ori)
    img_input_f = np.fft.fft2(img_input)
    
    watermark = (img_input_f - img_ori_f) / alpha
    watermark = np.real(watermark).astype(np.uint8)
    
    y_random_indices, x_random_indices = list(range(height)), list(range(width))
    random.seed(2021)
    random.shuffle(x_random_indices)
    random.shuffle(y_random_indices)
    
    result2 = np.zeros(watermark.shape, dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            result2[y, x] = watermark[y_random_indices[y], x_random_indices[x]]
    
    return watermark, result2
