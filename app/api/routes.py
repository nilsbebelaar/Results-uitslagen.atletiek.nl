from flask import Blueprint, request, current_app
from app.main.background import get_competition_info_xml, download_competition_results, async_download_competition_results
from app.models import Competitions
from threading import Thread
from config import ALLOWED_DOMAINS
import json

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/add/<id>', methods=['POST'])
def add(id):
    url_args = request.args.to_dict()

    if 'source' not in url_args:
        return "'source' is required"
    if 'domain' not in url_args:
        return "'domain' is required"

    if url_args['source'] not in ['html', 'xml']:
        return f"source '{url_args['source']}' is not supported"
    if url_args['domain'] not in ALLOWED_DOMAINS:
        return f"domain '{url_args['domain']}' is not supported"

    comp = {
        'id': id,
        'source': url_args['source'],
        'domain': url_args['domain']
    }

    get_competition_info_xml(comp)
    comp['status'] = 'Loading'
    Competitions.save_dict(comp)

    Thread(target=async_download_competition_results, args=(current_app._get_current_object(), id)).start()

    return f"Wedstrijd '{comp['name']}' wordt toegevoegd"


@api_bp.route('/api/status/<id>', methods=['GET'])
def status(id):
    comp = Competitions.load_dict(id)
    if comp:
        return comp['status']
    else:
        return 'ID Not Found'


@api_bp.route('/api/get_json/<id>', methods=['GET'])
def get_json(id):
    url_args = request.args.to_dict()

    if 'source' not in url_args:
        return "'source' is required"
    if 'domain' not in url_args:
        return "'domain' is required"

    if url_args['source'] not in ['html', 'xml']:
        return f"source '{url_args['source']}' is not supported"
    if url_args['domain'] not in ALLOWED_DOMAINS:
        return f"domain '{url_args['domain']}' is not supported"

    comp = {
        'id': id,
        'source': url_args['source'],
        'domain': url_args['domain']
    }

    get_competition_info_xml(comp)
    comp = async_download_competition_results(current_app._get_current_object(), id, full_reload=True)
    json_string = json.dumps(comp['athletes'], sort_keys=True, ensure_ascii=False)
    return json_string

