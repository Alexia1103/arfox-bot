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

    try:
        # 👉 AQUÍ va el try
        bandeja = obtener_correos_netflix(correo)

        return render_template(
            "inbox.html",
            bandeja=bandeja,
            destinatario=correo
        )

    except Exception as e:
        # 👉 Evita que Render tire 500
        print("IMAP ERROR:", e)

        return render_template(
            "error.html",
            mensaje="No se pudo leer el correo en este momento. Intenta nuevamente."
        ), 503

# Ruta opcional para volver al index desde inbox
@app.route("/volver_index")
def volver_index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
