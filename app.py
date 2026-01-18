from flask import Flask, request, jsonify, render_template
from gmail_service import obtener_correos_netflix
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/inbox", methods=["POST"])
def inbox():
    data = request.form
    correo = data.get("correo")
    if not correo:
        return "Por favor ingresa un correo", 400

    # Obtener la bandeja filtrada por el correo ingresado
    bandeja = obtener_correos_netflix(correo)
    return render_template("inbox.html", bandeja=bandeja, destinatario=correo)

# Ruta opcional para volver al index desde inbox
@app.route("/volver_index")
def volver_index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)