from flask import Flask, request, jsonify, send_file
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os
import io
import uuid

from datetime import datetime, timedelta

from models import db, User, File
from cryptography.fernet import Fernet

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

app = Flask(__name__)

# ---------------- CONFIG ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- INIT ----------------
db.init_app(app)
bcrypt = Bcrypt(app)
CORS(app)
jwt = JWTManager(app)

# ---------------- ENCRYPTION ----------------
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_file(data):
    return cipher.encrypt(data)

def decrypt_file(data):
    return cipher.decrypt(data)

# ---------------- DB CREATE ----------------
with app.app_context():
    db.create_all()

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return "Backend running!"

# ---------------- AUTH ----------------

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"})

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = create_access_token(identity=user.username)
        return jsonify({
            "message": "Login successful",
            "token": token
        })

    return jsonify({"message": "Invalid username or password"})

# ---------------- FILE UPLOAD ----------------

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if 'file' not in request.files:
        return jsonify({"message": "No file provided"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"message": "No selected file"})

    encrypted_data = encrypt_file(file.read())

    stored_filename = str(uuid.uuid4())
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)

    with open(filepath, 'wb') as f:
        f.write(encrypted_data)

    expiry = datetime.utcnow() + timedelta(minutes=10)

    new_file = File(
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_id=str(uuid.uuid4()),
        user_id=user.id,
        expiry_time=expiry
    )

    db.session.add(new_file)
    db.session.commit()

    return jsonify({
        "message": "File uploaded successfully",
        "file_id": new_file.file_id,
        "download_link": f"http://127.0.0.1:5000/download/{new_file.file_id}",
        "expires_at": str(expiry)
    })

# ---------------- DASHBOARD API ----------------

@app.route('/myfiles', methods=['GET'])
@jwt_required()
def get_my_files():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    files = File.query.filter_by(user_id=user.id).all()

    file_list = []

    for file in files:
        file_list.append({
            "filename": file.original_filename,
            "file_id": file.file_id,
            "expiry": str(file.expiry_time),
            "download_link": f"http://127.0.0.1:5000/download/{file.file_id}"
        })

    return jsonify(file_list)

# ---------------- FILE DOWNLOAD ----------------

@app.route('/download/<file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    file = File.query.filter_by(file_id=file_id).first()

    if not file:
        return jsonify({"message": "File not found"})

    if file.user_id != user.id:
        return jsonify({"message": "Unauthorized access"})

    if file.expiry_time and datetime.utcnow() > file.expiry_time:
        return jsonify({"message": "File link expired"})

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.stored_filename)

    if not os.path.exists(filepath):
        return jsonify({"message": "File missing on server"})

    with open(filepath, 'rb') as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_file(encrypted_data)

    return send_file(
        io.BytesIO(decrypted_data),
        download_name=file.original_filename,
        as_attachment=True
    )

# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(debug=True)