from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory
import os
import uuid
import json
import shutil
from datetime import datetime
from pymongo import MongoClient
import bcrypt
from werkzeug.utils import secure_filename
from functools import wraps
from utils.parsers import parse_input_file
from utils.title_suggested import suggest_titles
from utils.llm_formatter import generate_ieee_markdown
from utils.latex_formatter import generate_pdf_from_data
from PIL import Image

# ==============================
# 🔗 MongoDB Setup
# ==============================
client = MongoClient("mongodb://localhost:27017/")
db = client['authdb']
users_collection = db['users']

# ==============================
# 🔧 Flask Setup
# ==============================
UPLOAD_FOLDER = "uploads"
TEMP_FOLDER = "temp_data"
STATIC_FOLDER = "static"

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'dev-key-93c1745e3f2342c9bfa814bcdf2fd819'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(os.path.join(STATIC_FOLDER, 'pdfs'), exist_ok=True)

# ==============================
# 🔐 Authentication Decorator
# ==============================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in first!', 'warning')
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# ==============================
# 📝 Auth Routes
# ==============================
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')

    if users_collection.find_one({'email': email}):
        return jsonify({"success": False, "message": "User already exists"})

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password,
        "phone": phone,
        "uploads": [],
        "created_at": datetime.utcnow()
    })

    return jsonify({"success": True, "message": "Signup successful", "redirect": "/login.html"})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or '@' not in email or not password:
        return jsonify({"success": False, "message": "Invalid credentials"}), 400

    user = users_collection.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    session.clear()
    session['user'] = email
    session.permanent = True

    return jsonify({
        "success": True,
        "message": "Login successful",
        "redirect": "/dashboard"
    })

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login_page'))

# ==============================
# 🌐 Page Routes
# ==============================
@app.route('/')
def home():
    return redirect(url_for('login_page'))

@app.route('/login.html')
def login_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup.html')
def signup_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = users_collection.find_one({"email": session['user']})
    uploads = sorted(user.get('uploads', []), key=lambda x: x.get('parsed_on', datetime.min), reverse=True)
    return render_template('dashboard.html', uploads=uploads)

@app.route('/index.html')
@login_required
def index():
    return render_template('index.html')

# ==============================
# 📤 Upload & Parse Document
# ==============================
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    uploaded_file.save(file_path)

    try:
        parsed_data = parse_input_file(file_path)
        if not parsed_data or "error" in parsed_data:
            return jsonify({"error": parsed_data.get("error", "Unknown error")}), 400

        titles = suggest_titles(parsed_data)
        temp_id = str(uuid.uuid4())

        image_folder = os.path.join("static", "images", temp_id)
        os.makedirs(image_folder, exist_ok=True)

        valid_images = []
        for img in parsed_data.get("images", []):
            original_path = img.get("path")
            if not original_path or not os.path.exists(original_path):
                continue

            try:
                basename = os.path.splitext(os.path.basename(original_path))[0]
                new_path = os.path.join(image_folder, f"{basename}.png")
                with Image.open(original_path) as im:
                    im.convert("RGB").save(new_path, "PNG")
                img["path"] = f"/static/images/{temp_id}/{basename}.png"
                valid_images.append(img)
            except Exception as e:
                print(f"[SKIP] Failed to process image {original_path}: {e}")

        parsed_data["images"] = valid_images

        with open(os.path.join(TEMP_FOLDER, f"{temp_id}.json"), "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)

        session['temp_id'] = temp_id

        uploads_entry = {
            "file_name": uploaded_file.filename,
            "temp_id": temp_id,
            "parsed_on": datetime.utcnow(),
            "title": titles[0] if titles else "Untitled"
        }

        users_collection.update_one(
            {"email": session['user']},
            {"$push": {"uploads": uploads_entry}}
        )

        return redirect(url_for('editor'))

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ==============================
# 📝 Editor View
# ==============================
@app.route('/editor')
@login_required
def editor():
    temp_id = session.get('temp_id')
    if not temp_id:
        flash('No document in session', 'error')
        return redirect(url_for('index'))

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
        flash('Document not found', 'error')
        return redirect(url_for('index'))

    with open(temp_path) as f:
        parsed_data = json.load(f)

    return render_template('editor.html', parsed=parsed_data, from_dashboard=request.args.get('from_dashboard'))

# ==============================
# 🔁 Resume Editing
# ==============================
@app.route('/resume/<temp_id>')
@login_required
def resume(temp_id):
    user = users_collection.find_one({"email": session['user'], "uploads.temp_id": temp_id}, {"uploads.$": 1})
    if not user:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard'))

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
        users_collection.update_one({"email": session['user']}, {"$pull": {"uploads": {"temp_id": temp_id}}})
        flash('Document removed from history', 'error')
        return redirect(url_for('dashboard'))

    with open(temp_path) as f:
        parsed_data = json.load(f)

    return render_template('editor.html', parsed=parsed_data, from_dashboard=True)

# ==============================
# 📄 Generate IEEE Markdown
# ==============================
@app.route('/generate_ieee', methods=['POST'])
@login_required
def generate_ieee():
    temp_id = session.get('temp_id')
    if not temp_id:
        return jsonify({"error": "Missing parsed document data"}), 400

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
        return jsonify({"error": "Parsed document not found"}), 400

    with open(temp_path) as f:
        parsed_data = json.load(f)

    try:
        markdown = generate_ieee_markdown(parsed_data)
        return jsonify({"markdown": markdown})
    except Exception as e:
        return jsonify({"error": f"Error generating IEEE markdown: {str(e)}"}), 500

# ==============================
# 📄 Generate PDF
# ==============================
@app.route('/generate_pdf', methods=['POST'])
@login_required
def generate_pdf():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    temp_id = session.get('temp_id')
    if temp_id:
        with open(os.path.join(TEMP_FOLDER, f"{temp_id}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    try:
        result = generate_pdf_from_data(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

# ==============================
# 🗑 Delete Upload
# ==============================
@app.route('/delete_upload/<temp_id>', methods=['POST'])
@login_required
def delete_upload(temp_id):
    users_collection.update_one({"email": session['user']}, {"$pull": {"uploads": {"temp_id": temp_id}}})

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    pdf_path = os.path.join(STATIC_FOLDER, 'pdfs', f"{temp_id}.pdf")

    if os.path.exists(temp_path):
        os.remove(temp_path)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return redirect(url_for('dashboard'))

# ==============================
# 🖼️ Static Files
# ==============================
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

# ==============================
# 🚀 Run Server
# ==============================
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
