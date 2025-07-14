from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import io
from PIL import Image
import rembg
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app.config["MONGO_URI"] = "mongodb://localhost:27017/your_db_name"
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app = Flask(__name__)
CORS(app)

# Xoá nền ảnh
def remove_bg(image_bytes):
    return rembg.remove(image_bytes)

# Đổi kích thước ảnh theo px
def resize_image(image, width, height):
    return cv2.resize(image, (width, height))

# Cắt ảnh theo tỉ lệ
# ratio: tuple (w, h)
def crop_to_ratio(image, ratio):
    h, w = image.shape[:2]
    target_w = w
    target_h = int(w * ratio[1] / ratio[0])
    if target_h > h:
        target_h = h
        target_w = int(h * ratio[0] / ratio[1])
    x = (w - target_w) // 2
    y = (h - target_h) // 2
    return image[y:y+target_h, x:x+target_w]

@app.route('/remove-bg', methods=['POST'])
def api_remove_bg():
    file = request.files['image']
    result = remove_bg(file.read())
    return send_file(io.BytesIO(result), mimetype='image/png')

@app.route('/resize', methods=['POST'])
def api_resize():
    file = request.files['image']
    width = int(request.form['width'])
    height = int(request.form['height'])
    img = Image.open(file.stream).convert('RGBA')
    img_np = np.array(img)
    resized = resize_image(img_np, width, height)
    result = Image.fromarray(resized)
    buf = io.BytesIO()
    result.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/crop', methods=['POST'])
def api_crop():
    file = request.files['image']
    ratio = request.form['ratio'] # e.g. '3:3' or '9:16'
    w, h = map(int, ratio.split(':'))
    img = Image.open(file.stream).convert('RGBA')
    img_np = np.array(img)
    cropped = crop_to_ratio(img_np, (w, h))
    result = Image.fromarray(cropped)
    buf = io.BytesIO()
    result.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/')
def index():
    return jsonify({'message': 'Image Processing API'})

if __name__ == '__main__':
    app.run(debug=True)
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'msg': 'Email đã tồn tại'}), 400
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    mongo.db.users.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed_pw
    })
    return jsonify({'msg': 'Đăng ký thành công'}), 201
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = mongo.db.users.find_one({'email': data['email']})
    if user and bcrypt.check_password_hash(user['password'], data['password']):
        access_token = create_access_token(identity=user['email'])
        return jsonify(access_token=access_token)
    return jsonify({'msg': 'Sai tài khoản hoặc mật khẩu'}), 401