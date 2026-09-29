from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from model import detect_image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)


@app.route("/api/health")
def health():
    return jsonify({"success": True, "message": "AQUASCAN AI is running"})


@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"success": False, "message": "No image received"}), 400

    image = request.files["image"]
    if image.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    safe_name = os.path.basename(image.filename)
    image_path = os.path.join(UPLOAD_FOLDER, safe_name)
    image.save(image_path)

    try:
        detections = detect_image(image_path)
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": "AI detection failed",
            "error": str(exc)
        }), 500

    return jsonify({
        "success": True,
        "detections": detections,
        "message": "Sonar image uploaded successfully"
    })


@app.route("/gallery", methods=["GET"])
def gallery():
    files = os.listdir(UPLOAD_FOLDER)
    images = [
        file for file in files
        if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]
    return jsonify({"success": True, "images": images})


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:path>")
def frontend(path):
    file_path = os.path.join(BASE_DIR, path)
    if os.path.isfile(file_path):
        return send_from_directory(BASE_DIR, path)
    return send_from_directory(BASE_DIR, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
