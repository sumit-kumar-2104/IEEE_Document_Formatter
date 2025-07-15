from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory
import os
import uuid
import json
import shutil
import bcrypt
from pymongo import MongoClient
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps
from PIL import Image

# ===========================================
# 🔗 MongoDB setup
# ===========================================
client = MongoClient("mongodb://localhost:27017/")
db = client['authdb']
users_collection = db['users']

# ===========================================
# 🔧 Flask setup
# ===========================================
UPLOAD_FOLDER = "uploads"
TEMP_FOLDER = "temp_data"
STATIC_FOLDER = "static"

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(os.path.join(STATIC_FOLDER, 'pdfs'), exist_ok=True)

# ===========================================
# 🔐 Authentication Decorator
# ===========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# ===========================================
# 🔐 Authentication routes
# ===========================================
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')

    if not all([name, email, password, phone]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({"success": False, "message": "User already exists"}), 400

    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password,
            "phone": phone,
            "uploads": [],
            "created_at": datetime.utcnow()
        })
        return jsonify({
            "success": True, 
            "message": "Signup successful", 
            "redirect": "/login.html"
        })
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"Registration failed: {str(e)}"
        }), 500
    from flask import jsonify, request, session
import bcrypt

from flask import jsonify, request, session
import bcrypt
from bson.objectid import ObjectId  # For handling MongoDB's _id

@app.route('/login', methods=['POST'])
def login():
    # 1. Check if request has JSON data
    if not request.is_json:
        return jsonify({
            'success': False,
            'message': 'Request must be JSON'
        }), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 2. Validate email and password (basic checks)
    if not email or not isinstance(email, str):
        return jsonify({
            'success': False,
            'message': 'Valid email is required'
        }), 400

    if not password or not isinstance(password, str):
        return jsonify({
            'success': False,
            'message': 'Valid password is required'
        }), 400

    # 3. Find user in MongoDB
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({
            'success': False,
            'message': 'Invalid email or password'  # Generic message for security
        }), 401

    # 4. Verify password (critical step)
    try:
        # Ensure stored password is bytes (MongoDB might return str)
        stored_password = user['password']
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')

        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
    except Exception as e:
        print(f"Password check failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Authentication error'
        }), 500

    # 5. Set session data (avoid sensitive info)
    session['user_id'] = str(user['_id'])  # Convert ObjectId to string
    session['username'] = user.get('name', email.split('@')[0])

    # 6. Success response
    return jsonify({
        'success': True,
        'message': 'Logged in successfully',
        'redirect': '/dashboard',
        'user': {  # Optional: Safe user data for frontend
            'name': session['username'],
            'email': email
        }
    })
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login_page'))

# ===========================================
# 🌐 Page Routes
# ===========================================
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
    user = users_collection.find_one({"email": session["user"]})
    uploads = sorted(
        user.get("uploads", []),
        key=lambda x: x.get('parsed_on', datetime.min),
        reverse=True
    )
    return render_template('dashboard.html', uploads=uploads)

@app.route('/index.html')
@login_required
def index():
    return render_template('index.html')

# ===========================================
# 📤 File Upload + Parsing
# ===========================================
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(request.url)

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    try:
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)

        # Parse the file (replace with actual parser)
        parsed_data = {
            "title": "Sample IEEE Document",
            "abstract": "This is a sample abstract...",
            "keywords": "IEEE, Formatting, Template",
            "sections": [
                {
                    "heading": "Introduction",
                    "content": "Sample introduction content...",
                    "images": []
                }
            ],
            "references": ["1. Author, 'Title', Journal, 2023"]
        }

        temp_id = str(uuid.uuid4())
        session['temp_id'] = temp_id

        temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)

        users_collection.update_one(
            {"email": session['user']},
            {"$push": {"uploads": {
                "file_name": filename,
                "temp_id": temp_id,
                "parsed_on": datetime.utcnow(),
                "title": parsed_data.get("title", "Untitled Document")
            }}}
        )

        return redirect(url_for("editor"))

    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('index'))

# ===========================================
# 📝 Editor View
# ===========================================
@app.route('/editor')
@login_required
def editor():
    temp_id = session.get('temp_id')
    if not temp_id:
        flash('No document session found', 'error')
        return redirect(url_for('index'))

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
        flash('Document data not found', 'error')
        return redirect(url_for('index'))

    with open(temp_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    return render_template('editor.html', 
                         parsed=parsed_data,
                         from_dashboard=request.args.get('from_dashboard'))

# ===========================================
# 🔁 Resume Editing
# ===========================================
@app.route('/resume/<temp_id>')
@login_required
def resume(temp_id):
    user = users_collection.find_one(
        {"email": session["user"], "uploads.temp_id": temp_id},
        {"uploads.$": 1}
    )
    
    if not user:
        flash('Document not found in your history', 'error')
        return redirect(url_for('dashboard'))

    session['temp_id'] = temp_id
    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    
    if not os.path.exists(temp_path):
        users_collection.update_one(
            {"email": session["user"]},
            {"$pull": {"uploads": {"temp_id": temp_id}}}
        )
        flash('Document data not found', 'error')
        return redirect(url_for('dashboard'))

    with open(temp_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    return render_template("editor.html", 
                         parsed=parsed_data,
                         from_dashboard=True)

# ===========================================
# 📄 PDF Generation
# ===========================================
@app.route('/generate_pdf', methods=['POST'])
@login_required
def generate_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        temp_id = session.get("temp_id")
        if temp_id:
            temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        # Generate PDF (replace with actual PDF generation)
        pdf_filename = f"{temp_id}.pdf"
        pdf_path = os.path.join(STATIC_FOLDER, 'pdfs', pdf_filename)
        
        # Create dummy PDF (replace with actual PDF generation)
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%%Dummy PDF content')

        return jsonify({
            "success": True,
            "pdf_url": f"/static/pdfs/{pdf_filename}?{datetime.now().timestamp()}"
        })

    except Exception as e:
        return jsonify({
            "error": f"PDF generation failed: {str(e)}"
        }), 500

# ===========================================
# 🗑 Delete Upload
# ===========================================
@app.route('/delete_upload/<temp_id>', methods=['POST'])
@login_required
def delete_upload(temp_id):
    result = users_collection.update_one(
        {"email": session["user"], "uploads.temp_id": temp_id},
        {"$pull": {"uploads": {"temp_id": temp_id}}}
    )
    
    if result.modified_count == 0:
        flash('Document not found or not owned by you', 'error')
        return redirect(url_for('dashboard'))

    # Remove temp file
    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Remove PDF if exists
    pdf_path = os.path.join(STATIC_FOLDER, 'pdfs', f"{temp_id}.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    flash('Document deleted successfully', 'success')
    return redirect(url_for('dashboard'))

# ===========================================
# 🖼️ Serve Static Files
# ===========================================
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

# ===========================================
# 🚀 Run Server
# ===========================================
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)