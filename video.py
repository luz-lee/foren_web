import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import os
from image import apply_watermark, extract_watermark

def process_video(input_path, output_path, process_function, *args, frame_skip=1):
    try:
        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_idx = 0
        with ThreadPoolExecutor() as executor:
            futures = []
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % frame_skip == 0:
                    futures.append(executor.submit(process_function, frame, *args))
                frame_idx += 1

            for future in futures:
                processed_frame = future.result()
                out.write(processed_frame)

        cap.release()
        out.release()
    except Exception as e:
        print(f"Error processing video: {e}")

def apply_watermark_to_video(input_path, output_path, text_or_image_path, frame_skip=1, use_image=False):
    process_video(input_path, output_path, apply_watermark, text_or_image_path, frame_skip, use_image)

def extract_frame_watermark(frame, watermarked_frame, alpha=5):
    _, extracted_frame = extract_watermark(frame, watermarked_frame, alpha)
    return extracted_frame

def extract_watermark_from_video(input_path, watermarked_path, output_path, alpha=5, frame_skip=1):
    try:
        cap = cv2.VideoCapture(watermarked_path)
        watermarked_frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            watermarked_frames.append(frame)
        cap.release()

        cap = cv2.VideoCapture(input_path)
        frame_list = []
        frame_idx = 0
        with ThreadPoolExecutor() as executor:
            futures = []
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % frame_skip == 0:
                    watermarked_frame = watermarked_frames[frame_idx]
                    futures.append(executor.submit(extract_frame_watermark, frame, watermarked_frame, alpha))
                frame_idx += 1

            for future in futures:
                processed_frame = future.result()
                frame_list.append(processed_frame)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame in frame_list:
            out.write(frame)

        out.release()
    except Exception as e:
        print(f"Error extracting watermark: {e}")
