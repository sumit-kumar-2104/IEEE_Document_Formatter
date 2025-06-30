from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
import json
from utils.parsers import parse_input_file
from utils.title_suggested import suggest_titles
from utils.llm_formatter import generate_ieee_markdown
from utils.latex_formatter import generate_pdf_from_data

app = Flask(__name__)
app.secret_key = 'dev-key-93c1745e3f2342c9bfa814bcdf2fd819'

UPLOAD_FOLDER = "uploads"
TEMP_FOLDER = "temp_data"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
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

@app.route('/editor')
def editor():
    temp_id = session.get('temp_id')
    if not temp_id:
        return "Missing session data", 400

    temp_path = os.path.join(TEMP_FOLDER, f"{temp_id}.json")
    if not os.path.exists(temp_path):
        return "Parsed document not found", 400

    with open(temp_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    return render_template('editor.html', parsed=parsed_data)


@app.route('/generate_ieee', methods=['POST'])
def generate_ieee():
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
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    result = generate_pdf_from_data(data)
    return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True)
