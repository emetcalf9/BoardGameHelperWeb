import requests
import xml.etree.ElementTree as ET

BASE_URL = 'https://boardgamegeek.com/xmlapi2/'


# response = requests.get(BASE_URL + 'thing', {'id': '13'})
# tree = ET.fromstring(response.text)
# name = tree.find('./item/name[@type="primary"]').get('value')
# print(name)


def search_games(name):
    URL = BASE_URL + 'search'
    exact_search = ET.fromstring(requests.get(URL, [('query', name), ('type', 'boardgame'), ('exact', '1')]).text)
    if exact_search:
        result = exact_search.find('item')
        game = [(result.get('id'), result.find('name').get('value'))]
        return game
    else:
        response = ET.fromstring(requests.get(URL, [('query', name), ('type', 'boardgame')]).text)
        results = response.findall('item')
        game_list = []
        for game in results:
            game_list.append((game.get('id'), game.find('name').get('value')))
        return game_list


def get_game_info(id):
    URL = BASE_URL + 'thing'
    game = ET.fromstring(requests.get(URL, {'id': id}).text).find('item')
    name = game.find('./name[@type="primary"]').get('value')
    minPlay = game.find('minplayers').get('value')
    maxPlay = game.find('maxplayers').get('value')
    return (id, name, minPlay, maxPlay)
