from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
import json
import shutil
import bcrypt
from pymongo import MongoClient
from datetime import datetime
from dateutil import parser
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os, uuid, json
from datetime import datetime
from utils.parsers import parse_input_file
from utils.title_suggested import suggest_titles
from utils.llm_formatter import generate_ieee_markdown
from utils.latex_formatter import generate_pdf_from_data
from werkzeug.utils import secure_filename


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

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'dev-key-93c1745e3f2342c9bfa814bcdf2fd819'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

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

    if users_collection.find_one({'email': email}):
        return jsonify({"success": False, "message": "User already exists"})

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password,
        "phone": phone,
        "uploads": []
    })

    return jsonify({"success": True, "message": "Signup successful", "redirect": "/login.html"})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

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
    if 'user' not in session:
        return redirect(url_for('login_page'))

    user = users_collection.find_one({"email": session["user"]})
    uploads = user.get("uploads", [])
    return render_template('dashboard.html', uploads=uploads)

@app.route('/index.html')
def index():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')

# ========================
# 📤 File Upload + Parsing
# ========================
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login_page'))

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

        return redirect(url_for("editor"))

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ========================
# 📝 Editor View
# ========================
@app.route('/editor')
def editor():
    if 'user' not in session:
        return redirect(url_for('login_page'))

    temp_id = session.get('temp_id')
    if not temp_id:
        return "Missing session data", 400

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
        return "Parsed document not found", 400

    with open(temp_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    return render_template('editor.html', parsed=parsed_data)

# ========================
# 🔁 Resume Editing
# ========================
@app.route('/resume/<temp_id>')
def resume(temp_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
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

    with open(temp_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

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
    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return redirect(url_for("dashboard"))



# ===========================================
# 🚀 Run Server
# ===========================================
if __name__ == "__main__":
    app.run(debug=True)
