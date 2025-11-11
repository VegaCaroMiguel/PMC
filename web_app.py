import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from detection_utils import detect_image_status_c2pa, mark_image_as_ai
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/test-images")
def test_images():
    """Página de prueba para verificar carga de imágenes"""
    return render_template("test_images.html")


@app.post("/mark-as-ai")
def mark_as_ai():
    """Endpoint para marcar una imagen como generada por IA"""
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "No se proporcionó imagen"}), 400
    
    # Guardar archivo temporalmente
    filename = secure_filename(file.filename)
    temp_path = os.path.join(UPLOAD_FOLDER, f"mark_{filename}")
    file.save(temp_path)
    
    try:
        # Obtener parámetros opcionales
        prompt = request.form.get("prompt", "Imagen marcada manualmente")
        model = request.form.get("model", "Manual Marking System")
        author = request.form.get("author", "User")
        
        # Marcar imagen
        result = mark_image_as_ai(temp_path, prompt, model, author)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.post("/detect")
def detect():
    """Endpoint para detectar si una imagen es generada por IA"""
    # Opción 1: botón de ejemplos
    sample = request.form.get("sample")
    if sample in {"gato1", "gato2", "gato3"}:
        # Buscar en carpeta uploads
        image_path = os.path.join(UPLOAD_FOLDER, f"{sample}.jpg")
        if os.path.exists(image_path):
            return jsonify(detect_image_status_c2pa(image_path))
        # Fallback: buscar en raíz con diferentes extensiones
        for ext in ['.png', '.jpg', '.jpeg']:
            image_path = os.path.join(os.path.dirname(__file__), f"{sample}{ext}")
            if os.path.exists(image_path):
                return jsonify(detect_image_status_c2pa(image_path))
        return jsonify({"error": f"Imagen {sample} no encontrada"}), 404

    # Opción 2: archivo subido
    file = request.files.get("file")
    if file and file.filename:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"detect_{filename}")
        file.save(temp_path)
        try:
            result = detect_image_status_c2pa(temp_path)
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return jsonify(result)

    return jsonify({"error": "No se proporcionó imagen"}), 400


@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    """Servir archivos desde la carpeta uploads"""
    return send_from_directory(UPLOAD_FOLDER, filename, mimetype='image/jpeg')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


