
# Генератор аккаунтов OctoBrowser и ввод промокодов

Этот проект представляет собой софт для генерации аккаунтов OctoBrowser и ввода промокодов с поддержкой мультипотока, умной обработки ошибок и возможностью настройки под ваши нужды.

## 🚀 Функционал:
- **Мультипоточность** — поддержка работы с несколькими потоками одновременно.
- **Умная обработка ошибок** — подробные сообщения об ошибках и действиях софта.
- **Настройка работы софта** — настройка параметров под ваши нужды.

## 🛠 Установка и использование

### 1. Настройка `config.yaml`

Прежде чем запускать софт, настройте файл конфигурации `input/config.yaml` в соответствии с вашими предпочтениями:

```yaml
main:
    threads: 1  # Количество потоков
    proxyless: False  # Использовать прокси или нет
    log_proxy_err: False  # Логировать ошибки прокси
    detailed_exception_log: False  # Подробное логирование исключений при отправке запросов

email_client:
    provider: "MailTM"  # Единственный поддерживаемый провайдер почты в данный момент
    mail_subject: "[Registration] Complete Activation"  # Заголовок письма с подтверждением почты
    timeout_seconds: 25  # Время ожидания письма с верификацией почты (в секундах)

gen:
    promocode: ""  # Промокод для активации после регистрации, если не нужен — оставьте пустым

# Прокси настройка (если proxyless: False)
# Единственный поддерживаемый формат прокси: user:pass@host:port
proxy:
    - "username:password@proxy_host:proxy_port"  # Пример прокси
```

- Если `proxyless: False`, добавьте список прокси в файл `input/proxies.txt`. Прокси должны быть в формате `user:pass@host:port`.

### 2. Установка зависимостей

Для установки всех необходимых зависимостей выполните команду:

```bash
py -m pip install -r requirements.txt
```

### 3. Запуск

Для запуска скрипта используйте следующую команду:

```bash
python main.py
```

## 📜 Лицензия

Этот проект распространяется под MIT лицензией. Использование данного софта разрешается исключительно в образовательных целях. Все действия с использованием этого инструмента должны быть выполнены в рамках законодательства. Владелец не несет ответственности за использование данного софта.
- Telegram: [@churk_yyy](https://t.me/churk_yyy) (НЕ пишите с вопросами по скрипту).
