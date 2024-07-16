from flask import Flask, request, send_from_directory, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
import os
import cv2
from image import apply_watermark, extract_watermark
from video import apply_watermark_to_video, extract_watermark_from_video
from watermark_detector import add_and_detect_watermark

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'results'
app.config['EXTRACT_FOLDER'] = 'extracts'
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

    if video_file and text:
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

        highlighted_filename = 'highlighted_' + filename
        highlighted_path = os.path.join(app.config['DETECT_FOLDER'], highlighted_filename)
        create_highlighted_video(watermarked_path, highlighted_path, text, positions)

        response = {
            'original_url': url_for('uploaded_file', filename=filename),
            'watermarked_url': url_for('result_file', filename=watermarked_filename),
            'highlighted_url': url_for('detect_file', filename=highlighted_filename)
        }
        return jsonify(response)

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
        extracted_path = os.path.join(app.config['EXTRACT_FOLDER'], extracted_filename)
        watermark, result2 = extract_watermark(img, watermarked_img)
        cv2.imwrite(extracted_path, result2)

        non_visible_watermarked_img, highlighted_img, watermark_positions = add_and_detect_watermark(img, text)
        forensic_watermarked_filename = 'forensic_watermarked_' + filename
        forensic_highlighted_filename = 'forensic_highlighted_' + filename
        forensic_watermarked_path = os.path.join(app.config['DETECT_FOLDER'], forensic_watermarked_filename)
        forensic_highlighted_path = os.path.join(app.config['DETECT_FOLDER'], forensic_highlighted_filename)
        cv2.imwrite(forensic_watermarked_path, non_visible_watermarked_img)
        cv2.imwrite(forensic_highlighted_path, highlighted_img)

        response = {
            'original_url': url_for('uploaded_file', filename=filename),
            'watermarked_url': url_for('result_file', filename=watermarked_filename),
            'highlighted_url': url_for('detect_file', filename=forensic_highlighted_filename),
            'extracted_url': url_for('extract_file', filename=extracted_filename),
            'watermark_positions': watermark_positions
        }
        return jsonify(response)

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

@app.route('/extracts/<filename>')
def extract_file(filename):
    return send_from_directory(app.config['EXTRACT_FOLDER'], filename)

@app.route('/detects/<filename>')
def detect_file(filename):
    return send_from_directory(app.config['DETECT_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['RESULT_FOLDER']):
        os.makedirs(app.config['RESULT_FOLDER'])
    if not os.path.exists(app.config['EXTRACT_FOLDER']):
        os.makedirs(app.config['EXTRACT_FOLDER'])
    if not os.path.exists(app.config['DETECT_FOLDER']):
        os.makedirs(app.config['DETECT_FOLDER'])
    app.run(host='0.0.0.0', port=5000, debug=True)
