# wrapper_cloudapi.py
import os
from dotenv import load_dotenv
import requests
import logging

# Configuração do logger
logger = logging.getLogger("whatsapp")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler("whatsapp.log", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class WhatsAppCloudAPI:
    def __init__(self, phone_number_id=None, token=None):
        load_dotenv()
        self.PHONE_NUMBER_ID = phone_number_id or os.getenv(
            "WHATSAPP_PHONE_NUMBER_ID")
        self.TOKEN = token or os.getenv("WHATSAPP_CLOUD_API_TOKEN")
        self.URL = f"https://graph.facebook.com/v20.0/{self.PHONE_NUMBER_ID}/messages"

        self.headers = {
            "Authorization": f"Bearer {self.TOKEN}",
            "Content-Type": "application/json"
        }

    # -------------------------
    # ENVIO DE TEXTO NORMAL
    # -------------------------
    def send_text(self, number: str, message: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "text",
            "text": {"body": message}
        }

        logger.debug(f"Enviando mensagem de texto: {payload}")

        response = requests.post(self.URL, json=payload, headers=self.headers)

        logger.info(f"Envio texto → {number} | Status {response.status_code}")
        logger.debug(f"Resposta API: {response.text}")

        return response.json(), response.status_code

    # -------------------------
    # ENVIO DE TEMPLATE OFICIAL (HSM)
    # -------------------------
    def send_template(self, number: str, template_name: str, language="pt_BR", components=None):
        payload = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
            }
        }

        if components:
            payload["template"]["components"] = components

        logger.debug(f"Enviando template: {payload}")

        response = requests.post(self.URL, json=payload, headers=self.headers)

        logger.info(
            f"Envio template → {number} | Status {response.status_code}")
        logger.debug(f"Resposta API: {response.text}")

        return response.json(), response.status_code
