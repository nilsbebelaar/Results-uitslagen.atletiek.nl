import json
import os
from datetime import datetime, timezone

SCHEDULE_DIR = "app/static/export/schedule"
INDEX_PATH = f"{SCHEDULE_DIR}/index.json"

os.makedirs(SCHEDULE_DIR, exist_ok=True)


def schedule_path(id):
    return f"{SCHEDULE_DIR}/{id}.json"


def load_index():
    if not os.path.exists(INDEX_PATH):
        return {}
    with open(INDEX_PATH, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def save_index(index):
    os.makedirs(SCHEDULE_DIR, exist_ok=True)
    with open(INDEX_PATH, 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(index, sort_keys=True, indent=2, ensure_ascii=False))


def update_index_entry(comp, status='Ready'):
    index = load_index()
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
    save_index(index)


def set_status(id, status, domain=None, source=None):
    index = load_index()
    entry = index.get(str(id), {'id': id})
    entry['status'] = status
    if domain:
        entry['domain'] = domain
    if source:
        entry['source'] = source
    entry['updated_at'] = datetime.now(timezone.utc).isoformat()
    index[str(id)] = entry
    save_index(index)


def load_comp(id):
    path = schedule_path(id)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as infile:
        return json.load(infile)
