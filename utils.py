import numpy as np
import cv2
import random
from multiprocessing import Pool, cpu_count
from moviepy.editor import VideoFileClip
import os

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

# 비디오 워터마크 함수
def process_frame(frame_data):
    frame, text_or_image_path, use_image = frame_data
    result = apply_watermark(frame, text_or_image_path, use_image=use_image)
    return result

def process_video(input_path, output_path, text_or_image_path, frame_skip=1, use_image=False):
    try:
        clip = VideoFileClip(input_path)
        fps = clip.fps

        frame_data_list = []
        for frame in clip.iter_frames():
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to BGR format for OpenCV
            frame_data_list.append((frame, text_or_image_path, use_image))

        with Pool(cpu_count()) as pool:
            watermarked_frames = pool.map(process_frame, frame_data_list)

        # Create a new video clip with watermarked frames and original audio
        watermarked_clip = VideoFileClip(
            input_path,
            has_mask=False
        ).set_duration(clip.duration)

        def make_frame(t):
            frame_idx = int(t * fps)
            if frame_idx < len(watermarked_frames):
                return cv2.cvtColor(watermarked_frames[frame_idx], cv2.COLOR_BGR2RGB)  # Convert back to RGB format
            else:
                return cv2.cvtColor(watermarked_frames[-1], cv2.COLOR_BGR2RGB)  # Convert back to RGB format

        watermarked_clip = watermarked_clip.set_make_frame(make_frame)
        watermarked_clip = watermarked_clip.set_audio(clip.audio)
        watermarked_clip.write_videofile(output_path, codec='libx264', fps=fps)

    except Exception as e:
        print(f"Error processing video: {e}")

def apply_watermark_to_video(input_path, output_path, text_or_image_path, frame_skip=1, use_image=False):
    process_video(input_path, output_path, text_or_image_path, frame_skip, use_image)
