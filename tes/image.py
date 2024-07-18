import numpy as np
import cv2
import os
import random
from utils import resize_image, text_to_image

# 이미지 워터마크 함수
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

def add_and_detect_watermark(image, watermark_text, num_watermarks=5):
    watermark_positions = []

    h, w, _ = image.shape
    h_new = (h // 8) * 8
    w_new = (w // 8) * 8
    image_resized = cv2.resize(image, (w_new, h_new))
    
    ycrcb_image = cv2.cvtColor(image_resized, cv2.COLOR_BGR2YCrCb)
    y_channel, cr_channel, cb_channel = cv2.split(ycrcb_image)
    
    dct_y = cv2.dct(np.float32(y_channel))
    
    rows, cols = dct_y.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    for _ in range(num_watermarks):
        text_size = cv2.getTextSize(watermark_text, font, 0.5, 1)[0]
        text_x = random.randint(0, cols - text_size[0])
        text_y = random.randint(text_size[1], rows)
        watermark = np.zeros_like(dct_y)
        watermark = cv2.putText(watermark, watermark_text, (text_x, text_y), font, 0.5, (1, 1, 1), 1, cv2.LINE_AA)
        dct_y += watermark * 0.01
        watermark_positions.append((text_x, text_y, text_size[0], text_size[1]))
    
    idct_y = cv2.idct(dct_y)
    
    ycrcb_image[:, :, 0] = idct_y
    watermarked_image = cv2.cvtColor(ycrcb_image, cv2.COLOR_YCrCb2BGR)
    
    non_visible_watermark_image = watermarked_image.copy()
    
    watermark_highlight = watermarked_image.copy()
    for (text_x, text_y, text_w, text_h) in watermark_positions:
        cv2.putText(watermark_highlight, watermark_text, (text_x, text_y), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.rectangle(watermark_highlight, (text_x, text_y - text_h), (text_x + text_w, text_y), (0, 0, 255), 2)
    
    return non_visible_watermark_image, watermark_highlight, watermark_positions
