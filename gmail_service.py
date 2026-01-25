import os
import re
from imapclient import IMAPClient
import pyzmail
from datetime import datetime

IMAP_HOST = "imap.gmail.com"


def obtener_correos_netflix(destinatario):
    bandeja = []

    with IMAPClient(IMAP_HOST, ssl=True) as server:
        server.login(
            os.getenv("EMAIL_USER"),
            os.getenv("EMAIL_APP_PASSWORD")
        )

        server.select_folder("INBOX")

        # solo correos no leídos de Netflix
        mensajes = server.search([
            "UNSEEN",
            "FROM", "@netflix.com",
            "TO", destinatario
        ])

        for uid, data in server.fetch(mensajes, ["RFC822"]).items():
            msg = pyzmail.PyzMessage.factory(data[b"RFC822"])

            subject = msg.get_subject() or ""
            from_email = msg.get_addresses("from")[0][1] if msg.get_addresses("from") else ""

            cuerpo = ""
            if msg.html_part:
                cuerpo = msg.html_part.get_payload().decode(
                    msg.html_part.charset or "utf-8",
                    errors="ignore"
                )
            elif msg.text_part:
                cuerpo = msg.text_part.get_payload().decode(
                    msg.text_part.charset or "utf-8",
                    errors="ignore"
                )

            match = re.search(r"\b\d{6}\b", cuerpo)
            codigo = match.group(0) if match else None

            bandeja.append({
                "remitente": from_email,
                "asunto": subject,
                "html": cuerpo,
                "codigo": codigo
            })

            # marcar como leído
            server.add_flags(uid, [b"\\Seen"])

    return bandeja

