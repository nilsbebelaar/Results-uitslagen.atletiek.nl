import requests
import xmltodict
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from app.main.categories import code_to_eventname
from app.models import Competitions


headers = {'accept-language': 'nl'}
cookies = {'culture': 'nl'}


def save_to_file(comp):
    with open(f"app/static/export/{comp['id']}.json", 'w') as outfile:
        outfile.write(json.dumps(comp['athletes'], sort_keys=True, indent=2, ensure_ascii=False))


def download_competition_results(app, comp):
    with app.app_context():
        get_competition_info_xml(comp)
        if comp['source'] == 'html':
            get_all_results(comp)
            cleanup_athletes(comp)
        elif comp['source'] == 'xml':
            get_results_from_xml(comp)
            find_results_xml(comp)

        comp['status'] = 'Ready'
        save_to_file(comp)
        Competitions.save_dict(comp)
        return comp


def async_download_competition_results(app, ids, full_reload=False):
    with app.app_context():
        for id in ids:
            comp = Competitions.load_dict(id)
            if not comp:
                return

            if full_reload:
                get_competition_info_xml(comp)

            if comp['source'] == 'html':
                get_all_results(comp)
                cleanup_athletes(comp)
            elif comp['source'] == 'xml':
                get_results_from_xml(comp)
                find_results_xml(comp)

            comp['status'] = 'Ready'
            Competitions.save_dict(comp)
            save_to_file(comp)


def find_results_xml(comp):
    # Remove bib number as index
    comp['athletes'] = [athlete for athlete in comp['athletes'].values()]
    for athlete in comp['athletes']:
        athlete['competition'] = {
            'name': comp['name'],
            'location': comp['location'],
            'url': comp['url']
        }
        athlete['SELTECLOOKUP'] = '1' if athlete['licencenumber'] == '0' else '0'
        athlete['results'] = []

        for result in find_by_id(comp['results'], athlete['id'], [], 'athlete_id'):
            athlete['results'].append({
                'event': find_by_id(comp['events'], result['event_id'], 'name'),
                'result': result['result'],
                'url': comp['url'],
                # 'category': result['category'],
                'date': result['date']
            })
        athlete.pop('id', None)

    # Remove competitors if they have no results
    comp['athletes'] = [athlete for athlete in comp['athletes'] if athlete['results']]


def download_xml(comp):
    comp['url'] = 'https://' + comp['domain'] + '/Competitions/Details/' + str(comp['id'])
    with requests.session() as s:
        # XML page with competition information
        response = s.get(comp['url'] + '/ladvxml', headers=headers, cookies=cookies)
        xml = xmltodict.parse(response.text, process_namespaces=True)
    return xml['meetingresult']


def download_html(url):
    with requests.session() as s:
        response = s.get(url, headers=headers, cookies=cookies)
        page_result = BeautifulSoup(response.text, 'html5lib')
    return page_result


def get_competition_info_xml(comp):
    xml = download_xml(comp)
    comp['country'] = xml['@country']
    comp['begindate'] = xml['@begindate']
    comp['enddate'] = xml['@enddate']
    if comp['begindate'] == comp['enddate']:
        comp['date_print'] = parse_date(comp['begindate'], '%Y-%m-%d', '%d %b %Y')
    else:
        comp['date_print'] = (parse_date(comp['begindate'], '%Y-%m-%d', '%d %b - ') + parse_date(comp['enddate'], '%Y-%m-%d', '%d %b %Y'))
    comp['location'] = xml['@city']
    comp['name'] = xml['@name']

    if type(xml['clubs']['club']) is list:
        clubs = [{
            'country': c['@country'],
            'id': c['@id'],
            'name': c['@name']
        } for c in xml['clubs']['club']]
    else:
        clubs = [{
            'country': xml['clubs']['club']['@country'],
            'id': xml['clubs']['club']['@id'],
            'name': xml['clubs']['club']['@name']
        }]

    comp['athletes'] = {
        a['@number']: {
            'club': find_by_id(clubs, a['@club'], 'name'),
            'country': a['@country'],
            'birthdate': parse_date(a['@dateofbirth'][:10], '%Y-%m-%d') if '@dateofbirth' in a else None,
            'birthyear': a['@yearofbirth'],
            'firstname': a['@forename'],
            'lastname': a['@lastname'],
            'id': a['@id'],
            'licencenumber': a['@licencenumber'],
            'bib': a['@number'],
            'sex': 'male' if a['@sex'] == 'M' else ('female' if a['@sex'] == 'W' else ''),
            'results': []
        } for a in xml['athletes']['athlete']}

    comp['days'] = calc_day_difference(comp['begindate'], comp['enddate'], '%Y-%m-%d') + 1

    comp['resultlists'] = []
    # Find all result lists, for each day
    for day in range(comp['days']):
        page_competition = download_html(comp['url'] + '/' + str(day + 1))
        for block in page_competition.find_all('div', {'class': 'blockcontent'}):
            for a in block.find_all('a'):
                resultlist = {}
                resultlist['url'] = 'https://' + comp['domain'] + a['href'].replace('CurrentList', 'ResultList')
                resultlist['raw_name'] = a.find('div', {'class': 'mainname'}).text.strip()
                comp['resultlists'].append(resultlist)


def calc_day_difference(startdate_string, enddate_string, format):
    return (datetime.strptime(enddate_string, format) - datetime.strptime(startdate_string, format)).days


def parse_date(date_string, format_in, format_out='%d-%m-%Y'):
    return datetime.strftime(datetime.strptime(date_string, format_in), format_out)


def find_by_id(searchlist, id, findindex, searchindex='id'):
    if type(findindex) is list:
        return [c for c in searchlist if c[searchindex] == id]
    else:
        return [c[findindex] for c in searchlist if c[searchindex] == id][0]


def get_results_from_xml(comp):
    xml = download_xml(comp)
    comp['results'] = []
    for round in xml['rounds']['round']:
        if round['@roundtype'] == 'TIMERACE' and '@roundid' not in round:
            continue
        if 'individual' not in round['results']:
            continue
        if type(round['results']['individual']) is list:
            for result in round['results']['individual']:
                comp['results'].append({
                    'athlete_id': result['@athlete'],
                    'event_id': round['@event'],
                    'date': round['@startofeventdate'],
                    'category': round['@ageclass'],
                    'result': result['@result']
                })
        else:
            result = round['results']['individual']
            comp['results'].append({
                'athlete_id': result['@athlete'],
                'event_id': round['@event'],
                'date': round['@startofeventdate'],
                'category': round['@ageclass'],
                'result': result['@result']
            })

    comp['events'] = []
    for event in xml['events']['event']:
        comp['events'].append({
            'name': code_to_eventname(event['@code']),
            'id': event['@id']
        })


def get_all_results(comp):
    page_result = download_html(comp['url'].replace('Details', 'Resultoverview'))
    content = page_result.select('#seltecdlv>div, #content>div')
    for div in content:
        classes = div.get('class')
        if ('listheader' not in classes) and ('runblock' not in classes):
            continue

        if 'listheader' in classes:
            current_list = {}
            current_list['url'] = 'https://' + comp['domain'] + div.select_one('.leftheader a')['href']
            current_list['raw_name'] = div.select_one('.leftheader a').text.strip()
            date_string = div('div')[-1].text.strip()[:10]
            try:
                current_list['date'] = datetime.strftime(datetime.strptime(date_string, "%d.%m.%Y"), '%d-%m-%Y')
            except:
                current_list['date'] = ''

            continue

        if 'runblock' in classes:
            current_list['category'] = [c for c in classes if 'c-' in c][0].split('-')[-1]
            wind_string = div.select_one('.rightwind').text.strip().replace('Wind:', '').replace(', m/s', '')
            current_list['winds'] = {}
            if wind_string:
                # Parse wind to dict
                for index_colon, index_space in zip([i for i in findall(':', wind_string)], [i for i in findall(' ', wind_string)]):
                    if (len(wind_string) <= index_colon+1) or (wind_string[index_colon+1] == ','):
                        current_list['winds'][wind_string[index_space+1:index_colon]] = ''
                    else:
                        current_list['winds'][wind_string[index_space+1:index_colon]] = wind_string[index_colon+1:index_colon+5] if wind_string[index_colon+1] in [
                            '+', '-'] else wind_string[index_colon+1:index_colon+4]

            has_competitie_teams = True if div.select_one('.resultblock .blockheader .col-2 .secondline').text.strip().lower() == 'team' else False

            for line in div.select('.entryline'):
                bib = line.select_one('.col-1 .secondline').text.strip()
                if bib in comp['athletes']:
                    if has_competitie_teams:
                        comp['athletes'][bib]['team'] = line.select_one('.col-2 .secondline').text.strip() if line.select('.col-2 .secondline') else None
                    detail = line.select('.col-4 .secondline')[-1].text.strip() if line.select('.col-4 .secondline') else ''
                    heat = line.select_one('.col-6 .firstline').text.strip().split('/')[-1]
                    comp['athletes'][bib]['results'].append({
                        'result': line.select_one('.col-4 .firstline').text.strip(),
                        # 'category': line.select('.col-4 .firstline')[-1].text.strip(),
                        'event': parse_event_name(current_list['raw_name']) + parse_event_detail(detail),
                        'event_raw': current_list['raw_name'] + parse_event_detail(detail),
                        'url': current_list['url'],
                        'date': current_list['date'],
                        'wind': current_list['winds'][heat] if current_list['winds'] and heat else ''
                    })
            continue


def cleanup_athletes(comp):
    # Remove competitors if they have no results, also remove bib as index
    comp['athletes'] = [athlete for athlete in comp['athletes'].values() if athlete['results']]

    for athlete in comp['athletes']:
        athlete['competition'] = {
            'name': comp['name'],
            'location': comp['location'],
            'url': comp['url']
        }
        athlete['SELTECLOOKUP'] = '1' if athlete['licencenumber'] == '0' else '0'
        athlete.pop('id', None)


def parse_event_name(event_name):
    event_name_splitted = event_name.lower().split()
    meerkampbenamingen = ['pentathlon', 'pentahtlon', 'meerkamp', 'kamp', 'kampf']
    for i, name_part in enumerate(event_name_splitted):
        if name_part in meerkampbenamingen:
            event_name_splitted = event_name_splitted[i+1:]
            break
        if i > 2:
            break

    if event_name_splitted[0] in ['shot', 'long', 'high', 'pole', 'triple'] or event_name_splitted[1] in ['h', 'horden', 'hurdles', 'hurldes', 'hürden', 'haies', 'jump', 'lourd', 'throw', 'zone']:
        return event_name_splitted[0] + ' ' + event_name_splitted[1]
    elif event_name_splitted[1] in ['race']:
        return event_name_splitted[0] + ' ' + event_name_splitted[1] + ' ' + event_name_splitted[2]
    return event_name_splitted[0]


def parse_event_detail(detail):
    if detail:
        if detail[-2:] == 'mm':  # Detail contains Hurdle Heights
            value = int(re.findall(r'\d+', detail)[0])
            return f' {round(value/10)}cm'  # Convert to whole cm
        elif detail[-1] == 'g':
            value = int(re.findall(r'\d+', detail)[0])
            if value >= 1000:
                return f' {value/1000:.3g}kg'  # Convert to kg with at most two decimals
            else:
                return f' {value}g'  # Leave in g for values lower than 1000g
    return ''


def findall(p, s):
    '''Yields all the positions of
    the pattern p in the string s.'''
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
