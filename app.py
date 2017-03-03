#!/usr/bin/env python3

import hug
import re
import urllib
import datetime
from pymongo import MongoClient
from bson.json_util import dumps
from bs4 import BeautifulSoup

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DB = 'tvgraph'
MONGO_COLLECTION = 'tvseries'
MONGO_USER = 'tvgraph'
MONGO_PASSWORD = 'tvgraph123'


client = MongoClient(MONGO_HOST, MONGO_PORT)
dba = client[MONGO_DB]
dba.authenticate(MONGO_USER, MONGO_PASSWORD, mechanism='SCRAM-SHA-1')
db = dba[MONGO_COLLECTION]


@hug.get('/{show}', output=hug.output_format.html)
def test(show):
    id_pattern = re.compile(r"^tt\d{7}$")
    if show != "" and not id_pattern.match(show): return hug.redirect.to('/')
    with open('index.html') as f:
        return f.read()

@hug.get('/hcr.js', output=hug.output_format.html)
def index():
    with open('hcr.js') as f:
        return f.read()

@hug.get('/singleseries.js', output=hug.output_format.html)
def index():
    with open('highcharts-singleseries/singleseries.js') as f:
        return f.read()               

@hug.get('/favicon.ico', output=hug.output_format.ico_image)
def index():
    return 'favicon.ico'

@hug.get('/search/{query}')
def search(query):
    """ First, we get a search query from the user and see if it's an IMDB ID or not.
        If it's an ID, we try to get the show by ID.
        If it's a show name, we try to find it in our local DB and if we fail,
        we use the IMDB search.
    """
    id_pattern = re.compile(r"^tt\d{7}$")
    if id_pattern.match(query): return get_show(query)

    try:
        doc = db.find_one({'$text': {'$search': '\"' + query + '\"'}})
    except Exception:
        return False
    if doc:
        print("Found match in the local DB")
        return dumps(doc)
    else:
        print("Local match not found, searching IMDB")
        return search_imdb(query)

def search_imdb(show_name):
    """ Using IMDB search by show name.
        If found, we try to get the show by ID.
        If not found, returning False.
    """
    print('searching IMDB with query: ' + show_name)
    link = 'http://www.imdb.com/find?s=tt&ttype=tv&q=' + urllib.parse.quote(show_name)
    print('Getting search page: ' + link)
    page = urllib.request.urlopen(link).read()
    print('Received search page')
    soup = BeautifulSoup(page, 'lxml')
    print('parsing search page with soup')
    if not soup.find(class_="findList"):
        print('No results found')
        return False
    else:
        show_full_url = soup.table.tr.find_all('td')[1].a['href']
        show_url = show_full_url.split('/')[2]
        print('Found match on IMDB, getting that show')
        return get_show(show_url)

def get_show(show_id):
    """ Getting the show from our local DB using its ID.
        If found, checking that it's a show and returning it.
        This prevents unnecessary requests to IMDB for things that we know are not shows.
        If not found, we need to add it to DB by parsing its IMDB page.
    """
    try:
        doc = db.find_one({"show_id": show_id})
    except Exception:
        return False
    if doc:  # cache hit
        return dumps(doc) if doc['show'] else False
    else:
        try:
            link = "http://www.imdb.com/title/" + show_id + "/epdate"
            print('Getting page ' + link)
            page = urllib.request.urlopen(link).read()
            print('Received page')
            print("Cache miss, parsing page " + link)
            if parse_page(page, show_id):
                print("Parsing completed, refreshing")
                return get_show(show_id)
            else:
                print('something went')
                return False
        except Exception as e:
            print(e)
            return None

def parse_page(page, show_id):
    """ Parsing the IMDB show page using BeautifulSoup.
        If it's not a show, marking it as such in the DB.
        When done, requesting the show by ID again, knowing it's going to be in the database.
    """
    soup = BeautifulSoup(page, 'lxml')
    seasons = {}
    if not soup.find('h4'):  # not a show
        mongo_id = db.insert_one(
            {
                "show_id": show_id,
                "show": False
            })
        return False
    print('Starting to parse')
    show_title = re.findall(r'"(.*?)"', soup.title.text)[0]
    show_year = int(re.findall(r'\((.*?)\)', soup.title.text)[0])
    show_full_url = soup.find('link', {'rel': 'canonical'})['href']
    show_id = show_full_url.split('/')[4]
    show_poster_link = soup.find(id="primary-poster")['src']
    show_poster = urllib.request.urlopen(show_poster_link).read()

    seq_num = 0
    for tr in soup.table.find_all('tr'):
        td = tr.find_all('td')
        if td:  # one tr in table = one episode except for the first tr which doesn't have td
            seq_num += 1
            episode = {}
            full_number = td[0].text.replace(u'\xa0', u'')
            if full_number == '-': break  # this is to skip unnumbered episodes that have '-' for a number
            season_number, episode_number = full_number.split('.')
            episode['season_number'] = season_number
            episode['episode_number'] = episode_number
            episode['episode_title'] = td[1].text
            episode['episode_votes'] = int(td[3].text.replace(',', ''))
            episode['episode_id'] = td[1].find('a')['href'].split('/')[2]
            episode['x'] = seq_num
            episode['y'] = float(td[2].text)
            seasons.setdefault("_"+season_number, []).append(episode)  # some magic here
    mongo_id = db.insert_one({
        "show" : True,
        "show_title" : show_title,
        "show_year" : show_year,
        "show_id" : show_id,
        "show_poster" : show_poster,
        "created_at" : datetime.datetime.utcnow(),
        "seasons": seasons
        })
    print('Parsing complete')
    return True

"""
TODO:
- recent viewed shows history list (use localstorage instead of cookies)
"""