from flask import Flask, request, send_from_directory, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import cv2
from utils import apply_watermark, apply_watermark_to_video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'results'

# Create necessary directories
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['RESULT_FOLDER']):
    os.makedirs(app.config['RESULT_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload/image')
def upload_image():
    return render_template('upload_image.html')

@app.route('/upload/video')
def upload_video():
    return render_template('upload_video.html')

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
        return jsonify({
            'original_url': filename,
            'watermarked_url': watermarked_filename
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
        return jsonify({
            'original_url': filename,
            'watermarked_url': watermarked_filename
        })
    return 'Invalid request', 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/results/<filename>')
def result_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
