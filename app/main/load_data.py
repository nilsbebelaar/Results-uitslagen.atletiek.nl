import json

def save_export(athletes, id, suffix = ''):
    with open(f"app/static/export/{id}{suffix}.json", 'w') as outfile:
        outfile.write(json.dumps(athletes, sort_keys=True, indent=2, ensure_ascii=False))