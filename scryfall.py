import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.parse
import json
import sys

HEADERS = {'accept': 'application/json'}
REPLACE_THESE_IN_FILE_NAMES = ['#','%','&','{','}','\\','<','>','*','?','/','$','!','\'','"',':','@','+','`','|','=', ' ']


def replace_in_string(text):
    for char in REPLACE_THESE_IN_FILE_NAMES:
        if char in text:
            if char == '\'':
                text = text.replace(char, '')
            else:
                text = text.replace(char, '-')
    return text


def parse_csv(csv):
    query = ''
    with open(csv, 'r+') as f:
        for line in f.readlines():
            l = '!' + '\"' + line.replace('\n', '').replace('\"', '') + '\"'
            query += urllib.parse.quote(l.encode('utf8')) + '+or+'
    return query.strip('+or+')


def write_to_csv(csv, content):
    with open(csv, 'wb') as f:
        f.write(content)


class Scryfall():

    def __init__(self):
        self.scryfall_api_url = 'https://api.scryfall.com'
        self.scryfall_delay = 1  # Second(s)
        self.session = None

    def start_session(self):
        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def get(self, url):
        r = self.session.get(url, headers=HEADERS)
        time.sleep(self.scryfall_delay)
        return r

    def get_sets_raw(self):
        url = '/'.join([self.scryfall_api_url, 'sets'])
        r = self.get(url)
        return r

    def card_search(self, query):
        url = '/'.join([self.scryfall_api_url, 'cards', 'search'])
        url_with_query = url + '?format=csv&q=' + query
        r = self.get(url_with_query)
        return r

    def download_card(self):
        try:

        except Exception as e:
            print(e)

    def search_set(self, **kwargs):
        set_code = None
        for k, v in kwargs.items():
            if k == 'set_code':
                set_code = v
        url = '/'.join([self.scryfall_api_url, 'sets', set_code])
        r = self.get(url)
        set_end_point = self.get(r.json()['search_uri']).json()
        cards = set_end_point['data']
        for card in cards:
            if 'card_faces' in card:
                for double_card in card['card_faces']:
                    png = self.get(double_card['image_uris']['png'])
                    name = replace_in_string(double_card['name'])
                    print(f'{name}.png')
                    with open(f'{name}.png', 'wb') as f:
                        f.write(png.content)
                    time.sleep(2)
            else:
                name = replace_in_string(card['name'])
                png = self.get(card['image_uris']['png'])
                print(f'{name}.png')
                with open(f'{name}.png', 'wb') as f:
                    f.write(png.content)
                time.sleep(2)
        return r.json()

    def run(self):
        self.start_session()
        # q = parse_csv('input.csv')
        r = self.search_set(set_code='neo')
        # write_to_csv('scryfall.csv', r.content)


s = Scryfall()
s.run()
