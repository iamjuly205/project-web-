
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import io
from PIL import Image
import rembg
import os
import logging


# Create app and load config

# --- App & Config ---
app = Flask(__name__)
app.config['MAX_IMAGE_PIXELS'] = int(os.getenv('MAX_IMAGE_PIXELS', 10000))
CORS(app)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("image-api")


# --- Helper functions ---
def is_image_file(file_storage):
    if not file_storage:
        return False
    mimetype = getattr(file_storage, 'mimetype', '') or ''
    return mimetype.startswith('image/')


def remove_bg(image_bytes):
    # rembg.remove expects bytes and returns bytes (PNG)
    return rembg.remove(image_bytes)


def resize_image(image, width, height):
    # image: numpy array (H,W,C)
    return cv2.resize(image, (width, height))


def crop_to_ratio(image, ratio_w, ratio_h):
    h, w = image.shape[:2]
    target_w = w
    target_h = int(w * ratio_h / ratio_w)
    if target_h > h:
        target_h = h
        target_w = int(h * ratio_w / ratio_h)
    x = max((w - target_w) // 2, 0)
    y = max((h - target_h) // 2, 0)
    return image[y:y+target_h, x:x+target_w]


# --- Routes ---
@app.route('/')
def index():
    return jsonify({
        'message': 'Image Processing API',
        'endpoints': {
            '/remove-bg': 'POST (image file)',
            '/resize': 'POST (image file, width, height)',
            '/crop': 'POST (image file, ratio W:H)'
        }
    })


@app.route('/remove-bg', methods=['POST'])
def api_remove_bg():
    file = request.files.get('image')
    if not file or not is_image_file(file):
        return jsonify({'error': 'No image uploaded or invalid file type'}), 400
    try:
        img_bytes = file.read()
        if not img_bytes:
            return jsonify({'error': 'Empty file'}), 400
        result_bytes = remove_bg(img_bytes)
        logger.info('Background removed for image (%d bytes)', len(img_bytes))
        return send_file(io.BytesIO(result_bytes), mimetype='image/png')
    except Exception as e:
        logger.exception('remove-bg error')
        return jsonify({'error': 'Failed to remove background'}), 500


@app.route('/resize', methods=['POST'])
def api_resize():
    file = request.files.get('image')
    if not file or not is_image_file(file):
        return jsonify({'error': 'No image uploaded or invalid file type'}), 400
    try:
        width = int(request.form.get('width', 0))
        height = int(request.form.get('height', 0))
    except ValueError:
        return jsonify({'error': 'Width and height must be integers'}), 400
    if width <= 0 or height <= 0 or width > app.config['MAX_IMAGE_PIXELS'] or height > app.config['MAX_IMAGE_PIXELS']:
        return jsonify({'error': 'Invalid width/height or exceeds limit'}), 400
    try:
        img = Image.open(file.stream).convert('RGBA')
        img_np = np.array(img)
        resized = resize_image(img_np, width, height)
        result = Image.fromarray(resized)
        buf = io.BytesIO()
        result.save(buf, format='PNG')
        buf.seek(0)
        logger.info('Resized image to %dx%d', width, height)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        logger.exception('resize error')
        return jsonify({'error': 'Failed to resize image'}), 500


@app.route('/crop', methods=['POST'])
def api_crop():
    file = request.files.get('image')
    ratio = request.form.get('ratio', '')
    if not file or not is_image_file(file):
        return jsonify({'error': 'No image uploaded or invalid file type'}), 400
    if ':' not in ratio:
        return jsonify({'error': 'Invalid ratio format. Use W:H'}), 400
    try:
        w_ratio, h_ratio = map(int, ratio.split(':'))
    except ValueError:
        return jsonify({'error': 'Ratio parts must be integers'}), 400
    if w_ratio <= 0 or h_ratio <= 0:
        return jsonify({'error': 'Ratio values must be positive'}), 400
    try:
        img = Image.open(file.stream).convert('RGBA')
        img_np = np.array(img)
        cropped = crop_to_ratio(img_np, w_ratio, h_ratio)
        result = Image.fromarray(cropped)
        buf = io.BytesIO()
        result.save(buf, format='PNG')
        buf.seek(0)
        logger.info('Cropped image to ratio %d:%d', w_ratio, h_ratio)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        logger.exception('crop error')
        return jsonify({'error': 'Failed to crop image'}), 500





if __name__ == '__main__':
    logger.info('Starting Image Processing API backend...')
    try:
        app.run(debug=True)
        logger.info('Backend started successfully.')
    except Exception as e:
        logger.exception('Backend failed to start.')