import yaml
import time
import os

from pydantic import BaseModel
from loguru import logger


class Config(BaseModel):
    main: dict
    email_client: dict
    gen: dict
    
    class Config:
        extra = "forbid"

class MainConfig(BaseModel):
    threads: int
    proxyless: bool
    log_proxy_err: bool
    detailed_exception_log: bool

class EmailClientConfig(BaseModel):
    provider: str
    mail_subject: str
    timeout_seconds: int
    
class GeneratorConfig(BaseModel):
    promocode: str

def validate_config():
    """Валидация конфига"""
    
    try:
        with open("./input/config.yaml", "r") as file:
            config = yaml.safe_load(file)
            
        config_data = Config.model_validate(config)

        main_config = MainConfig(**config_data.main)
        email_config = EmailClientConfig(**config_data.email_client)
        gen_config = GeneratorConfig(**config_data.gen)
        return main_config, email_config, gen_config
    except Exception as e:
        logger.exception(f"Ошибка валидации конфига -> {e}")
        time.sleep(5)
        os._exit(1)
        

main_config, email_config, gen_config = validate_config()

THREADS = main_config.threads
PROXYLESS = main_config.proxyless
PROXY_ERR_LOG = main_config.log_proxy_err
DETAILED_EXCEPTION = main_config.detailed_exception_log

EMAIL_PROVIDER = email_config.provider
MAIL_SUBJECT = email_config.mail_subject
MAIL_TIMEOUT = email_config.timeout_seconds

PROMOCODE = gen_config.promocode
