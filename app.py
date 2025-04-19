from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

@app.route("/", methods=["GET"])
def home():
    return "Flask Server Running!"

@app.route("/detect_emotion", methods=["POST"])
def detect_emotion():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    image_bytes = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Invalid image format"}), 400

    try:
        # Convert BGR to RGB for DeepFace
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Detect Emotion using DeepFace
        result = DeepFace.analyze(img_rgb, actions=["emotion"], enforce_detection=False)
        dominant_emotion = result[0]["dominant_emotion"]

        return jsonify({"emotion": dominant_emotion})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)