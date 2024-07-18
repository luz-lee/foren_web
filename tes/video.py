import cv2
import numpy as np
import tempfile
import os
import random
from concurrent.futures import ThreadPoolExecutor
from utils import resize_image, text_to_image

# 비디오 워터마크 함수
def process_video(input_path, output_path, process_function, *args, frame_skip=1):
    try:
        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_idx = 0
        futures = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % frame_skip == 0:
                    futures.append(executor.submit(process_function, frame, *args))
                else:
                    futures.append(executor.submit(lambda x: x, frame))
                frame_idx += 1

            for future in futures:
                processed_frame = future.result()
                out.write(processed_frame)

        cap.release()
        out.release()
    except Exception as e:
        print(f"Error processing video: {e}")

def apply_watermark(frame, text_or_image_path, alpha=5, use_image=False):
    height, width = frame.shape[:2]
    if use_image and os.path.exists(text_or_image_path):
        img_wm = cv2.imread(text_or_image_path, cv2.IMREAD_GRAYSCALE)
        img_wm = resize_image(img_wm, (height, width))
    else:
        img_wm = text_to_image(text_or_image_path, (height, width))

    img_f = np.fft.fft2(frame, axes=(0, 1))

    y_random_indices, x_random_indices = list(range(height)), list(range(width))
    random.seed(2021)
    random.shuffle(x_random_indices)
    random.shuffle(y_random_indices)

    random_wm = np.zeros(frame.shape, dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            random_wm[y_random_indices[y], x_random_indices[x]] = img_wm[y, x]

    result_f = img_f + alpha * random_wm

    result = np.fft.ifft2(result_f, axes=(0, 1))
    result = np.real(result)
    result = result.astype(np.uint8)

    return result

def apply_watermark_to_video(input_path, output_path, text_or_image_path, frame_skip=1, use_image=False):
    process_video(input_path, output_path, apply_watermark, text_or_image_path, frame_skip, use_image)

def create_highlighted_video(input_path, output_path, text, positions):
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    font = cv2.FONT_HERSHEY_SIMPLEX

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        for (text_x, text_y, text_w, text_h) in positions:
            cv2.putText(frame, text, (text_x, text_y), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.rectangle(frame, (text_x, text_y - text_h), (text_x + text_w, text_y), (0, 0, 255), 2)

        out.write(frame)

    cap.release()
    out.release()

# 비디오 업로드에 사용될 기타 함수들...


# 비디오 업로드에 사용될 기타 함수들
def add_forensic_watermark(video_path, text, num_watermarks=5):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    temp_fd, watermarked_path = tempfile.mkstemp(suffix=".mp4")
    os.close(temp_fd)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_watermarked = cv2.VideoWriter(watermarked_path, fourcc, fps, (width, height))

    watermark_positions = []

    for frame_idx in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        frame = apply_watermark(frame, text, use_image=False)
        out_watermarked.write(frame)

        if frame_idx % 30 == 0:
            positions = detect_watermark_positions(frame, text)
            watermark_positions.extend(positions)

    cap.release()
    out_watermarked.release()

    return watermarked_path, watermark_positions

def detect_watermark_positions(frame, text):
    watermark_positions = []
    h, w, _ = frame.shape
    ycrcb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    y_channel, _, _ = cv2.split(ycrcb_image)
    dct_y = cv2.dct(np.float32(y_channel))
    font = cv2.FONT_HERSHEY_SIMPLEX

    text_size = cv2.getTextSize(text, font, 0.5, 1)[0]
    text_x = random.randint(0, w - text_size[0])
    text_y = random.randint(text_size[1], h)

    watermark_positions.append((text_x, text_y, text_size[0], text_size[1]))

    return watermark_positions
