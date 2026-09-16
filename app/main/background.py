import requests
import xmltodict
from xml.parsers.expat import ExpatError, errors
import json
import re
from bs4 import BeautifulSoup
from contextlib import contextmanager
from datetime import datetime, timedelta
from app.main.categories import code_to_eventname
from app.models import Competitions
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS
from requests import Session, HTTPError
from requests.exceptions import SSLError
from config import Config

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'nl',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.3'
}


cookies = {'culture': 'nl'}
RECORD_TEXTS = [
    'Records',
    'Rekorde'
]

MAX_RETRY_ATTEMPT = 3


@contextmanager
def get_session(https_url):
    if Config.USE_PROXY:
        with ApiGateway(https_url, regions=EXTRA_REGIONS) as g:
            session = Session()
            session.mount(https_url, g)
            yield session
    else:
        yield Session()


def save_to_file(comp, save_type='athletes', filepath=None):
    filepath = filepath or f"app/static/export/{comp['id']}.json"
    with open(filepath, 'w', encoding='utf-8') as outfile:
        if save_type == 'athletes':
            outfile.write(json.dumps(comp['athletes'], sort_keys=True, indent=2, ensure_ascii=False))
        if save_type == 'full_comp':
            outfile.write(json.dumps(comp, sort_keys=True, indent=2, ensure_ascii=False))


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


def download_xml(comp, s: Session):
    attempt = 0
    comp['url'] = f"https://{comp['domain']}/Competitions/Details/{comp['id']}"
    while True:
        if attempt >= MAX_RETRY_ATTEMPT:
            raise TimeoutError
        attempt += 1
        try:
            response = s.get(comp['url'] + '/ladvxml', headers=headers, cookies=cookies)
            response.raise_for_status()
            xml = xmltodict.parse(response.text, process_namespaces=True)
            return xml['meetingresult']

        except HTTPError as e:
            print("GET error: ", e)
        except ExpatError as e:
            print("XML Error:", errors.messages[e.code])


def download_html(url, s: Session):
    attempt = 0
    while True:
        if attempt >= MAX_RETRY_ATTEMPT:
            raise TimeoutError
        attempt += 1
        try:
            print("HTML Request: ", url)
            response = s.get(url, headers=headers, cookies=cookies)
            # print("HTML Request: ", response.status_code, response.text[:100], response.text[1000:1200])
            response.raise_for_status()
            page_result = BeautifulSoup(response.text, 'html5lib')
            return page_result

        except HTTPError as e:
            print("GET error: ", e)
        except SSLError as e:
            print("SSL error: ", e)


def get_competition_info_xml(comp):
    https_url = f'https://{comp['domain']}'
    with get_session(https_url) as session:
        xml = download_xml(comp, session)

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
            a['@id']: {
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
                'results': [],
                'startlists': []
            } for a in xml['athletes']['athlete']}

        comp['days'] = calc_day_difference(comp['begindate'], comp['enddate'], '%Y-%m-%d') + 1

        comp['resultlists'] = {}
        # Find all result lists, for each day
        for day in range(comp['days']):
            page_competition = download_html(f"{comp['url']}/{day + 1}", session)
            list_date = datetime.strptime(comp['begindate'], '%Y-%m-%d') + timedelta(days=day)
            for block in page_competition.find_all('div', {'class': 'blockcontent'}):
                for a in block.find_all('a'):
                    if not a.has_attr('href'):
                        continue
                    list_id = a['href'].split('/')[-2]
                    roundtime = a.find('div', {'class': 'roundtime'}).text.strip()
                    starttime = datetime.combine(list_date.date(), datetime.strptime(roundtime, '%H:%M').time())
                    mainname = a.find('div', {'class': 'mainname'}).text.strip()
                    typename = a.find('div', {'class': 'typename'}).text.strip().split('(')[0]
                    comp['resultlists'][list_id] = {
                        'url': 'https://' + comp['domain'] + a['href'].replace('CurrentList', 'ResultList'),
                        'raw_name': f"{mainname} {typename}",
                        'starttime': starttime.strftime('%Y-%m-%d %H:%M')
                    }


def get_results_from_xml(comp):
    https_url = f'https://{comp['domain']}'
    with get_session(https_url) as session:
        xml = download_xml(comp, session)

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


def get_registrations(comp):
    https_url = f'https://{comp['domain']}'
    with get_session(https_url) as session:
        page_result = download_html(f"{https_url}/Competitions/Competitoroverview/{comp['id']}", session)
        content = page_result.select('#seltecdlv>div, #content>div')

        athletes_by_bib = {}
        athletes_with_no_bib = []

        for a in comp['athletes'].values():
            if a['bib'] == "-1":
                athletes_with_no_bib.append(a)
            else:
                athletes_by_bib[a['bib']] = a['id']

        for div in content:
            for line in div.select('.entryline'):
                bib = line.select_one('.col-1 .firstline').text.strip()
                fullname = line.select_one('.col-2 .firstline').text.strip()
                club = line.select_one('.col-2 .secondline').text.strip()
                country = line.select_one('.col-42p .firstline').text.strip()
                birthyear = line.select_one('.col-42p .secondline').text.strip()

                athlete_id = athletes_by_bib.get(bib)
                if athlete_id is None:
                    for a in athletes_with_no_bib:
                        if a['firstname'].split()[0] == fullname.split()[0] and a['lastname'].split()[-1] == fullname.split()[-1]:
                            athlete_id = a['id']
                            break

                if not athlete_id:
                    continue

                for a in line.select_one('.col-last').find_all('a'):
                    list_url = ('https://' + comp['domain'] + a['href']).replace('CurrentList', 'RegisterList')
                    list_id = a['href'].split('/')[-2]

                    resultlist = comp['resultlists'].get(list_id)

                    if resultlist:
                        comp['athletes'][athlete_id]['startlists'].append({
                            'list_id': list_id,
                            'name_short': a.text.strip(),
                            'name': resultlist['raw_name'],
                            'url': list_url,
                            'date_time': resultlist['starttime'],
                        })
                    else:
                        print(f"List not found! {list_id}, {list_url}")
            continue


def get_all_results(comp):
    https_url = f'https://{comp['domain']}'
    with get_session(https_url) as session:
        for list_id, list in comp['resultlists'].items():
            if check_for_match(['3x', '3 x', '4x', '4 x', '5x', '5 x', '6x', '6 x', '7x', '7 x', '8x', '8 x', '9x', '9 x', '10x', '10 x'], list['raw_name']):  # Skip relays
                continue
            page_result = download_html(list['url'], session)
            content = page_result.select('#seltecdlv>div, #content>div')

            athletes_by_bib = {}
            athletes_with_no_bib = []
    
            for a in comp['athletes'].values():
                if a['bib'] == "-1":
                    athletes_with_no_bib.append(a)
                else:
                    athletes_by_bib[a['bib']] = a['id']

            for div in content:
                classes = div.get('class')
                if not classes:  # skip empty divs
                    continue
                if ('listheader' not in classes) and ('runblock' not in classes):
                    continue

                if 'listheader' in classes:
                    rightheader = div.select_one('.rightheader')
                    if not rightheader:
                        continue
                    if rightheader.text.strip() != "Uitslagenlijst":
                        continue
                    current_list = {}
                    current_list['url'] = list['url']
                    # current_list['raw_name'] = div.select_one('.leftheader').text.strip()
                    current_list['raw_name'] = list['raw_name']
                    date_string = div('div')[-1].text.strip()[:10]
                    try:
                        current_list['date'] = datetime.strftime(datetime.strptime(date_string, "%d.%m.%Y"), '%d-%m-%Y')
                    except:
                        current_list['date'] = ''
                    continue

                if 'runblock' in classes:
                    if 'heatblock' in classes:  # skip indivudual heats as we get results from total result list
                        continue
                    if div.select_one('.blockname'):
                        if div.select_one('.blockname .leftname').text.strip() in RECORD_TEXTS:
                            continue
                    wind_string = div.select_one('.rightwind').text.strip().replace('Wind:', '').replace(', m/s', '') if div.select_one('.rightwind') else None
                    current_list['winds'] = {}
                    if wind_string:
                        # Parse wind to dict
                        for index_colon, index_space in zip([i for i in findall(':', wind_string)], [i for i in findall(' ', wind_string)]):
                            if (len(wind_string) <= index_colon + 1) or (wind_string[index_colon + 1] == ','):
                                current_list['winds'][wind_string[index_space + 1:index_colon]] = ''
                            else:
                                current_list['winds'][wind_string[index_space + 1:index_colon]] = wind_string[index_colon + 1:index_colon + 5] if wind_string[index_colon + 1] in [
                                    '+', '-'] else wind_string[index_colon + 1:index_colon + 4]

                    has_competitie_teams = True if div.select_one('.resultblock .blockheader .col-2 .secondline').text.strip().lower() == 'team' else False

                    multiple_attempts = False
                    if div.select('.blockheader .col-detailresult'):
                        if re.search("[a-z/A-Z]1", div.select_one('.blockheader .col-detailresult').text.strip()):
                            multiple_attempts = True

                    for line in div.select('.entryline'):
                        bib = line.select_one('.col-1 .secondline').text.strip()

                        athlete_id = athletes_by_bib.get(bib)
                        if athlete_id is None:
                            for a in athletes_with_no_bib:
                                if a['firstname'].split()[0] == fullname.split()[0] and a['lastname'].split()[-1] == fullname.split()[-1]:
                                    athlete_id = a['id']
                                    break
        
                        if not athlete_id:
                            continue

                        if has_competitie_teams:
                            comp['athletes'][athlete_id]['team'] = line.select_one('.col-2 .secondline').text.strip() if line.select('.col-2 .secondline') else None
                        detail = line.select('.col-4 .secondline')[-1].text.strip() if line.select('.col-4 .secondline') else ''
                        heat = line.select_one('.col-6 .firstline').text.strip().split('/')[-1]

                        if multiple_attempts:
                            attempts = [{
                                'result': a.find_next('div').text.strip(),
                                'wind': a.select_one('.secondline').text.strip().replace('(', '').replace(')', '') if a.select('.secondline') else ''
                            } for a in line.select('.col-detailresult')]
                            best_attempt = [{
                                'result': line.select_one('.col-4 .firstline').text.strip(),
                                'wind': line.select_one('.col-4 .secondline').text.strip().replace('(', '').replace(')', '')
                            }]
                        else:
                            attempts = ''
                            best_attempt = {
                                'result': line.select_one('.col-4 .firstline').text.strip(),
                                'wind': current_list['winds'][heat] if current_list['winds'] and heat else ''
                            }

                        comp['athletes'][athlete_id]['results'].append({
                            'best_attempt': best_attempt,
                            'attempts': attempts,
                            'event': parse_event_name(current_list['raw_name']) + parse_event_detail(detail),
                            'event_raw': current_list['raw_name'] + parse_event_detail(detail),
                            'url': current_list['url'],
                            'date': current_list['date'],
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
            event_name_splitted = event_name_splitted[i + 1:]
            break
        if i >= 2:
            break

    if event_name_splitted[0] in ['shot', 'long', 'high', 'pole', 'triple'] or event_name_splitted[1] in ['h', 'horden', 'hurdles', 'hurldes', 'hürden', 'haies', 'hindernis', 'steeple', 'jump', 'lourd', 'throw', 'zone']:
        return event_name_splitted[0] + ' ' + event_name_splitted[1]
    elif event_name_splitted[1] in ['race']:
        return event_name_splitted[0] + ' ' + event_name_splitted[1] + ' ' + event_name_splitted[2]
    return event_name_splitted[0]


def parse_event_detail(detail):
    if detail:
        if detail[-2:] == 'mm':  # Detail contains Hurdle Heights
            value = int(re.findall(r'\d+', detail)[0])
            return f' {round(value / 10)}cm'  # Convert to whole cm
        elif detail[-1] == 'g':
            value = int(re.findall(r'\d+', detail)[0])
            if value >= 1000:
                return f' {value / 1000:.3g}kg'  # Convert to kg with at most two decimals
            else:
                return f' {value}g'  # Leave in g for values lower than 1000g
    return ''


def findall(p, s):
    '''Yields all the positions of
    the pattern p in the string s.'''
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i + 1)


def check_for_match(check_for: list, check_in: str):
    for s in check_for:
        if s in check_in:
            return True
    return False


def calc_day_difference(startdate_string, enddate_string, format):
    return (datetime.strptime(enddate_string, format) - datetime.strptime(startdate_string, format)).days


def parse_date(date_string, format_in, format_out='%d-%m-%Y'):
    return datetime.strftime(datetime.strptime(date_string, format_in), format_out)


def find_by_id(searchlist, id, findindex, searchindex='id'):
    if type(findindex) is list:
        return [c for c in searchlist if c[searchindex] == id]
    else:
        return [c[findindex] for c in searchlist if c[searchindex] == id][0]
