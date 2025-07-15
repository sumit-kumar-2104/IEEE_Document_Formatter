from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
import json
import shutil
from datetime import datetime
<<<<<<< HEAD
from dateutil import parser
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os, uuid, json
from datetime import datetime
from utils.parsers import parse_input_file
from utils.title_suggested import suggest_titles
from utils.llm_formatter import generate_ieee_markdown
from utils.latex_formatter import generate_pdf_from_data
=======
from pymongo import MongoClient
import bcrypt
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de
from werkzeug.utils import secure_filename


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

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'dev-key-93c1745e3f2342c9bfa814bcdf2fd819'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
<<<<<<< HEAD

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
=======
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

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
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de

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
<<<<<<< HEAD
        "uploads": []
    })

    return jsonify({"success": True, "message": "Signup successful", "redirect": "/login.html"})

=======
        "uploads": [],
        "created_at": datetime.utcnow()
    })

    return jsonify({"success": True, "message": "Signup successful", "redirect": "/login.html"})
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

<<<<<<< HEAD
    user = users_collection.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        session['user'] = user['email']
        return jsonify({'success': True, 'message': 'Login successful', 'redirect': '/dashboard'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))




# ========================
# 🌐 Page Routes
# ========================
=======
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
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de
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
def dashboard():
<<<<<<< HEAD
    if 'user' not in session:
        return redirect(url_for('login_page'))

    user = users_collection.find_one({"email": session["user"]})
    uploads = user.get("uploads", [])
=======
    user = users_collection.find_one({"email": session['user']})
    uploads = sorted(user.get('uploads', []), key=lambda x: x.get('parsed_on', datetime.min), reverse=True)
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de
    return render_template('dashboard.html', uploads=uploads)

@app.route('/index.html')
def index():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')

<<<<<<< HEAD
# ========================
# 📤 File Upload + Parsing
# ========================
=======
# ==============================
# 📤 Upload & Parse Document
# ==============================
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login_page'))

<<<<<<< HEAD
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    # 🧾 Save uploaded file temporarily
    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    uploaded_file.save(file_path)

    try:
        # 🧠 Parse the file (should extract text + image paths)
        parsed_data = parse_input_file(file_path)
        if not parsed_data or "error" in parsed_data:
            return jsonify({"error": parsed_data.get("error", "Unknown error")}), 400

        # 🎯 Title suggestion
        titles = suggest_titles(parsed_data)
        temp_id = str(uuid.uuid4())

        # 📁 Create static image folder for this document
        image_folder = os.path.join("static", "images", temp_id)
        os.makedirs(image_folder, exist_ok=True)

        # ✅ Ensure all image paths are valid and convert to PNG
        valid_images = []
        for img in parsed_data.get("images", []):
            original_path = img.get("path")
            if not original_path or not os.path.exists(original_path):
                continue

            try:
                ext = os.path.splitext(original_path)[1].lower()
                basename = os.path.splitext(os.path.basename(original_path))[0]
                new_path = os.path.join(image_folder, f"{basename}.png")

                # Always convert using Pillow to ensure compatibility
                with Image.open(original_path) as im:
                    im.convert("RGB").save(new_path, "PNG")

                img["path"] = f"/static/images/{temp_id}/{basename}.png"
                valid_images.append(img)

            except Exception as e:
                print(f"[SKIP] Failed to process image {original_path}: {e}")
                continue

        parsed_data["images"] = valid_images

        # 💾 Save parsed data to temp storage
        temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)

        # 🔐 Save session token
        session['temp_id'] = temp_id

        # 📚 Log upload in DB
        email = session['user']
        uploads_entry = {
            "file_name": uploaded_file.filename,
            "temp_id": temp_id,
            "parsed_on": datetime.utcnow(),
            "title": titles[0] if titles else "Untitled"
        }

        users_collection.update_one(
            {"email": email},
            {"$push": {"uploads": uploads_entry}}
        )
=======
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Dummy Parsed Data (Replace with real parser)
    parsed_data = {
        "title": "Sample IEEE Document",
        "abstract": "This is a sample abstract...",
        "keywords": "IEEE, Formatting, Template",
        "sections": [{
            "heading": "Introduction",
            "content": "Sample introduction content...",
            "images": []
        }],
        "references": ["1. Author, 'Title', Journal, 2023"]
    }

    temp_id = str(uuid.uuid4())
    session['temp_id'] = temp_id

    with open(os.path.join(TEMP_FOLDER, f"{temp_id}.json"), "w") as f:
        json.dump(parsed_data, f, indent=2)

    users_collection.update_one(
        {"email": session['user']},
        {"$push": {"uploads": {
            "file_name": filename,
            "temp_id": temp_id,
            "parsed_on": datetime.utcnow(),
            "title": parsed_data.get("title", "Untitled Document")
        }}}
    )
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de

    return redirect(url_for('editor'))

<<<<<<< HEAD
    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ========================
# 📝 Editor View
# ========================
=======
# ==============================
# 📝 Editor View
# ==============================
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de
@app.route('/editor')
def editor():
    if 'user' not in session:
        return redirect(url_for('login_page'))

    temp_id = session.get('temp_id')
    if not temp_id:
<<<<<<< HEAD
        return "Missing session data", 400

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
        return "Parsed document not found", 400
=======
        flash('No document in session', 'error')
        return redirect(url_for('index'))

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
        flash('Document not found', 'error')
        return redirect(url_for('index'))
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de

    with open(temp_path) as f:
        parsed_data = json.load(f)

<<<<<<< HEAD
    return render_template('editor.html', parsed=parsed_data)

# ========================
# 🔁 Resume Editing
# ========================
=======
    return render_template('editor.html', parsed=parsed_data, from_dashboard=request.args.get('from_dashboard'))

# ==============================
# 🔁 Resume Editing
# ==============================
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de
@app.route('/resume/<temp_id>')
def resume(temp_id):
<<<<<<< HEAD
    if 'user' not in session:
        return redirect(url_for('login_page'))
=======
    user = users_collection.find_one({"email": session['user'], "uploads.temp_id": temp_id}, {"uploads.$": 1})
    if not user:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard'))
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
<<<<<<< HEAD
        users_collection.update_one(
            {"email": session["user"]},
            {"$pull": {"uploads": {"temp_id": temp_id}}}
        )
        user = users_collection.find_one({"email": session["user"]})
        uploads = user.get("uploads", [])
        return render_template("dashboard.html", uploads=uploads, error="Parsed file not found. Please upload again.")

    session['temp_id'] = temp_id
    with open(temp_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    markdown = parsed_data.get("edited_markdown")
    return render_template("editor.html", parsed=parsed_data, saved_markdown=markdown, from_dashboard=True)

# ========================
# 📄 Markdown + PDF Gen
# ========================
@app.route('/generate_ieee', methods=['POST'])
def generate_ieee():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    temp_id = session.get('temp_id')
    if not temp_id:
        return jsonify({"error": "Missing parsed document data"}), 400

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
        return jsonify({"error": "Parsed document not found"}), 400
=======
        users_collection.update_one({"email": session['user']}, {"$pull": {"uploads": {"temp_id": temp_id}}})
        flash('Document removed from history', 'error')
        return redirect(url_for('dashboard'))
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de

    with open(temp_path) as f:
        parsed_data = json.load(f)

<<<<<<< HEAD
    try:
        markdown = generate_ieee_markdown(parsed_data)
        return jsonify({"markdown": markdown})
    except Exception as e:
        return jsonify({"error": f"Error generating IEEE markdown: {str(e)}"}), 500


@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Save the latest edited version to temp file
    temp_id = session.get("temp_id")
    if temp_id:
        temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return jsonify({"error": f"Failed to save temp data: {str(e)}"}), 500

    # Generate the PDF
    try:
        result = generate_pdf_from_data(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

# ========================
# 🗑 Delete Upload
# ========================
@app.route('/delete_upload/<temp_id>', methods=['GET', 'POST'])
def delete_upload(temp_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))

    email = session['user']

    # Remove from MongoDB
    users_collection.update_one(
        {"email": email},
        {"$pull": {"uploads": {"temp_id": temp_id}}}
    )

    # Remove temp file
=======
    return render_template('editor.html', parsed=parsed_data, from_dashboard=True)

# ==============================
# 📄 PDF Generation (Dummy)
# ==============================
@app.route('/generate_pdf', methods=['POST'])
@login_required
def generate_pdf():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    temp_id = session.get('temp_id')
    if temp_id:
        with open(os.path.join(TEMP_FOLDER, f"{temp_id}.json"), "w") as f:
            json.dump(data, f, indent=2)

    pdf_filename = f"{temp_id}.pdf"
    with open(os.path.join(STATIC_FOLDER, 'pdfs', pdf_filename), 'wb') as f:
        f.write(b'%PDF-1.4\n%% Dummy PDF content')

    return jsonify({"success": True, "pdf_url": f"/static/pdfs/{pdf_filename}?{datetime.now().timestamp()}"})

# ==============================
# 🗑 Delete Upload
# ==============================
@app.route('/delete_upload/<temp_id>', methods=['POST'])
@login_required
def delete_upload(temp_id):
    result = users_collection.update_one({"email": session['user']}, {"$pull": {"uploads": {"temp_id": temp_id}}})
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de
    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    pdf_path = os.path.join(STATIC_FOLDER, 'pdfs', f"{temp_id}.pdf")

    if os.path.exists(temp_path):
        os.remove(temp_path)
<<<<<<< HEAD

    return redirect(url_for("dashboard"))
=======
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de


<<<<<<< HEAD
=======
# ==============================
# 🖼️ Static Files
# ==============================
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de

# ==============================
# 🚀 Run Server
<<<<<<< HEAD
# ===========================================
if __name__ == "__main__":
    app.run(debug=True)
=======
# ==============================
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
>>>>>>> f46904fe22f2cfeb3c3668920e76ed841f8446de
