import os
import os.path
import base64
import json              # <-- IMPORTAR JSON
import re
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def obtener_servicio_gmail():
    creds = None

    # Cargar token desde variable de entorno
    token_json = os.environ.get("GMAIL_TOKEN_JSON")
    if token_json:
        creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)

    # Si no hay token válido, usar credenciales de entorno
    if not creds or not creds.valid:
        creds_env = os.environ.get("GMAIL_CREDENTIALS_JSON")
        if creds_env:
            flow = InstalledAppFlow.from_client_secrets_info(
                json.loads(creds_env), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Opcional: guardar token para uso futuro
        if creds and creds.valid:
            token_data = creds.to_json()
            # Solo local; en Render no es necesario
            # with open("token.json", "w") as f:
            #     f.write(token_data)

    service = build("gmail", "v1", credentials=creds)
    return service

def obtener_correos_netflix(destinatario):
    """
    Obtiene todos los correos de Netflix enviados al correo 'destinatario' del día de hoy,
    manteniendo el HTML completo.
    """
    service = obtener_servicio_gmail()
    hoy = datetime.now().strftime("%Y/%m/%d")
    query = f"from:@netflix.com to:{destinatario} after:{hoy}"

    resultados = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=20
    ).execute()

    mensajes = resultados.get("messages", [])
    bandeja = []

    for msg in mensajes:
        mensaje = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        payload = mensaje.get("payload", {})
        headers = payload.get("headers", [])
        subject = next((h["value"] for h in headers if h["name"]=="Subject"), "")
        from_email = next((h["value"] for h in headers if h["name"]=="From"), "")

        # Cuerpo HTML
        cuerpo = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/html" and "data" in part["body"]:
                    cuerpo = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
        else:
            cuerpo = base64.urlsafe_b64decode(payload.get("body", {}).get("data", b"")).decode("utf-8")

        # Extraemos código de 6 dígitos si aparece
        match = re.search(r"\b\d{6}\b", cuerpo)
        codigo = match.group(0) if match else None

        bandeja.append({
            "id": msg["id"],
            "remitente": from_email,
            "asunto": subject,
            "html": cuerpo,
            "codigo": codigo
        })

    return bandeja
