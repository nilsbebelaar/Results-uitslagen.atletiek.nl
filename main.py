import requests
import pyperclip
from bs4 import BeautifulSoup
import json
from categories import category_to_gender

COMP_TYPE = 'indoor'
COMP_ID = 8702
BASE_URL = 'https://uitslagen.atletiek.nl'


def main():
    competition = {'id': COMP_ID, 'type': COMP_TYPE}
    competition = get_resultlists(competition)
    competition = get_registrations(competition)
    competition = find_results(competition)

    json_string = json.dumps(competitors)
    pyperclip.copy(json_string)  # Copy the json to clipboard
    print(json_string)




def find_results(competition):
    competition['competitors'] = []
    for resultlist in competition['resultlists']:
        for result in resultlist['results']:
            # For every result, loop through all competitors
            for competitor in competition['registrations']:
                # If a competitor's bib-number exists in the results, append the result to the competitor['results'] list
                if result['bib'] == competitor['bib']:
                    competitor['category'] = result['category']
                    competitor['gender'] = result['gender']
                    competitor['results'].append({
                        'event': resultlist['event_name'],
                        'result': result['result'],
                        'url': resultlist['url_result']
                    })
                    competition['competitors'].append(competitor)
    return competition


def get_registrations(competition):
    url = BASE_URL + '/Competitions/Competitoroverview/' + str(competition['id'])
    session = requests.session()

    soup = BeautifulSoup(session.get(url).text, 'html.parser')

    for line in soup.find('div', {'class': 'blocktable'}).find_all('div', {'class': 'entryline'}):
    competition['registrations'] = []
        competitor = {}
        competitor['bib'] = line.find('div', {'class': 'col-1'}).find('div', {'class': 'firstline'}).text.strip()
        competitor['name'] = line.find('div', {'class': 'col-2'}).find('div', {'class': 'firstline'}).text.strip()
        competitor['club'] = line.find('div', {'class': 'col-2'}).find('div', {'class': 'secondline'}).text.strip()
        competitor['birthyear'] = line.find('div', {'class': 'col-42p'}).find('div', {'class': 'secondline'}).text.strip()
        competitor['results'] = []
        competition['registrations'].append(competitor)

    session.close()
    return competition


def get_resultlists(competition):
    url = BASE_URL + '/Competitions/Details/' + str(competition['id'])
    session = requests.session()

    page_competition = BeautifulSoup(session.get(url).text, 'html.parser')


    competition['resultlists'] = []
    # Find all result lists
    for block in page_competition.find_all('div', {'class': 'blockcontent'}):
        for a in block.find_all('a'):
            result_url = BASE_URL + a['href']
            register_url = result_url.replace('CurrentList', 'RegisterList')
            # Save the result url as well as the url with all registrations
            # Registrations are needed as the catergory is not visible on the results page
            competition['resultlists'].append({'url_result': result_url, 'url_registrations': register_url})

    for resultlist in competition['resultlists']:

        page_result = BeautifulSoup(session.get(resultlist['url_result']).text, 'html.parser')

        # Name of resultlist is part of <div class="leftheader">
        resultlist['event_name'] = parse_event_name(page_result.find('div', {'class': 'leftheader'}).text.strip())

        resultlist['results'] = []
        # Each result is saved in a new <div class="entryline">
        # Only take the first <div class="roundblock">, all others are duplicates per category
        for line in page_result.find('div', {'class': 'roundblock'}).find_all('div', {"class": "entryline"}):
            result = {}
            result['bib'] = line.find('div', {'class': 'col-1'}).find('div', {'class': 'secondline'}).text.strip()
            result['name'] = line.find('div', {'class': 'col-2'}).find('div', {'class': 'firstline'}).text.strip()
            result['club'] = line.find('div', {'class': 'col-2'}).find('div', {'class': 'secondline'}).text.strip()
            result['birthyear'] = line.find('div', {'class': 'col-3'}).find('div', {'class': 'secondline'}).text.strip()
            result['result'] = line.find('div', {'class': 'col-4'}).div.text.strip()
            resultlist['results'].append(result)

        # Competitor categories are only shown on the registration page
        page_registrations = BeautifulSoup(session.get(resultlist['url_registrations']).text, 'html.parser')
        for result in resultlist['results']:
            # Check each result
            for line in page_registrations.find_all('div', {"class": "entryline"}):
                bib = line.find('div', {'class': 'col-1'}).find('div', {'class': 'firstline'}).text.strip()
                # Compare the result to every line in the registrations, if the bib numbers match, save the category and gender
                if result['bib'] == bib:
                    result['category'] = line.find('div', {'class': 'col-5'}).find('div', {'class': 'firstline'}).text.strip()
                    result['gender'] = category_to_gender(result['category'])

    session.close()
    return competition


# THIS NEEDS EXTRA WORK
def parse_event_name(event_name):
    if event_name.split()[1] == 'Horden':
        return ' '.join(event_name.split()[:2])
    else:
        return event_name.split()[0]


if __name__ == '__main__':
    main()
