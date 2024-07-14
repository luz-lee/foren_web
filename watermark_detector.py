import cv2
import numpy as np
import tempfile
import os
import random

def add_forensic_watermark(video_path, watermark_text, num_watermarks=5):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
    os.close(temp_fd)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_watermarked = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
    
    temp_fd, temp_path_highlight = tempfile.mkstemp(suffix=".mp4")
    os.close(temp_fd)
    
    out_highlight = cv2.VideoWriter(temp_path_highlight, fourcc, fps, (width, height))

    font = cv2.FONT_HERSHEY_SIMPLEX
    watermark_positions = []

    for _ in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        h_new = (h // 8) * 8
        w_new = (w // 8) * 8
        image_resized = cv2.resize(frame, (w_new, h_new))
        
        ycrcb_image = cv2.cvtColor(image_resized, cv2.COLOR_BGR2YCrCb)
        y_channel, cr_channel, cb_channel = cv2.split(ycrcb_image)
        
        dct_y = cv2.dct(np.float32(y_channel))
        
        rows, cols = dct_y.shape
        if not watermark_positions:
            for _ in range(num_watermarks):
                text_size = cv2.getTextSize(watermark_text, font, 0.5, 1)[0]
                text_x = np.random.randint(0, cols - text_size[0])
                text_y = np.random.randint(text_size[1], rows)
                watermark_positions.append((text_x, text_y, text_size[0], text_size[1]))

        for (text_x, text_y, text_w, text_h) in watermark_positions:
            watermark = np.zeros_like(dct_y)
            watermark = cv2.putText(watermark, watermark_text, (text_x, text_y), font, 0.5, (1, 1, 1), 1, cv2.LINE_AA)
            dct_y += watermark * 0.01
        
        idct_y = cv2.idct(dct_y)
        
        ycrcb_image[:, :, 0] = idct_y
        watermarked_image = cv2.cvtColor(ycrcb_image, cv2.COLOR_YCrCb2BGR)

        watermark_highlight = watermarked_image.copy()
        for (text_x, text_y, text_w, text_h) in watermark_positions:
            cv2.putText(watermark_highlight, watermark_text, (text_x, text_y), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.rectangle(watermark_highlight, (text_x, text_y - text_h), (text_x + text_w, text_y), (0, 0, 255), 2)

        out_watermarked.write(watermarked_image)
        out_highlight.write(watermark_highlight)

    cap.release()
    out_watermarked.release()
    out_highlight.release()

    return temp_path, temp_path_highlight, watermark_positions

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
