import os
import json
import base64
import re
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def obtener_servicio_gmail():
    creds = None

    token_json = os.environ.get("GMAIL_TOKEN_JSON")

    if token_json:
        creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)

    # 👉 Si el token expiró, intentamos refrescarlo
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        raise Exception(
            "No hay credenciales válidas en Render. "
            "Debes generar GMAIL_TOKEN_JSON con refresh_token."
        )

    service = build("gmail", "v1", credentials=creds)
    return service



def obtener_correos_netflix(destinatario):
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

        cuerpo = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/html" and "data" in part["body"]:
                    cuerpo = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
        else:
            cuerpo = base64.urlsafe_b64decode(payload.get("body", {}).get("data", b"")).decode("utf-8")

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
