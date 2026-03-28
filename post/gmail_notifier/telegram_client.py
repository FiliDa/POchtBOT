import requests
import logging
from .config import TELEGRAM_BOT_TOKEN


class TelegramClient:
    def __init__(self, token=None):
        self.token = token or TELEGRAM_BOT_TOKEN

    def _escape_md(self, s):
        if s is None:
            return ''
        import re
        return re.sub(r'([_\*\[\]\(\)~`>\#\+\-=\|\{\}\.\!])', r'\\\1', s)

    def send(self, chat_id, text, message_thread_id=None):
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'MarkdownV2'
        }
        if message_thread_id:
            payload['message_thread_id'] = message_thread_id
        try:
            logging.info(f"telegram.send start chat_id={chat_id} thread={message_thread_id} length={len(text)}")
            r = requests.post(url, json=payload, timeout=15)
            ok = False
            if r.status_code == 200:
                j = r.json()
                ok = bool(j.get('ok'))
                logging.info(f"telegram.send done status={r.status_code} ok={ok} desc={j.get('description','')}" )
            else:
                logging.info(f"telegram.send fail status={r.status_code} body={r.text[:300]}")
            return ok
        except Exception:
            logging.exception("telegram.send error")
            return False

    def format_email(self, email):
        to_v = self._escape_md(email.get('to', ''))
        from_v = self._escape_md(email.get('from', ''))
        subject_v = self._escape_md(email.get('subject', ''))
        date_v = self._escape_md(email.get('date', ''))
        body_v = self._escape_md((email.get('text') or '')[:1500])
        parts = [
            '📧 *Новое письмо в Gmail*',
            '',
            f"*Ящик:* {to_v}",
            f"*От:* {from_v}",
            f"*Тема:* {subject_v}",
            f"*Дата:* {date_v}",
            '',
            body_v
        ]
        return '\n'.join(parts)

    def send_document(self, chat_id, filename, data_bytes, mime_type=None, message_thread_id=None, caption=None):
        url = f'https://api.telegram.org/bot{self.token}/sendDocument'
        files = {
            'document': (filename, data_bytes, mime_type or 'application/octet-stream')
        }
        payload = {
            'chat_id': chat_id
        }
        if caption:
            payload['caption'] = self._escape_md(caption)
            payload['parse_mode'] = 'MarkdownV2'
        if message_thread_id:
            payload['message_thread_id'] = message_thread_id
        try:
            logging.info(f"telegram.sendDocument start chat_id={chat_id} file={filename} size={len(data_bytes)}")
            r = requests.post(url, data=payload, files=files, timeout=60)
            ok = r.status_code == 200 and bool(r.json().get('ok'))
            logging.info(f"telegram.sendDocument done status={r.status_code} ok={ok}")
            return ok
        except Exception:
            logging.exception("telegram.sendDocument error")
            return False

    def send_photo(self, chat_id, filename, data_bytes, message_thread_id=None, caption=None):
        url = f'https://api.telegram.org/bot{self.token}/sendPhoto'
        files = {
            'photo': (filename, data_bytes)
        }
        payload = {
            'chat_id': chat_id
        }
        if caption:
            payload['caption'] = self._escape_md(caption)
            payload['parse_mode'] = 'MarkdownV2'
        if message_thread_id:
            payload['message_thread_id'] = message_thread_id
        try:
            logging.info(f"telegram.sendPhoto start chat_id={chat_id} file={filename} size={len(data_bytes)}")
            r = requests.post(url, data=payload, files=files, timeout=60)
            ok = r.status_code == 200 and bool(r.json().get('ok'))
            logging.info(f"telegram.sendPhoto done status={r.status_code} ok={ok}")
            return ok
        except Exception:
            logging.exception("telegram.sendPhoto error")
            return False

    def send_video(self, chat_id, filename, data_bytes, message_thread_id=None, caption=None):
        url = f'https://api.telegram.org/bot{self.token}/sendVideo'
        files = {
            'video': (filename, data_bytes)
        }
        payload = {
            'chat_id': chat_id
        }
        if caption:
            payload['caption'] = self._escape_md(caption)
            payload['parse_mode'] = 'MarkdownV2'
        if message_thread_id:
            payload['message_thread_id'] = message_thread_id
        try:
            logging.info(f"telegram.sendVideo start chat_id={chat_id} file={filename} size={len(data_bytes)}")
            r = requests.post(url, data=payload, files=files, timeout=120)
            ok = r.status_code == 200 and bool(r.json().get('ok'))
            logging.info(f"telegram.sendVideo done status={r.status_code} ok={ok}")
            return ok
        except Exception:
            logging.exception("telegram.sendVideo error")
            return False
