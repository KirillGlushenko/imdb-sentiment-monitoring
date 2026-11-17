
import json
import smtplib
import urllib.request
from pathlib import Path
from email.message import EmailMessage


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


def load_config():
    config = {}

    if not ENV_PATH.exists():
        return config

    for line in ENV_PATH.read_text(
        encoding="utf-8-sig"
    ).splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        key, separator, value = line.partition("=")

        if separator:
            config[key.strip()] = value.strip()

    return config


def send_telegram(message: str) -> None:
    try:
        config = load_config()

        token = config.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = config.get("TELEGRAM_CHAT_ID", "")

        if not token or not chat_id:
            print("[TELEGRAM] Настройки не заполнены")
            return

        url = (
            f"https://api.telegram.org/bot"
            f"{token}/sendMessage"
        )

        payload = json.dumps({
            "chat_id": chat_id,
            "text": message
        }).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            result = json.load(response)

        if result.get("ok"):
            print("[TELEGRAM] Сообщение отправлено!")
        else:
            print("[TELEGRAM] Ошибка отправки")

    except Exception as error:
        print(
            "[TELEGRAM] Ошибка: "
            f"{type(error).__name__}"
        )


def send_email(subject: str, message: str) -> None:
    config = load_config()

    mode = config.get("EMAIL_MODE", "test").lower()

    if mode == "test":
        print("\n[EMAIL] Тестовый режим")
        print(f"Тема: {subject}")
        print(f"Сообщение:\n{message}")
        print("[EMAIL] Реальная отправка отключена")
        return

    if mode != "smtp":
        print("[EMAIL] Неизвестный режим отправки")
        return

    required = [
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "EMAIL_FROM",
        "EMAIL_TO"
    ]

    if any(not config.get(key) for key in required):
        print("[EMAIL] Настройки SMTP не заполнены")
        return

    try:
        email = EmailMessage()

        email["Subject"] = subject
        email["From"] = config["EMAIL_FROM"]
        email["To"] = config["EMAIL_TO"]
        email.set_content(message)

        host = config["SMTP_HOST"]
        port = int(config["SMTP_PORT"])

        if port == 465:
            server = smtplib.SMTP_SSL(
                host, port, timeout=15
            )
        elif port == 587:
            server = smtplib.SMTP(
                host, port, timeout=15
            )
        else:
            print("[EMAIL] Используй порт 465 или 587")
            return

        with server:
            if port == 587:
                server.starttls()

            server.login(
                config["SMTP_USER"],
                config["SMTP_PASSWORD"]
            )

            server.send_message(email)

        print("[EMAIL] Письмо успешно отправлено!")

    except Exception as error:
        print(
            "[EMAIL] Ошибка отправки: "
            f"{type(error).__name__}"
        )
