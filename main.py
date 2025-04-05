# github.com/Churkashh

import os
import time
import uuid
import ctypes
import random
import threading
import tls_client

from loguru import logger

from additional.constants import (
    DETAILED_EXCEPTION,
    CURRENT_VERSION,
    BASIC_PASSWORD,
    EMAIL_PROVIDER,
    PASSWORD_HASH,
    PROXY_ERR_LOG,
    PROXYLESS,
    PROMOCODE,
    PROXIES,
    THREADS,
)
from additional.mailtm import MailTMClient


account_limit = int(input("Количество аккаунтов: "))

if os.name == "nt":
    CMD = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.SetWindowLongW(CMD, -16, ctypes.windll.user32.GetWindowLongW(CMD, -16) | 0x80000)
    ctypes.windll.user32.SetLayeredWindowAttributes(CMD, 0, 235, 0x2)
    os.system("cls")
    print("# github.com/Churkashh")
    time.sleep(0.5)
    os.system("cls")

main_threads = []
file_lock = threading.Lock()

def fetch_session() -> tls_client.Session:
    """Создание tls-client сессии"""
    session = tls_client.Session(client_identifier='chrome_120', random_tls_extension_order=True)
    session.headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US',
        'Content-Type': 'application/json',
        'Origin': 'https://octobrowser.net',
        'Pragma': 'no-cache',
        'Referer': 'https://octobrowser.net/signup/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
    }
    
    if not PROXYLESS:
        session.proxies = f"http://{random.choice(PROXIES)}"
        
    return session

class Statistics:
    """Статистика софта"""
    activated = 0
    created = 0
    fails = 0

class Utils:
    @staticmethod
    def write(content, filename):
        """Запись в файл"""
        with file_lock:
            with open(filename, 'a') as file:
                file.write(f'{content}\n')
                
    @staticmethod
    def title_worker():
        """Смена названия консоли"""
        if os.name == 'nt':
            while True:
                title = f"v{CURRENT_VERSION} OctoGen (github.com/Churkashh) | Created: {Statistics.created} ~ Fails: {Statistics.fails} ~ Activated: {Statistics.activated} | github.com/Churkashh"
                ctypes.windll.kernel32.SetConsoleTitleW(title)
                time.sleep(3)


class OctoGen():
    def __init__(self):
        self.__session = fetch_session()
        self.__mailClient = None
        self.__email = ''
        self.__bearer = ''
        self.__account_uuid = ''
    
    def _send_email(self):
        """Отправка письма подтверждения"""
        while True:
            try:
                payload = {
                    'email': self.__email,
                    'password': BASIC_PASSWORD,
                    'telegram': '',
                    'cid': '',
                    'meta': {},
                }
                
                resp = self.__session.post("https://app.octobrowser.net/api/v2/auth/signup", json=payload)
                if resp.status_code != 200:
                    logger.error(f"Ошибка регистрации ({resp.status_code}) -> {resp.text}")
                    return False
                
                return True
            except Exception as exc:
                self.__handle_exception(str(exc))
                
                
    def _verify_email(self, verify_link: str):
        """Подтверждение почты"""
        while True:
            try:
                resp = self.__session.get(verify_link)
                if resp.status_code != 302:
                    logger.error(f"Ошибка подтверждения почты ({resp.status_code}) -> {resp.text}")
                    return False
                
                if "user_uuid" not in resp.headers['Location']:
                    logger.error(f"Неизвестная ошибка верификации почты -> {resp.text}")
                    return False
                
                logger.info(f"[{self.__email}] Почта подтверждена.")
                return True
            except Exception as exc:
                self.__handle_exception(str(exc))
                
    def _login(self):
        """Логин в аккаунт (запросы Desktop приложения)"""
        self.__session.headers = {
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "app.octobrowser.net",
            "User-Agent": "python-httpx/0.27.2", # интересные хедеры с приложения
        }
        
        while True:
            try:
                payload = {
                    "email": self.__email,
                    "password_hash": PASSWORD_HASH # Octo хэширует пароль для логина в приложении, используется статик значение
                }
                
                resp = self.__session.post("https://app.octobrowser.net/api/v1/auth/login", json=payload)
                if resp.status_code != 200:
                    logger.error(f"[{self.__email}] Ошибка логина в аккаунт ({resp.status_code}) -> {resp.text}")
                    return False
                
                if not resp.json()["success"]:
                    logger.error(f"[{self.__email}] Неизвестная ошибка логина в аккаунт -> {resp.text}")
                break
            except Exception as exc:
                self.__handle_exception(str(exc))
        
        self.__bearer = resp.json()["data"]["access_token"]
        self.__account_uuid = resp.json()["data"]["uuid"]
        
        self.__session.headers = { 
            "Accept": "*/*",
            "Authorization": f"Bearer {self.__bearer}",
            "cid": str(uuid.uuid4()),
            "Connection": "keep-alive",
            "hid": str(uuid.uuid1()).upper(),
            "Host": "app.octobrowser.net",
            "sid": "",
            "user-agent": "octo/win-x86_64-11/2.5.5b/135/", # хедеры для взаимодействия с другими запросами в приложении
            "X-Octo-Local-Api": "0"
        }
        
        return True
        
    def _enter_promocode(self):
        """Ввод промокода"""
        while True:
            try:
                self.__session.get("https://app.octobrowser.net/api/v1/teams/users/data") # если его не отправить - получишь ошибку невалид промокода
                
                payload = {
                    "code_value": PROMOCODE
                }

                resp = self.__session.post("https://app.octobrowser.net/api/v1/promo/code", json=payload)
                if resp.status_code != 201:
                    logger.error(f"[{self.__email}] Ошибка ввода промокода ({resp.status_code}) -> {resp.text}")
                    return False
                
                logger.success(f"[{self.__email}] Промокод {payload['code_value']} активирован.")
                return True
            except Exception as exc:
                self.__handle_exception(str(exc))
                
    def __handle_exception(self, exception: str):
        """Отработчик исключений"""
        if "Proxy" in exception:
            if PROXY_ERR_LOG:
                logger.error(f"[{self.__email}] Ошибка прокси -> {exception}")
                
            self.__session.proxies = f"http://{random.choice(PROXIES)}"
            return
        
        if DETAILED_EXCEPTION:
            logger.exception(f"Ошибка отправки запроса -> {exception}")
            
        else:
            logger.error(f"[{self.__email}] Ошибка отправки запроса -> {exception}")
            
    def _MailTM_thread(self):
        """Поток с использованием MailTM почт"""
        self.__mailClient = MailTMClient()
        self.__email = self.__mailClient.create_account()
        if not self.__email:
            return
        
        status = self._send_email()
        if not status:
            Statistics.fails += 1
            return
        
        verify_link = self.__mailClient.get_mail()
        if not verify_link:
            Statistics.fails += 1
            return
        
        status = self._verify_email(verify_link)
        if not status:
            Statistics.fails += 1
            return
        
        status = self._login()
        if not status:
            Statistics.fails += 1
            return
        
        Statistics.created += 1
        Utils.write(f"{self.__email}:{BASIC_PASSWORD}:{self.__account_uuid}", f"./output/created.txt")
        
        if PROMOCODE:
            status = self._enter_promocode()
            if not status:
                Statistics.fails += 1
                Utils.write(f"{self.__email}:{BASIC_PASSWORD}:{self.__account_uuid}", f"./output/failed to enter promocode.txt")
                return
            
            Statistics.activated += 1
            Utils.write(f"{self.__email}:{BASIC_PASSWORD}:{self.__account_uuid}", f"./output/{PROMOCODE} activated.txt")
        else:
            logger.success(f"[{self.__email}] Аккаунт успешно зарегистрирован.")
                
    def thread(self):
        try:
            if EMAIL_PROVIDER == "MailTM": # возможно в будущем будут другие провайдеры почт
                self._MailTM_thread()
        except Exception as exc:
            logger.exception(f"Исключение -> {exc}")
        

def worker():
    while Statistics.created < account_limit:
        OctoGen().thread()
        
def main():
    """Основная функция"""
    try:
        threading.Thread(target=Utils.title_worker).start()
        for _ in range(THREADS):
            thread = threading.Thread(target=worker)
            main_threads.append(thread)
            thread.start()
        
        while Statistics.created < account_limit:
            time.sleep(5)
            
        for thread in main_threads:
            thread.join()
        
        print()
        logger.success(f"Успешно сгенерировал {Statistics.created} аккаунтов. Ошибок: {Statistics.fails} | Промокодов активировано: {Statistics.activated}.")
        
    except Exception as exc:
        logger.exception(f"Исключение -> {exc}")
        
if __name__ == "__main__":
    main()
    
# github.com/Churkashh