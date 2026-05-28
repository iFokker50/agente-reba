from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from agent_reba import analizar_imagen_reba
import os
import uuid


load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "image" not in request.files:
            return jsonify({
                "success": False,
                "message": "No se envió ninguna imagen."
            }), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({
                "success": False,
                "message": "No se seleccionó ningún archivo."
            }), 400

        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "message": "Formato no permitido. Usa PNG, JPG, JPEG o WEBP."
            }), 400

        body_side = request.form.get("body_side", "izquierdo").lower().strip()

        if body_side not in ["izquierdo", "derecho"]:
            return jsonify({
                "success": False,
                "message": "Lado no válido. Debe ser izquierdo o derecho."
            }), 400

        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{extension}"

        image_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(image_path)

        reporte = analizar_imagen_reba(image_path, body_side)

        return jsonify({
            "success": True,
            "message": "Análisis generado correctamente.",
            "report": reporte
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=False)
