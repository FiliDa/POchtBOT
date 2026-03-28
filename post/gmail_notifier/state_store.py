import json
import os


def load_state(path):
    if not os.path.exists(path):
        return {"processed_ids": [], "last_checked_ms": None}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data.get('processed_ids'), list):
                data['processed_ids'] = []
            return {
                "processed_ids": data.get('processed_ids', []),
                "last_checked_ms": data.get('last_checked_ms')
            }
    except Exception:
        return {"processed_ids": [], "last_checked_ms": None}


def save_state(path, processed_ids, last_checked_ms):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "processed_ids": list(processed_ids),
                "last_checked_ms": last_checked_ms
            }, f, ensure_ascii=False)
        return True
    except Exception:
        return False

