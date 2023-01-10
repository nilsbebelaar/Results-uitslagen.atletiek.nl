import requests
import xmltodict
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from app.main.categories import code_to_eventname
from app.models import Competitions


headers = {'accept-language': 'nl'}


def save_to_file(comp):
    with open(f"app/static/export/{comp['id']}.json", 'w') as outfile:
        outfile.write(json.dumps(comp['athletes'], sort_keys=True, indent=2, ensure_ascii=False))


def async_download_competition_results(app, id, full_reload=False):
    with app.app_context():
        comp = Competitions.load_dict(id)
        if not comp:
            return

        if full_reload:
            get_competition_info_xml(comp)

        if comp['source'] == 'html':
            get_results_from_lists(comp)
        elif comp['source'] == 'xml':
            get_results_from_xml(comp)

        find_results(comp)

        comp['status'] = 'Ready'
        Competitions.save_dict(comp)

        save_to_file(comp)
        return comp


def find_results(comp):
    for athlete in comp['athletes']:
        athlete['competition'] = {
            'name': comp['name'],
            'location': comp['location'],
            'url': comp['url']
        }
        athlete['SELTECLOOKUP'] = '1' if athlete['licencenumber'] == '0' else '0'
        athlete['results'] = []
        if comp['source'] == 'html':
            # For every athlete, loop through all results
            for resultlist in comp['resultlists']:
                for result in resultlist['results']:
                    # If a athlete's bib-number exists in the results, append the result to the athlete['results'] list
                    if athlete['bib'] == result['bib']:
                        if resultlist['is_highjump']:
                            result['category'] = resultlist['categories'][athlete['bib']]

                        if result['category'] in ['MASTERSM', 'MASTERSV']:
                            result['category'] = result['category'] + ' ' + athlete['birthyear']

                        athlete['results'].append({
                            'event': parse_event_name(resultlist['raw_name']) + parse_event_detail(result['event_detail']),  # result['category'], athlete['birthyear']),
                            'result': result['result'],
                            'url': resultlist['url'],
                            'date': resultlist['date'],
                            'category': result['category']
                        })
        elif comp['source'] == 'xml':
            for result in find_by_id(comp['results'], athlete['id'], [], 'athlete_id'):
                athlete['results'].append({
                    'event': find_by_id(comp['events'], result['event_id'], 'name'),
                    'result': result['result'],
                    'url': comp['url'],
                    'date': result['date'],
                    'category': result['category']
                })
        athlete.pop('id', None)

    # Remove competitors if the have no results
    comp['athletes'] = [athlete for athlete in comp['athletes'] if athlete['results']]


def download_xml(comp):
    comp['url'] = 'https://' + comp['domain'] + '/Competitions/Details/' + str(comp['id'])
    session = requests.session()

    # XML page with competition information
    response = session.get(comp['url'] + '/ladvxml', headers=headers)
    xml = xmltodict.parse(response.text, process_namespaces=True)

    session.close()
    return xml['meetingresult']


def download_html(url):
    session = requests.session()

    response = session.get(url, headers=headers)
    page_result = BeautifulSoup(response.text, 'html.parser')

    session.close()
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

    clubs = [{
        'country': c['@country'],
        'id': c['@id'],
        'name': c['@name']
    } for c in xml['clubs']['club']]

    comp['athletes'] = [{
        'club': find_by_id(clubs, a['@club'], 'name'),
        'country': a['@country'],
        'birthdate': parse_date(a['@dateofbirth'][:10], '%Y-%m-%d') if '@dateofbirth' in a else None,
        'birthyear': a['@yearofbirth'],
        'firstname': a['@forename'],
        'lastname': a['@lastname'],
        'id': a['@id'],
        'licencenumber': a['@licencenumber'],
        'bib': a['@number'],
        'sex': 'male' if a['@sex'] == 'M' else ('female' if a['@sex'] == 'W' else '')
    } for a in xml['athletes']['athlete']]

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


def get_results_from_lists(comp):
    for resultlist in comp['resultlists']:
        # Page with the result list
        page_result = download_html(resultlist['url'])

        # Find the date of the result list
        listheaders = page_result.find_all('div', {'class': 'listheader'})
        if len(listheaders) <= 2:
            date_string = listheaders[0].find_all('div')[-1].text.strip()[:10]
        if len(listheaders) == 3:
            date_string = listheaders[1].find_all('div')[-1].text.strip()[:10]
        resultlist['date'] = datetime.strftime(datetime.strptime(date_string, "%d.%m.%Y"), '%d-%m-%Y')

        resultlist['results'] = []
        # Each result is saved in a new <div class="entryline">
        # Only take the first <div class="roundblock">, all others are duplicates per category
        if page_result.find('div', {'class': 'roundblock'}):
            for line in page_result.find('div', {'class': 'roundblock'}).find_all('div', {"class": "entryline"}):
                result = {}
                result['bib'] = line.find('div', {'class': 'col-1'}).find('div', {'class': 'secondline'}).text.strip()
                result['result'] = line.find('div', {'class': 'col-4'}).div.text.strip()
                result['category'] = line.find_all('div', {'class': 'col-4'})[-1].find('div', {'class': 'firstline'}).text.strip()
                detail = line.find_all('div', {'class': 'col-4'})[-1].find('div', {'class': 'secondline'})
                result['event_detail'] = detail.text.strip() if detail else ''
                resultlist['results'].append(result)

            resultlist['is_highjump'] = True if resultlist['raw_name'][:4].lower() in ['hoog', 'hoch', 'high'] else False

            if resultlist['is_highjump']:
                resultlist['categories'] = {}

                page_result = download_html(resultlist['url'].replace('ResultList', 'StartList'))
                for line in page_result.find('div', {'class': 'blocktable'}).find_all('div', {"class": "entryline"}):
                    bib = line.find('div', {'class': 'col-1'}).find('div', {'class': 'secondline'}).text.strip()
                    category = line.find('div', {'class': 'col-5'}).find('div', {'class': 'firstline'}).text.strip()
                    resultlist['categories'][bib] = category


# THIS NEEDS EXTRA WORK
def parse_event_name(event_name):
    event_name_splitted = event_name.lower().split()
    if event_name_splitted[0] in ['shot', 'long', 'high'] or event_name_splitted[1] in ['horden', 'hurdles', 'hürden']:
        return event_name_splitted[0] + ' ' + event_name_splitted[1]
    return event_name_splitted[0]


def parse_event_detail(detail):
    if detail:
        if detail[-2:] == 'mm':  # Detail contains Hurdle Heights
            value = int(re.findall(r'\d+', detail)[0])
            return f' {int(value/10)}cm'  # Convert to whole cm
        elif detail[-1] == 'g':
            value = int(re.findall(r'\d+', detail)[0])
            if value >= 1000:
                return f' {value/1000:.3g}kg'  # Convert to kg with at most two decimals
            else:
                return f' {value}g'  # Leave in g for values lower than 1000g
    return ''
