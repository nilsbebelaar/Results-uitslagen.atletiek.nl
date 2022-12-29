import requests
import pyperclip
from bs4 import BeautifulSoup
import json
from datetime import datetime
from categories import category_to_gender, category_to_hurdleheight

COMP_TYPE = 'indoor'
COMP_ID = 8702

BASE_URL = 'https://uitslagen.atletiek.nl'
headers = {'accept-language': 'nl'}


def main():
    competition = {'id': COMP_ID, 'type': COMP_TYPE}
    competition = get_resultlists(competition)
    competition = get_registrations(competition)
    competition = find_results(competition)

    # Create JSON from competition['competitors']
    json_string = json.dumps(competition['competitors'], sort_keys=True, indent=2, ensure_ascii=False)
    # Copy JSON to clipboard for easy pasting
    pyperclip.copy(json_string)

    # Export JSON to file in /export directory
    filename = f"export/export_{competition['id']}.json"
    with open(filename, 'w') as outfile:
        outfile.write(json_string)

    print(f"{competition['name']} was exported to {filename} and copied to clipboard.")


def find_results(competition):
    competition['competitors'] = []
    for resultlist in competition['resultlists']:
        for result in resultlist['results']:
            # For every result, loop through all competitors
            for competitor in competition['registrations']:
                # If a competitor's bib-number exists in the results, append the result to the competitor['results'] list
                if result['bib'] == competitor['bib']:
                    competitor['competition'] = {
                        'name': competition['name'],
                        'location': competition['location'],
                        'type': competition['type']
                    }
                    competitor['category'] = result['category']
                    competitor['gender'] = result['gender']
                    competitor['results'].append({
                        'event': parse_event_name(resultlist['event_name_raw'], competitor['category']),
                        'result': result['result'],
                        'url': resultlist['url_result'],
                        'date': datetime.strftime(resultlist['date'], '%d-%m-%Y'),
                        # Temp hack for linking in atletiek.nu
                        'event-category': f"{parse_event_name(resultlist['event_name_raw'], competitor['category'])} {competitor['category']}"
                    })
                    competitor['SELTECLOOKUP'] = "1"  # Empty field needed because tussenvoegsels are not published
                    competition['competitors'].append(competitor)
    return competition


def get_registrations(competition):
    url = BASE_URL + '/Competitions/Competitoroverview/' + str(competition['id'])
    session = requests.session()

    # Page with all registrations of the competition
    page_registrations = BeautifulSoup(session.get(url, headers=headers).text, 'html.parser')

    competition['registrations'] = []
    for line in page_registrations.find('div', {'class': 'blocktable'}).find_all('div', {'class': 'entryline'}):
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

    # Page with competition information and all result lists
    page_competition = BeautifulSoup(session.get(url, headers=headers).text, 'html.parser')

    title = page_competition.find('h1').text.strip()
    # Competition name is stored after the date, but some competitions are split over multiple days:
    # 1: '18 dec 2022 <name> - <city>'
    # 2: '08 - 09 okt 2022 <name> - <city>'
    # So we check for the '-' at index [3], and we rfind() the last '-' to get its index, we can then extract the name
    split_index = title.rfind('-')
    competition['name'] = title[17:split_index-1] if title[3] == '-' else title[12:split_index-1].strip()
    competition['location'] = title[split_index+1:].strip()

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
        # Page with the result list
        page_result = BeautifulSoup(session.get(resultlist['url_result'], headers=headers).text, 'html.parser')

        # Name of result list is part of <div class="leftheader">
        resultlist['event_name_raw'] = page_result.find('div', {'class': 'leftheader'}).text.strip()

        # Find the date of the result list
        date_string = page_result.find('div', {'class': 'listheader'}).find_all('div')[-1].text.strip()[:10]
        resultlist['date'] = datetime.strptime(date_string, "%d.%m.%Y")

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
        page_registrations = BeautifulSoup(session.get(resultlist['url_registrations'], headers=headers).text, 'html.parser')
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
def parse_event_name(event_name, category):
    event_name_splitted = event_name.lower().split()
    if event_name_splitted[1] == 'horden':
        distance = event_name_splitted[0][:-1]
        return ' '.join(event_name_splitted[:2]) + category_to_hurdleheight(category, distance)
    else:
        return event_name_splitted[0]


if __name__ == '__main__':
    main()
