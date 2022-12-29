import requests
import pyperclip
from bs4 import BeautifulSoup
import json

COMP_ID = 8702
BASE_URL = 'https://uitslagen.atletiek.nl'

def main():
    resultlists = get_resultlists(COMP_ID)
    competitors = get_competitors(COMP_ID)
    competitors = find_results(resultlists, competitors)

    json_string = json.dumps(competitors)
    pyperclip.copy(json_string) #Copy the json to clipboard
    print(json_string)


def find_results(resultlists, competitors):
    for competitor in competitors:
        competitor['results'] = []
        #For every competitor, loop through all resultlists
        for resultlist in resultlists:
            for result in resultlist['results']:
                #If a competitor's bib-number exists in the results, append the result to the competitor['results'] list
                if result['bib'] == competitor['bib']:
                    competitor['results'].append({'event': resultlist['event_name'], 'result': result['result']})
    return competitors


def get_competitors(competition_id):
    url = BASE_URL + '/Competitions/Competitoroverview/' + str(competition_id)
    session = requests.session()

    soup = BeautifulSoup(session.get(url).text, 'html.parser')

    competitors = []
    for line in soup.find('div', {'class': 'blocktable'}).find_all('div', {'class': 'entryline'}):
        competitor = {}
        competitor['bib'] = line.find('div', {'class': 'col-1'}).find('div', {'class': 'firstline'}).text.strip()
        competitor['name'] = line.find('div', {'class': 'col-2'}).find('div', {'class': 'firstline'}).text.strip()
        competitor['club'] = line.find('div', {'class': 'col-2'}).find('div', {'class': 'secondline'}).text.strip()
        competitor['birthyear'] = line.find('div', {'class': 'col-42p'}).find('div', {'class': 'secondline'}).text.strip()
        competitors.append(competitor)

    session.close()
    return competitors


def get_resultlists(competition_id):
    url = BASE_URL + '/Competitions/Details/' + str(competition_id)
    session = requests.session()

    soup = BeautifulSoup(session.get(url).text, 'html.parser')

    resultlists = []

    data = soup.find_all('div', {'class': 'blockcontent'})
    for block in soup.find_all('div', {'class': 'blockcontent'}):
        for a in block.find_all('a'):
            list_url = BASE_URL + a['href']
            resultlists.append({'url': list_url})

    for resultlist in resultlists:
        soup = BeautifulSoup(session.get(resultlist['url']).text, 'html.parser')

        # Name of resultlist is part of <div class="leftheader">
        resultlist['event_name'] = parse_event_name(soup.find('div', {'class': 'leftheader'}).text.strip())

        resultlist['results'] = []
        # Each result is saved in a new <div class="entryline">
        # Only take the first <div class="roundblock">, all others are duplicates per category
        for line in soup.find('div', {'class': 'roundblock'}).find_all('div', {"class": "entryline"}):
            result = {}
            result['bib'] = line.find('div', {'class': 'col-1'}).find('div', {'class': 'secondline'}).text.strip()
            result['name'] = line.find('div', {'class': 'col-2'}).find('div', {'class': 'firstline'}).text.strip()
            result['club'] = line.find('div', {'class': 'col-2'}).find('div', {'class': 'secondline'}).text.strip()
            result['birthyear'] = line.find('div', {'class': 'col-3'}).find('div', {'class': 'secondline'}).text.strip()
            result['result'] = line.find('div', {'class': 'col-4'}).div.text.strip()
            resultlist['results'].append(result)

    session.close()
    return resultlists

#THIS NEEDS EXTRA WORK
def parse_event_name(event_name):
    if event_name.split()[1] == 'Horden':
        return ' '.join(event_name.split()[:2])
    else:
        return event_name.split()[0]

if __name__ == '__main__':
    main()
