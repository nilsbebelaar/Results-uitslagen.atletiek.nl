from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.main.background import get_competition_info_xml, async_download_competition_results
from app.models import Competitions
from threading import Thread
from config import ALLOWED_DOMAINS

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        comp = {
            'id': request.form.get('ID'),
            'type': request.form.get('type'),
            'source': request.form.get('source').split('-')[-1]
        }

        domain = request.form.get('source').split('-')[0]
        if domain == 'NED':
            comp['domain'] = 'uitslagen.atletiek.nl'
        elif domain == 'GER':
            comp['domain'] = 'ergebnisse.leichtathletik.de'
        elif domain == 'LUX':
            comp['domain'] = 'laportal.net'

        get_competition_info_xml(comp)
        comp['status'] = 'Not downloaded'
        Competitions.save_dict(comp)

        return redirect(url_for('main.add', id=comp['id']))


@main_bp.route('/add/<id>', methods=['GET', 'POST'])
def add(id):
    if request.method == 'GET':
        comp = Competitions.load_dict(id)
        return render_template('add.html', comp=comp)

    if request.method == 'POST':
        comp = Competitions.load_dict(id)
        comp['name'] = request.form.get('name')
        comp['type'] = request.form.get('type')
        comp['location'] = request.form.get('location')
        comp['status'] = 'Downloading'
        Competitions.save_dict(comp)

        Thread(target=async_download_competition_results, args=(current_app._get_current_object(), id)).start()

        flash(f"Wedstrijd '{comp['name']}' wordt toegevoegd", 'info')
        return redirect(url_for('main.list'))


@main_bp.route('/list', methods=['GET'])
def list():
    comps = Competitions.list()
    return render_template('list.html', comps=comps)


@main_bp.route('/reload/<id>', methods=['GET'])
def reload(id):
    comp = Competitions.load_dict(id)
    comp = {'id': id, 'name': comp['name']}
    comp['status'] = 'Downloading'
    Competitions.save_dict(comp)

    Thread(target=async_download_competition_results, args=(current_app._get_current_object(), id, True)).start()

    flash(f"Wedstrijd '{comp['name']}' wordt opnieuw gedownload", 'info')
    return redirect(url_for('main.list'))
