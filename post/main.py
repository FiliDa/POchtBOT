import time
import logging
from gmail_notifier.gmail_client import GmailClient
from gmail_notifier.telegram_client import TelegramClient
from gmail_notifier.config import CHAT_IDS, GROUP_TOPIC_ID, CHECK_INTERVAL, FORWARD_GROUP


def process_once(gmail, telegram):
    emails = gmail.get_new_emails()
    logging.info(f"loop.process count={len(emails)}")
    for e in emails:
        logging.info(f"loop.format subject={e.get('subject','')} from={e.get('from','')}")
        msg = telegram.format_email(e)
        ok_group = telegram.send(CHAT_IDS['group'], msg, GROUP_TOPIC_ID)
        logging.info(f"loop.send.group ok={ok_group}")
        ok_personal = telegram.send(CHAT_IDS['personal'], msg)
        logging.info(f"loop.send.personal ok={ok_personal}")
        ok_secondary = telegram.send(CHAT_IDS['secondary'], msg)
        logging.info(f"loop.send.secondary ok={ok_secondary}")
        if ok_personal or ok_secondary:
            mid = e.get('id')
            if mid:
                gmail.mark_as_read(mid)
                gmail.processed_ids.add(mid)


def run():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info("app.start")
    gmail = GmailClient()
    telegram = TelegramClient()
    while True:
        try:
            process_once(gmail, telegram)
            logging.info(f"sleep {CHECK_INTERVAL}s")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logging.info("app.stop")
            break
        except Exception:
            logging.exception("loop.error")
            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    run()
