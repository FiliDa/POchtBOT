# 📬 POchtBOT — Gmail → Telegram Notifier

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Gmail API](https://img.shields.io/badge/Gmail%20API-OAuth2-DB4437?style=flat&logo=gmail&logoColor=white)](https://developers.google.com/gmail/api)
[![Telegram Bot](https://img.shields.io/badge/Telegram%20Bot%20API-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://core.telegram.org/bots/api)

Утилита для пересылки новых писем из Gmail в Telegram: в групповой чат (с поддержкой топиков), личный чат и дополнительный канал. Работает через официальные Gmail API (OAuth 2.0) и Telegram Bot API.

## Возможности
- Проверка входящих Gmail и пересылка новых писем в Telegram
- Форматирование MarkdownV2 и экранирование спецсимволов
- Поддержка отправки вложений (ограничение по размеру настраивается)
- Групповые темы (message_thread_id) для структурированных обсуждений
- Простая конфигурация через переменные окружения

## Структура
```
POchtBOT/
└── post/
    ├── main.py                         # цикл опроса и пересылки
    └── gmail_notifier/
        ├── config.py                   # переменные окружения, пути, интервалы
        ├── gmail_client.py             # аутентификация OAuth2, чтение писем/вложений
        ├── telegram_client.py          # отправка сообщений/фото/документов
        └── state_store.py              # состояние: обработанные id и метки времени
```

## Установка
1) Установите зависимости (пример):
```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib requests
```
2) Подготовьте OAuth2 для Gmail API:
   - В консоли Google Cloud создайте OAuth Client (Desktop)
   - Скачайте `credentials.json` и положите рядом с `post/` или задайте путь переменной окружения `GOOGLE_CREDENTIALS_PATH`
   - Первый запуск откроет локальный сервер для авторизации и сохранит `token.json`

## Переменные окружения
Обязательные/рекомендуемые параметры задаются в окружении и читаются в [config.py](post/gmail_notifier/config.py):

- TELEGRAM_BOT_TOKEN — токен вашего бота
- TELEGRAM_CHAT_ID_PERSONAL — chat_id личного чата для уведомлений
- TELEGRAM_CHAT_ID_GROUP — chat_id группового чата
- TELEGRAM_CHAT_ID_SECONDARY — дополнительный чат/канал (опционально)
- TELEGRAM_GROUP_TOPIC_ID — ID топика в групповом чате (опционально)
- FORWARD_GROUP — "true"/"false", пересылать ли в группу (по умолчанию false)
- CHECK_INTERVAL — интервал проверки новых писем в секундах (по умолчанию 60)
- ATTACHMENT_MAX_SIZE_MB — максимальный размер вложения для отправки (по умолчанию 45)
- GOOGLE_CREDENTIALS_PATH — путь к credentials.json (по умолчанию credentials.json)
- GOOGLE_TOKEN_PATH — путь к token.json (по умолчанию token.json)
- STATE_PATH — путь к state.json файлу состояния (по умолчанию state.json)

Все значения по умолчанию не содержат персональных данных.

## Запуск
```
python -m post.main
```
Первый запуск потребует веб‑авторизацию в Google, после чего создастся `token.json`.

## Безопасность
- Токены и chat_id не хранятся в коде — используйте переменные окружения
- `credentials.json`, `token.json`, `post/state.json` исключены из репозитория в `.gitignore`
- Не публикуйте логи и локальные базы в публичный доступ

## Автор
Filippov D.A. — Backend Engineer  
Email: phoenixmediacall@gmail.com  
GitHub: https://github.com/FiliDa

---
Если проект полезен — поставьте ⭐ и предлагайте улучшения через Issues.
