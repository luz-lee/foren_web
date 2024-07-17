from flask import Flask, request, send_from_directory, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import cv2
from image import apply_watermark, extract_watermark, add_and_detect_watermark
from video import apply_watermark_to_video, create_highlighted_video
from watermark_detector import add_forensic_watermark

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'results'
app.config['DETECT_FOLDER'] = 'detects'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    video_file = request.files.get('video')
    image_file = request.files.get('image')
    text = request.form['text']
    watermark_image = request.files.get('watermark_image')
    use_image = False

    if video_file:
        filename = secure_filename(video_file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(input_path)
        watermark_image_path = text
        if watermark_image:
            watermark_filename = secure_filename(watermark_image.filename)
            watermark_image_path = os.path.join(app.config['UPLOAD_FOLDER'], watermark_filename)
            watermark_image.save(watermark_image_path)
            use_image = True

        watermarked_filename = 'watermarked_' + filename
        watermarked_path = os.path.join(app.config['RESULT_FOLDER'], watermarked_filename)
        apply_watermark_to_video(input_path, watermarked_path, watermark_image_path, frame_skip=2, use_image=use_image)

        forensic_watermarked_path, forensic_highlight_path, watermark_positions = add_forensic_watermark(input_path, text)
        forensic_watermarked_filename = 'forensic_watermarked_' + filename
        forensic_highlight_filename = 'forensic_highlighted_' + filename
        final_forensic_watermarked_path = os.path.join(app.config['DETECT_FOLDER'], forensic_watermarked_filename)
        final_forensic_highlight_path = os.path.join(app.config['DETECT_FOLDER'], forensic_highlight_filename)
        os.rename(forensic_watermarked_path, final_forensic_watermarked_path)
        os.rename(forensic_highlight_path, final_forensic_highlight_path)

        return jsonify({
            'original_url': os.path.join('/uploads', filename),
            'forensic_watermarked_url': os.path.join('/detects', forensic_watermarked_filename),
            'forensic_highlight_url': os.path.join('/detects', forensic_highlight_filename),
            'watermark_positions': watermark_positions
        })
    elif image_file and text:
        filename = secure_filename(image_file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(input_path)
        img = cv2.imread(input_path)
        watermarked_img = apply_watermark(img, text)
        watermarked_filename = 'watermarked_' + filename
        watermarked_path = os.path.join(app.config['RESULT_FOLDER'], watermarked_filename)
        cv2.imwrite(watermarked_path, watermarked_img)
        extracted_filename = 'extracted_' + filename
        extracted_path = os.path.join(app.config['RESULT_FOLDER'], extracted_filename)
        watermark, result2 = extract_watermark(img, watermarked_img)
        cv2.imwrite(extracted_path, result2)

        non_visible_watermarked_img, highlighted_img, watermark_positions = add_and_detect_watermark(img, text)
        forensic_watermarked_filename = 'forensic_watermarked_' + filename
        forensic_highlighted_filename = 'forensic_highlighted_' + filename
        forensic_watermarked_path = os.path.join(app.config['DETECT_FOLDER'], forensic_watermarked_filename)
        forensic_highlighted_path = os.path.join(app.config['DETECT_FOLDER'], forensic_highlighted_filename)
        cv2.imwrite(forensic_watermarked_path, non_visible_watermarked_img)
        cv2.imwrite(forensic_highlighted_path, highlighted_img)

        return jsonify({
            'original_url': os.path.join('/uploads', filename),
            'extracted_url': os.path.join('/results', extracted_filename),
            'forensic_watermarked_url': os.path.join('/detects', forensic_watermarked_filename),
            'forensic_highlight_url': os.path.join('/detects', forensic_highlighted_filename),
            'watermark_positions': watermark_positions
        })
    return 'Invalid request', 400

@app.route('/upload_image')
def upload_image():
    return render_template('upload_image.html')

@app.route('/upload_video')
def upload_video():
    return render_template('upload_video.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/results/<filename>')
def result_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

@app.route('/detects/<filename>')
def detect_file(filename):
    return send_from_directory(app.config['DETECT_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['RESULT_FOLDER']):
        os.makedirs(app.config['RESULT_FOLDER'])
    if not os.path.exists(app.config['DETECT_FOLDER']):
        os.makedirs(app.config['DETECT_FOLDER'])
    app.run(host='0.0.0.0', port=5000, debug=True)
