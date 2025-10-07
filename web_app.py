import os
import json
from flask import Flask, render_template, request, jsonify
from detection_utils import detect_image_status


app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/detect")
def detect():
    # Opción 1: botón de ejemplos
    sample = request.form.get("sample")
    if sample in {"gato1", "gato2"}:
        image_filename = f"{sample}.png"
        image_path = os.path.join(os.path.dirname(__file__), image_filename)
        return jsonify(detect_image_status(image_path))

    # Opción 2: archivo subido
    file = request.files.get("file")
    if file and file.filename:
        temp_path = os.path.join(os.path.dirname(__file__), f"_upload_{file.filename}")
        file.save(temp_path)
        try:
            result = detect_image_status(temp_path)
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return jsonify(result)

    return jsonify({"error": "No se proporcionó imagen"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


