import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
CHAT_IDS = {
    'personal': os.getenv('TELEGRAM_CHAT_ID_PERSONAL', ''),
    'group': os.getenv('TELEGRAM_CHAT_ID_GROUP', ''),
    'secondary': os.getenv('TELEGRAM_CHAT_ID_SECONDARY', '')
}
_topic_id_raw = os.getenv('TELEGRAM_GROUP_TOPIC_ID', '').strip()
GROUP_TOPIC_ID = int(_topic_id_raw) if _topic_id_raw.isdigit() else None
FORWARD_GROUP = os.getenv('FORWARD_GROUP', 'false').lower() == 'true'

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))

CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
TOKEN_PATH = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
STATE_PATH = os.getenv('STATE_PATH', 'state.json')
ATTACHMENT_MAX_SIZE_MB = int(os.getenv('ATTACHMENT_MAX_SIZE_MB', '45'))
