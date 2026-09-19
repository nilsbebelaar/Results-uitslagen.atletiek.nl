import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from threading import Lock

SCHEDULE_DIR = "app/static/export/schedule"
INDEX_PATH = f"{SCHEDULE_DIR}/index.json"

os.makedirs(SCHEDULE_DIR, exist_ok=True)

_index_lock = Lock()


def schedule_path(id):
    return f"{SCHEDULE_DIR}/{id}.json"


def load_index():
    if not os.path.exists(INDEX_PATH):
        return {}
    with open(INDEX_PATH, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def save_index(index):
    os.makedirs(SCHEDULE_DIR, exist_ok=True)
    tmp_path = f"{INDEX_PATH}.tmp"
    with open(tmp_path, 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(index, sort_keys=True, indent=2, ensure_ascii=False))

    # os.replace can transiently fail on Windows (PermissionError) if something
    # else (antivirus, indexer) briefly has the destination open for reading.
    for attempt in range(5):
        try:
            os.replace(tmp_path, INDEX_PATH)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.05)


@contextmanager
def _locked_index():
    # Serializes every read-modify-write against index.json: without this, concurrent
    # background threads (or a thread racing a page load) can both open the file for
    # writing at once, which on Windows can surface as OSError: [Errno 22] Invalid argument.
    with _index_lock:
        index = load_index()
        yield index
        save_index(index)


def update_index_entry(comp, status='Ready'):
    with _locked_index() as index:
        index[str(comp['id'])] = {
            'id': comp['id'],
            'name': comp.get('name'),
            'location': comp.get('location'),
            'date_print': comp.get('date_print'),
            'domain': comp.get('domain'),
            'source': comp.get('source'),
            'status': status,
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }


def set_status(id, status, domain=None, source=None):
    with _locked_index() as index:
        entry = index.get(str(id), {'id': id})
        entry['status'] = status
        entry.pop('progress', None)
        if domain:
            entry['domain'] = domain
        if source:
            entry['source'] = source
        index[str(id)] = entry


def set_progress(id, current, total):
    with _locked_index() as index:
        entry = index.get(str(id), {'id': id})
        entry['progress'] = {'current': current, 'total': total}
        index[str(id)] = entry


def load_comp(id):
    path = schedule_path(id)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as infile:
        return json.load(infile)
