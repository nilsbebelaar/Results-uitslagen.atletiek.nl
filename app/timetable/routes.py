from flask import Blueprint, render_template, request, redirect, url_for, flash
from threading import Thread
from datetime import datetime
from app.main.background import get_competition_info_xml, get_registrations, save_to_file
from app.timetable.storage import load_index, load_comp, schedule_path, update_index_entry, set_status

timetable_bp = Blueprint('timetable', __name__, template_folder='templates', static_folder='static')

DOMAINS = {
    'NED': 'uitslagen.atletiek.nl',
    'GER': 'ergebnisse.leichtathletik.de',
    'LUX': 'laportal.net',
    'LUX2': 'fla.laportal.net',
    'SUI': 'slv.laportal.net',
}

WEEKDAYS = ['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo']
MONTHS = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sept', 'okt', 'nov', 'dec']


def format_datetime(date_time_str):
    if not date_time_str:
        return ''
    dt = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
    return f"{WEEKDAYS[dt.weekday()]} {dt.day}-{MONTHS[dt.month - 1]} {dt.strftime('%H:%M')}"


def time_indicator(date_time_str, now=None):
    if not date_time_str:
        return None
    event_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
    minutes = (event_time - (now or datetime.now())).total_seconds() / 60

    if minutes < -10:
        return None

    if minutes < 0:
        return {'label': f"{round(-minutes)} min geleden", 'css_class': 'is-danger'}

    hours, mins = divmod(round(minutes), 60)
    label = f"over {hours}u {mins:02d}m" if hours else f"over {mins} min"
    return {'label': label, 'css_class': 'is-danger' if minutes <= 15 else 'is-success'}


def parse_bibs(raw):
    return {b.strip() for b in raw.split(',') if b.strip()} if raw else set()


def bibs_param(bibs):
    return ','.join(sorted(bibs, key=lambda b: (len(b), b)))


def run_pipeline(id, domain, source):
    comp = {'id': id, 'domain': domain, 'source': source}
    try:
        get_competition_info_xml(comp)
        get_registrations(comp)
        save_to_file(comp, save_type='full_comp', filepath=schedule_path(comp['id']))
        update_index_entry(comp, status='Ready')
    except Exception:
        set_status(id, 'Error', domain=domain, source=source)


@timetable_bp.route('/timetable/', methods=['GET'])
def index():
    index_entries = sorted(load_index().values(), key=lambda c: c.get('date_print') or '', reverse=True)
    return render_template('timetable/index.html', comps=index_entries)


@timetable_bp.route('/timetable/add', methods=['POST'])
def add():
    id = request.form.get('ID')
    source_field = request.form.get('source', '')
    domain_code, _, source = source_field.partition('-')

    domain = DOMAINS.get(domain_code)
    if not domain:
        flash(f'Domain {domain_code} not supported', 'error')
        return redirect(url_for('timetable.index'))

    set_status(id, 'Loading', domain=domain, source=source)
    Thread(target=run_pipeline, args=(id, domain, source)).start()

    return redirect(url_for('timetable.view', id=id))


@timetable_bp.route('/timetable/<id>/update', methods=['GET'])
def update(id):
    entry = load_index().get(str(id))
    if not entry:
        flash(f"Wedstrijd '{id}' niet gevonden", 'error')
        return redirect(url_for('timetable.index'))

    set_status(id, 'Loading', domain=entry['domain'], source=entry['source'])
    Thread(target=run_pipeline, args=(entry['id'], entry['domain'], entry['source'])).start()

    return redirect(url_for('timetable.view', id=id, bibs=request.args.get('bibs'), view=request.args.get('view')))


@timetable_bp.route('/timetable/<id>', methods=['GET'])
def view(id):
    entry = load_index().get(str(id))
    comp = load_comp(id)

    if not comp:
        if entry and entry.get('status') == 'Loading':
            return render_template('timetable/loading.html', id=id)
        flash(f"Wedstrijd '{id}' niet gevonden", 'error')
        return redirect(url_for('timetable.index'))

    status = entry.get('status') if entry else None
    athletes = list(comp['athletes'].values())
    bibs = parse_bibs(request.args.get('bibs', ''))
    view_mode = request.args.get('view', 'time')
    q = (request.args.get('q') or '').strip()

    candidates = []
    if q:
        matches = [
            a for a in athletes
            if a['bib'] == q or q.lower() in f"{a['firstname']} {a['lastname']}".lower()
        ]
        if len(matches) == 1:
            bibs.add(matches[0]['bib'])
            return redirect(url_for('timetable.view', id=id, bibs=bibs_param(bibs), view=view_mode))
        elif len(matches) == 0:
            flash(f"Geen atleet gevonden voor '{q}'", 'error')
            return redirect(url_for('timetable.view', id=id, bibs=bibs_param(bibs), view=view_mode))
        else:
            candidates = [
                {**a, 'add_param': bibs_param(bibs | {a['bib']})}
                for a in matches
            ]

    selected = [a for a in athletes if a['bib'] in bibs]

    rows = []
    groups = []
    for athlete in selected:
        name = f"{athlete['firstname']} {athlete['lastname']}"
        club = athlete.get('club')
        remove_param = bibs_param(bibs - {athlete['bib']})
        entries = [
            {
                'bib': athlete['bib'],
                'name': name,
                'club': club,
                'event': sl.get('name') or sl.get('name_short'),
                'time': sl.get('date_time'),
                'time_display': format_datetime(sl.get('date_time')),
                'indicator': time_indicator(sl.get('date_time')),
                'url': sl.get('url'),
                'remove_param': remove_param,
            }
            for sl in athlete.get('startlists', [])
        ]
        rows.extend(entries)
        groups.append({
            'bib': athlete['bib'],
            'name': name,
            'club': club,
            'rows': sorted(entries, key=lambda r: r['time'] or ''),
            'remove_param': remove_param,
        })

    if view_mode == 'athlete':
        groups.sort(key=lambda g: g['name'].lower())
        rows = groups
    else:
        rows.sort(key=lambda r: (r['time'] or '', r['name'].lower()))

    return render_template(
        'timetable/view.html',
        comp=comp,
        rows=rows,
        view_mode=view_mode,
        bibs=bibs,
        bibs_param=bibs_param(bibs),
        candidates=candidates,
        q=q,
        status=status,
    )
