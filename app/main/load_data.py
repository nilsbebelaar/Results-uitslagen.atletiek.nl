import json
from glob import glob

def load_comp(id):
    return json.loads(open(f"data/{id}.json", "r").read())

def save_comp(comp):
    with open(f"data/{comp['id']}.json", 'w') as outfile:
        outfile.write(json.dumps(comp, sort_keys=True, indent=2, ensure_ascii=False))

def list_comps():
    existing_ids = [f.split('.')[0].split('/')[-1].split('\\')[-1] for f in glob("data/*.json")]
    return [load_comp(id) for id in existing_ids]

def save_export(athletes, id, suffix = ''):
    with open(f"app/static/export/{id}{suffix}.json", 'w') as outfile:
        outfile.write(json.dumps(athletes, sort_keys=True, indent=2, ensure_ascii=False))