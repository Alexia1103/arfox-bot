from flask import Flask, request, jsonify, render_template
from gmail_service import obtener_correos_netflix

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

    bandeja = obtener_correos_netflix(correo)
    return render_template("inbox.html", bandeja=bandeja, destinatario=correo)

if __name__ == "__main__":
    app.run(debug=True)
