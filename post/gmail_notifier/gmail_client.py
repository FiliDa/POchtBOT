import time
import os
import base64
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import SCOPES, CREDENTIALS_PATH, TOKEN_PATH, STATE_PATH, ATTACHMENT_MAX_SIZE_MB
from .state_store import load_state, save_state


class GmailClient:
    def __init__(self):
        self.service = None
        state = load_state(STATE_PATH)
        self.last_checked_ms = state.get('last_checked_ms')
        self.processed_ids = set(state.get('processed_ids', []))
        self.init_service()

    def init_service(self):
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        self.service = build('gmail', 'v1', credentials=creds)
        self.last_checked_ms = int(time.time() * 1000)

    def list_unread_messages(self):
        try:
            result = self.service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=4
            ).execute()
            messages = result.get('messages', [])
            logging.info(f"gmail.list_unread_recent count={len(messages)}")
            return messages
        except HttpError:
            logging.exception("gmail.list_unread error")
            return []

    def get_message(self, message_id):
        logging.info(f"gmail.get_message id={message_id}")
        return self.service.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()

    def mark_as_read(self, message_id):
        try:
            self.service.users().messages().modify(
                userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logging.info(f"gmail.mark_read id={message_id}")
            return True
        except HttpError:
            logging.exception(f"gmail.mark_read error id={message_id}")
            return False

    def _collect_attachments(self, payload, acc):
        if not payload:
            return
        filename = payload.get('filename')
        body = payload.get('body', {})
        att_id = body.get('attachmentId')
        mime = payload.get('mimeType')
        size = body.get('size')
        if filename and att_id:
            acc.append({
                'filename': filename,
                'mimeType': mime,
                'attachmentId': att_id,
                'size': size
            })
        for part in payload.get('parts', []):
            self._collect_attachments(part, acc)

    def get_attachments_for_message(self, message):
        max_bytes = ATTACHMENT_MAX_SIZE_MB * 1024 * 1024
        attachments = []
        acc = []
        self._collect_attachments(message.get('payload'), acc)
        mid = message.get('id')
        for meta in acc:
            too_large = (meta.get('size') or 0) > max_bytes
            data_bytes = None
            if not too_large:
                try:
                    resp = self.service.users().messages().attachments().get(
                        userId='me', messageId=mid, id=meta['attachmentId']
                    ).execute()
                    data = resp.get('data')
                    if data:
                        padding = len(data) % 4
                        if padding:
                            data += '=' * (4 - padding)
                        data_bytes = base64.urlsafe_b64decode(data)
                except HttpError:
                    logging.exception(f"gmail.attachment.get error mid={mid} att={meta['attachmentId']}")
            attachments.append({
                'filename': meta.get('filename'),
                'mimeType': meta.get('mimeType'),
                'size': meta.get('size') or 0,
                'too_large': too_large,
                'data': data_bytes
            })
        logging.info(f"gmail.attachments count={len(attachments)} mid={mid}")
        return attachments

    def _decode_b64(self, data):
        if not data:
            return ''
        padding = len(data) % 4
        if padding:
            data += '=' * (4 - padding)
        try:
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        except Exception:
            return ''

    def _html_to_text(self, html):
        import re
        text = re.sub(r'<script[\s\S]*?</script>', '', html)
        text = re.sub(r'<style[\s\S]*?</style>', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def _extract_text_from_payload(self, payload):
        if not payload:
            return ''
        mime = payload.get('mimeType') or ''
        body = payload.get('body', {})
        data = body.get('data')
        if mime.startswith('multipart/'):
            parts = payload.get('parts', [])
            if mime == 'multipart/alternative':
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        d = part.get('body', {}).get('data')
                        if d:
                            txt = self._decode_b64(d)
                            if txt:
                                return txt
                for part in parts:
                    if part.get('mimeType') == 'text/html':
                        d = part.get('body', {}).get('data')
                        if d:
                            html = self._decode_b64(d)
                            if html:
                                return self._html_to_text(html)
                for part in parts:
                    t = self._extract_text_from_payload(part)
                    if t:
                        return t
                return ''
            else:
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        d = part.get('body', {}).get('data')
                        if d:
                            txt = self._decode_b64(d)
                            if txt:
                                return txt
                for part in parts:
                    if part.get('mimeType') == 'text/html':
                        d = part.get('body', {}).get('data')
                        if d:
                            html = self._decode_b64(d)
                            if html:
                                return self._html_to_text(html)
                for part in parts:
                    t = self._extract_text_from_payload(part)
                    if t:
                        return t
                return ''
        else:
            if mime == 'text/plain' and data:
                return self._decode_b64(data)
            if mime == 'text/html' and data:
                html = self._decode_b64(data)
                return self._html_to_text(html)
            if data:
                return self._decode_b64(data)
        return ''

    def _dedupe_lines(self, text):
        if not text:
            return ''
        out = []
        prev = None
        for line in text.splitlines():
            s = line.strip()
            if s != prev:
                out.append(line)
                prev = s
        return '\n'.join(out).strip()

    def parse_email_data(self, message):
        headers = message.get('payload', {}).get('headers', [])
        hd = {}
        for h in headers:
            name = h.get('name', '').lower()
            value = h.get('value', '')
            if name:
                hd[name] = value
        text = self._extract_text_from_payload(message.get('payload'))
        text = self._dedupe_lines(text)
        internal_date = message.get('internalDate')
        try:
            internal_date = int(internal_date) if internal_date is not None else 0
        except Exception:
            internal_date = 0
        data = {
            'subject': hd.get('subject', ''),
            'from': hd.get('from', ''),
            'date': hd.get('date', ''),
            'to': hd.get('to', ''),
            'text': text,
            'internalDate': internal_date
        }
        mid = message.get('id')
        if mid:
            data['id'] = mid
        return data

    def get_new_emails(self):
        logging.info("gmail.check.start")
        emails = []
        for item in self.list_unread_messages():
            msg = self.get_message(item['id'])
            data = self.parse_email_data(msg)
            logging.info(
                f"gmail.message id={data.get('id','')} subject={data.get('subject','')} from={data.get('from','')} internalDate={data.get('internalDate',0)}"
            )
            mid = data.get('id')
            if mid and mid not in self.processed_ids:
                emails.append(data)
        max_internal = max([e.get('internalDate', 0) for e in emails], default=self.last_checked_ms or 0)
        now_ms = int(time.time() * 1000)
        self.last_checked_ms = max_internal or now_ms
        logging.info(f"gmail.check.end new_count={len(emails)} last_checked_ms={self.last_checked_ms}")
        save_state(STATE_PATH, self.processed_ids, self.last_checked_ms)
        return emails
