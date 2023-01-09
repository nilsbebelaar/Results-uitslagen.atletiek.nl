import requests
import xmltodict
from bs4 import BeautifulSoup
from datetime import datetime
from app.main.categories import category_to_gender, category_to_hurdleheight, category_to_weight
from app.main.load_data import save_export
from app.models import Competitions


BASE_URL = 'https://uitslagen.atletiek.nl'
headers = {'accept-language': 'nl'}


def save_download(comp):
    for athlete in comp['athletes']:
        athlete.pop('id', None)
    athletes = [a for a in comp['athletes'] if int(a['licencenumber']) != 0]
    athletes_no_number = [a for a in comp['athletes'] if int(a['licencenumber']) == 0]
    save_export(athletes, comp['id'])
    save_export(athletes_no_number, comp['id'], '_no_licencenumber')


def async_download_competition_results(app, id, full_reload=False):
    with app.app_context():
        comp = Competitions.load_dict(id)
        if not comp:
            return
        if full_reload:
            get_competition_info_xml(comp)
        get_results_from_lists(comp)
        find_results(comp)
        save_download(comp)
        comp['status'] = 'Ready'
        Competitions.save_dict(comp)


def find_results(comp):
    for athlete in comp['athletes']:
        athlete['competition'] = {
            'name': comp['name'],
            'location': comp['location'],
            'type': comp['type'],
            'url': comp['url']
        }
        athlete['results'] = []
        # For every athlete, loop through all results
        for resultlist in comp['resultlists']:
            for result in resultlist['results']:
                # If a athlete's bib-number exists in the results, append the result to the athlete['results'] list
                if athlete['bib'] == result['bib']:
                    if result['category'] in ['MASTERSM', 'MASTERSV']:
                        result['category'] = result['category'] + ' ' + athlete['birthyear']
                    athlete['results'].append({
                        'event': parse_event_name(resultlist['event_name_raw'], result['category'], athlete['birthyear']),
                        'result': result['result'],
                        'url': resultlist['url'],
                        'date': resultlist['date'],
                        'category': result['category']
                    })
                    # competitor['SELTECLOOKUP'] = "1"  # Empty field needed because tussenvoegsels are not published

    # Remove competitors if the have no results
    comp['athletes'] = [athlete for athlete in comp['athletes'] if athlete['results']]


def get_competition_info_xml(comp):
    comp['url'] = BASE_URL + '/Competitions/Details/' + str(comp['id'])
    session = requests.session()

    # XML page with competition information
    response = session.get(comp['url'] + '/ladvxml', headers=headers)
    xml = xmltodict.parse(response.text, process_namespaces=True)

    xml = xml['meetingresult']

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
        'sex': a['@sex']
    } for a in xml['athletes']['athlete']]

    comp['days'] = calc_day_difference(comp['begindate'], comp['enddate'], '%Y-%m-%d') + 1

    comp['resultlists'] = []
    # Find all result lists, for each day
    for day in range(comp['days']):
        response = session.get(comp['url'] + '/' + str(day + 1), headers=headers)
        page_competition = BeautifulSoup(response.text, 'html.parser')
        for block in page_competition.find_all('div', {'class': 'blockcontent'}):
            for a in block.find_all('a'):
                resultlist = {}
                resultlist['url'] = BASE_URL + a['href']
                resultlist['raw_name'] = a.find('div', {'class': 'mainname'}).text.strip()
                comp['resultlists'].append(resultlist)
    session.close()


def calc_day_difference(startdate_string, enddate_string, format):
    return (datetime.strptime(enddate_string, format) - datetime.strptime(startdate_string, format)).days


def parse_date(date_string, format_in, format_out='%d-%m-%Y'):
    return datetime.strftime(datetime.strptime(date_string, format_in), format_out)


def find_by_id(searchlist, id, searchindex):
    return [c[searchindex] for c in searchlist if c['id'] == id][0]


def get_results_from_lists(comp):
    session = requests.session()
    for resultlist in comp['resultlists']:
        # Page with the result list
        response = session.get(resultlist['url'], headers=headers)
        page_result = BeautifulSoup(response.text, 'html.parser')

        # Name of result list is part of <div class="leftheader">
        resultlist['event_name_raw'] = page_result.find('div', {'class': 'leftheader'}).text.strip()

        # Find the date of the result list
        date_string = page_result.find('div', {'class': 'listheader'}).find_all('div')[-1].text.strip()[:10]
        resultlist['date'] = datetime.strftime(datetime.strptime(date_string, "%d.%m.%Y"), '%d-%m-%Y')

        resultlist['results'] = []
        # Each result is saved in a new <div class="entryline">
        # Only take the first <div class="roundblock">, all others are duplicates per category
        for line in page_result.find('div', {'class': 'roundblock'}).find_all('div', {"class": "entryline"}):
            result = {}
            result['bib'] = line.find('div', {'class': 'col-1'}).find('div', {'class': 'secondline'}).text.strip()
            result['result'] = line.find('div', {'class': 'col-4'}).div.text.strip()
            result['category'] = line.find_all('div', {'class': 'col-4'})[-1].find('div', {'class': 'firstline'}).text.strip()
            resultlist['results'].append(result)
    session.close()


# THIS NEEDS EXTRA WORK
def parse_event_name(event_name, category, birthyear):
    event_name_splitted = event_name.lower().split()
    if event_name_splitted[1] == 'horden':
        distance = event_name_splitted[0][:-1]
        return ' '.join(event_name_splitted[:2]) + category_to_hurdleheight(category, distance, birthyear)
    elif event_name_splitted[0] in ['kogelstoten', 'speerwerpen', 'gewichtwerpen', 'kogelslingeren', 'discuswerpen']:
        distance = event_name_splitted[0][:-1]
        return ' '.join(event_name_splitted[:1]) + category_to_weight(event_name_splitted[0], category, birthyear)
    else:
        return event_name_splitted[0]
