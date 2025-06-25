from flask import Flask, render_template, request, jsonify
import os
from utils.parsers import parse_input_file
from utils.title_suggester import suggest_titles

UPLOAD_FOLDER = "uploads"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        if "error" in parsed_data:
            return jsonify({"error": parsed_data["error"]}), 400

        titles = suggest_titles(parsed_data)
        return jsonify({
            "parsed": parsed_data,
            "suggested_titles": titles
        })
    except Exception as e:
        print("Upload error:", str(e))
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
