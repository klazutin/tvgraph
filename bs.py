#!/bin/env python3

import urllib.request
from pymongo import MongoClient
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import re

def parse_page(page):
    soup = BeautifulSoup(page, 'lxml')
    table = soup.table
    season_episodes = {}
    seasons = []
    for tr in table.find_all('tr'):  # one tr in table = 1 episode except for the first
        tdl = tr.find_all('td')
        if tdl:
            episode = {}
            full_number = tdl[0].text.replace(u'\xa0', u'')
            season_number = full_number.split('.')[0]
            episode_number = full_number.split('.')[1]
            episode['season_number'] = season_number
            episode['episode_number'] = episode_number
            episode['episode_title'] = tdl[1].text
            episode['episode_rating'] = tdl[2].text
            episode['episode_votes'] = tdl[3].text
            episode['episode_url'] = tdl[1].find('a')['href']
            season_episodes[episode_number] = episode
            # season_episodes.append(episode)
            # seasons[season_number] = season_episodes
    seasons.append(season_episodes)
    show = {}
    show['title'] = re.findall(r'"(.*?)"', soup.title.text)[0]
    for link in soup.find_all('link'):
        if 'canonical' in link['rel']:
            show_full_url = link['href']
    show['url'] = "/title/" + show_full_url.split('/')[4]
    show['seasons'] = seasons
    print(json.dumps(show))
    # return season_episodes


def get_page(link):
    http = urllib.request.urlopen(link).read()
    return http


def add_to_db(item):
    client = MongoClient()
    db = client.test
    collection = db.tvseries
    # bj = {"title": "BoJack Horseman",
    #       "seasons": 2}
    collection.insert(item)


# parse_page(open('bj.html'))
parse_page(get_page('http://www.imdb.com/title/tt3488298/eprate'))


"""
MongoDB object schema:
object: {
    "show_title": "BoJack Horseman",
    "show_num": "tt3398228" //for db searches, indexed field
    "show_url": "http://www.imdb.com/title/tt3398228",
    "seasons": {
        1: {
            1: {
                "episode_title": "BoJack Horseman: The BoJack Horseman Story, Chapter One",
                "episode_rating": "7.2",
                "episode_url": "http://www.imdb.com/title/tt3957774/"
            },
            2: {
                "episode_title": "BoJack Hates the Troops",
                "episode_rating": "7.8",
                "episode_url": "http://www.imdb.com/title/tt3982374/"
            }
        },
        2:
            1: {
                "episode_title": "Brand New Couch",
                "episode_rating": "8.2",
                "episode_url": "http://www.imdb.com/title/tt4311472/"
            },
            2: {
                "episode_title": "Yesterdayland",
                "episode_rating": "8.1",
                "episode_url": "http://www.imdb.com/title/tt4835722/"
            }
    }
}
"""
