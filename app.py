from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
import json
import bcrypt
from pymongo import MongoClient

# ===========================================
# 🔗 MongoDB setup using PyMongo
# ===========================================
# client = MongoClient("mongodb+srv://sumitdiwakar476:aITGchpZ4hjllOLp@cluster0.zaeuevf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient("mongodb://localhost:27017/")
db = client['authdb']
users_collection = db['users']

# ===========================================
# 🔗 Folders setup
# ===========================================
UPLOAD_FOLDER = "uploads"
TEMP_FOLDER = "temp_data"

app = Flask(__name__)
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
        "phone": phone
    })

    return jsonify({"success": True, "message": "Signup successful", "redirect": "/login.html"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({"success": False, "message": "User not found"})

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['user'] = str(user['_id'])
        return jsonify({"success": True, "message": "Login successful", "redirect": "/dashboard"})
    else:
        return jsonify({"success": False, "message": "Incorrect password"})

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to login page
    return redirect(url_for('login_page'))

# ===========================================
# 🏠 Page routes
# ===========================================

@app.route('/')
def home():
    # Redirect to login page by default
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
    return render_template('dashboard.html')

@app.route('/index.html')
def index():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')

# ===========================================
# 📤 Upload route
# ===========================================

from utils.parsers import parse_input_file
from utils.title_suggested import suggest_titles
from utils.llm_formatter import generate_ieee_markdown
from utils.latex_formatter import generate_pdf_from_data

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login_page'))

    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
    uploaded_file.save(file_path)

    try:
        parsed_data = parse_input_file(file_path)
        if not parsed_data or "error" in parsed_data:
            return jsonify({"error": parsed_data.get("error", "Unknown error")}), 400

        titles = suggest_titles(parsed_data)

        # Store parsed data in temp file
        temp_id = str(uuid.uuid4())
        temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)

        session['temp_id'] = temp_id

        return jsonify({
            "parsed": parsed_data,
            "suggested_titles": titles
        })
    except Exception as e:
        print("Upload error:", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ===========================================
# 📝 Editor route
# ===========================================

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

# ===========================================
# 📝 Generate IEEE markdown
# ===========================================

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

# ===========================================
# 📄 Generate PDF
# ===========================================

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    result = generate_pdf_from_data(data)
    return jsonify(result)

# ===========================================
# 🚀 Run server
# ===========================================

if __name__ == "__main__":
    app.run(debug=True)
