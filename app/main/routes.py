from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.wrappers import Response
from .background import get_competition_info_xml, async_download_competition_results
from .load_data import load_comp, save_comp, list_comps
from threading import Thread

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        id = request.form.get('ID')
        type = request.form.get('type')

        comp = {'id': id, 'type': type}
        get_competition_info_xml(comp)
        save_comp(comp)

        return redirect(url_for('main.add', id=id))


@main_bp.route('/reload/<id>', methods=['GET'])
def reload(id):
    comp = load_comp(id)
    comp = {'id': id, 'type': comp['type'], 'name': comp['name']}
    comp['status'] = 'Downloading'
    save_comp(comp)

    Thread(target=async_download_competition_results, args=(id, True)).start()

    flash(f"Wedstrijd '{comp['name']}' wordt opnieuw gedownload", 'info')
    return redirect(url_for('main.list'))


@main_bp.route('/add/<id>', methods=['GET', 'POST'])
def add(id):
    if request.method == 'GET':
        comp = load_comp(id)
        return render_template('add.html', comp=comp)

    if request.method == 'POST':
        comp = load_comp(id)
        comp['name'] = request.form.get('name')
        comp['type'] = request.form.get('type')
        comp['location'] = request.form.get('location')
        comp['status'] = 'Downloading'
        save_comp(comp)

        Thread(target=async_download_competition_results, args=(id,)).start()

        flash(f"Wedstrijd '{comp['name']}' wordt toegevoegd", 'info')
        return redirect(url_for('main.list'))


@main_bp.route('/list', methods=['GET'])
def list():
    comps = list_comps()
    return render_template('list.html', comps=comps)
