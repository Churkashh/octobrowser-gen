import re
import time
import random
import string
import tls_client

from loguru import logger

from additional.constants import PROXIES, BASIC_PASSWORD, PROXYLESS, MAIL_SUBJECT, MAIL_TIMEOUT


class MailTMClient:
    def __init__(self):
        self.session = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True)
        if not PROXYLESS:
            self.session.proxies = f"http://{random.choice(PROXIES)}"
        
        self.token = None
        self.account_id = None
        self.email = None
        self.password = BASIC_PASSWORD

    def _generate_email(self, domains: list[str]):
        prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"{prefix}@{random.choice(domains)}"

    def create_account(self):
        try:
            resp = self.session.get("https://api.mail.tm/domains")
            domains = [d["domain"] for d in resp.json().get("hydra:member", [])]
            if not domains:
                logger.critical("Нет доступных MailTM доменов.")
                return False

            self.email = self._generate_email(domains)

            account_payload = {
                "address": self.email,
                "password": self.password
            }
            create_resp = self.session.post("https://api.mail.tm/accounts", json=account_payload)
            if create_resp.status_code not in [200, 201]:
                logger.error(f"Ошибка создания почты MailTM ({resp.status_code}) -> {resp.text}")
                return False

            token_resp = self.session.post("https://api.mail.tm/token", json=account_payload)
            if token_resp.status_code == 200:
                data = token_resp.json()
                self.token = data.get("token")
                self.account_id = data.get("id")
                return self.email
            
            return False
        except Exception as exc:
            logger.exception(exc)
            return False

    def get_mail(self):
        if not self.token:
            logger.error("Не найден Bearer токен (MailTmClient)")
            return False

        headers = {"Authorization": f"Bearer {self.token}"}
        start_time = time.time()
        while time.time() - start_time < MAIL_TIMEOUT:
            try:
                response = self.session.get(
                    "https://api.mail.tm/messages",
                    headers=headers,
                )
                if response.status_code == 200:
                    messages = response.json().get("hydra:member", [])
                    for msg in messages:
                        if msg.get("subject") == MAIL_SUBJECT:
                            return self._get_message(msg["id"], headers)
                time.sleep(3)
            except Exception as exc:
                logger.exception(exc)
                return False
        return False

    def _get_message(self, msg_id: str, headers: dict):
        try:
            response = self.session.get(
                f"https://api.mail.tm/messages/{msg_id}",
                headers=headers,
            )
            if response.status_code == 200:
                text = response.json().get("text", "")

                match = re.search(r"https://app\.octobrowser\.net/api/v2/auth/confirm/[^\]\s]+", text)
                if match:
                    return match.group(0)
                else:
                    return False
            return False
        except Exception as exc:
            logger.exception(exc)
            return False