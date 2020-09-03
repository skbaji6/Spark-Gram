import datetime
import json
import re

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
import pymongo
from telethon.tl.types import Message

from util import admin_cmd


no_of_posts_to_read = 5
@spark.on(admin_cmd(pattern="tmv"))
async def _(event):
    client = pymongo.MongoClient(spark.config.MONGO_DB_URL)
    db = client.samaydb
    command = event.text.split(" ")
    if len(command)>1:
        global no_of_posts_to_read
        no_of_posts_to_read = int(event.text.split(" ")[1])
    scheduler = AsyncIOScheduler()
    scheduler.add_job(tmv_scrape, 'interval', minutes=60, id='tmv_scrape_job', args=[spark,db])
    scheduler.start()


async def tmv_scrape(spark,db):
    urls_scrape_data = []
    sub_urls = []
    languages = []

    year_pattern = re.compile("((19|20)\d\d)")

    response = requests.get('https://www.1tamilmv.life/')
    soup = BeautifulSoup(response.text, 'html.parser')
    tag = soup.find('div', {'class': 'ipsWidget_inner'})
    ptags = tag.find_all("p")
    link_info = dict()
    post_count = 0
    for chi in ptags[1].children:
        if chi.name == 'br':
            post_count = post_count + 1
            link_info['urls'] = list(set(sub_urls))
            magnets = list()
            torrents = list()
            for link in link_info['urls']:
                magents_res, torrents_res, time = await get_magnet_links(link)
                magnets.extend(list(magents_res))
                torrents.extend(list(torrents_res))
                link_info['update_time'] = time
            link_info['magnets'] = magnets
            link_info['torrents'] = torrents
            link_info['languages'] = languages
            urls_scrape_data.append(link_info)
            present_post_date = datetime.datetime.strptime(link_info['update_time'], '%Y-%m-%dT%H:%M:%SZ')
            last_update = db.lastupdatedTimestamps.find_one({"_id": 'tamilmv'})
            #last_update_date = datetime.datetime.strptime(last_update['time'], '%Y-%m-%dT%H:%M:%SZ')
            if present_post_date > last_update['time']:
                db.tamilmv.find_one_and_update({'_id': link_info['_id']}, {'$set': link_info}, upsert=True)
                db.lastupdatedTimestamps.find_one_and_update({'_id': 'tamilmv'},
                                                             {'$set': {'_id': 'tamilmv', 'time': present_post_date}},
                                                             upsert=True)
                destination_user = await spark.get_entity(-1001297647039)
                for magnet in link_info['magnets']:
                    sent_message: Message = await spark.send_message(destination_user, magnet)
                    await sent_message.reply("/gleech")

            global no_of_posts_to_read
            if post_count == no_of_posts_to_read:
                break
        else:
            strong_tag = chi.find('strong')
            if not isinstance(strong_tag, int) and strong_tag is not None and len(strong_tag) > 0:
                atag = strong_tag.find('a')
                if atag is not None and len(atag) > -1:
                    sub_urls.append(atag.attrs['href'])
                text_to_analyze = strong_tag.text
                for match in re.finditer(year_pattern, text_to_analyze):
                    year = match.group()
                link_info['year'] = year
                if link_info['year'] is not None and text_to_analyze.find(link_info['year']) > -1:
                    link_info['movie_name'] = text_to_analyze[:text_to_analyze.find(link_info['year']) - 1].strip()
                    text_to_analyze = text_to_analyze.upper()
                    if text_to_analyze.find('TELUGU') > 0:
                        languages.append("Telugu")
                    if text_to_analyze.find('TAMIL') > 0:
                        languages.append("Tamil")
                    if text_to_analyze.find('HINDI') > 0:
                        languages.append("Hindi")
                    if text_to_analyze.find('MALAYALAM') > 0:
                        languages.append("Malayalam")
                    if text_to_analyze.find('KANNADA') > 0:
                        languages.append("Kannada")
                    if text_to_analyze.find('ENGLISH') > 0 or text_to_analyze.find('ENG') > 0:
                        languages.append("English")
                    link_info['_id'] = text_to_analyze


async def get_magnet_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    magnets = set()
    torrents = set()
    for ptag in soup.find_all('p'):
        for atag in ptag.find_all('a'):
            href = atag.get('href', None)
            if href and (href.startswith("magnet")):
                magnets.add(href)
    for atorrent in soup.find_all('a', {'class': 'ipsAttachLink'}):
        span = atorrent.find('span')
        if span is not None and "torrent" in span.text:
            href = atorrent.get('href', None)
            if href and "attachment" in href:
                torrents.add(href)
    header_division = soup.find('div', {'class': 'ipsPageHeader ipsClearfix'})
    time = header_division.find('time').get('datetime')

    return magnets, torrents, time
