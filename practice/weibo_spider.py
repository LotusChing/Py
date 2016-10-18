# coding:utf-8
import logging
import requests
import datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient


base_url = 'http://weibo.cn'
airport_url = base_url + '/bjairport'
date = datetime.datetime.now().strftime("%Y-%m-%d")
date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' '
logging.basicConfig(filename='console.log', level=logging.INFO, format='%(asctime)s  %(levelname)s [%(processName)s] '
                                                                       + '[%(threadName)s] - %(message)s')

def web_data(url):
    data = requests.get(url)
    soup = BeautifulSoup(data.text, 'lxml')
    return soup


def mongo_db_conn(**kwargs):
    user = kwargs['user']
    passwd = kwargs['passwd']
    host = kwargs['host']
    port = kwargs['port']
    client = MongoClient(host, port)
    db = client[kwargs['db']]
    db.authenticate(user, passwd, source=kwargs['db'])
    return db


def get_weather_data(url):
    soup = web_data(url)
    try:
        return [data.get_text().strip('【国门早知道】') for data in soup.select('div > span.ctt') if '国门早知道' in str(data)][0]
    except IndexError as f:
        logging.warning(f)
        return 1


def spider(soup, url):
    try:
        logging.info('Try to get weather information from full text page.')
        full_text_url = [data.a['href'] for data in soup.select('div > span.ctt') if '国门早知道' in str(data)][0]
        logging.info('Get full text ok.')
        weather_info_url = base_url + full_text_url
        data = requests.get(weather_info_url)
        soup = BeautifulSoup(data.text, 'lxml')
        weather_info = str(soup.select('div > span.ctt')[0].get_text()).strip(':【国门早知道】')
        logging.info('Get weather information successful.')
        return weather_info
    except Exception as f:
        logging.warning(f)
        logging.info('Try to get the weather information from single page.')
        weather_info = get_weather_data(url)
        logging.info('Get weather info ok.')
        return weather_info


def latest_data(db, tb):
    coll = db[tb]
    old_data = [i for i in coll.find({}, {'id': 1, 'content': 1, '_id': 0}).sort("id", -1).limit(1)][0]
    return old_data


def newtest_data(data, weather_info):
    newtest_id = int(data['id'])
    newtest_id += 1
    weather_data = {
                    "id": str(newtest_id),
                    "addTime": date_time,
                    "checkTime": date_time,
                    "content": weather_info,
                    "keys": "",
                    "limitTime": date_time,
                    "state": "2",
                    "onlinestate": "1",
                    "loginUserName": "zyw",
                    "title": weather_info,
                    "type": "1",
                    "updateTime": date_time
                    }

    return weather_data


def mongo_insert_doc(db, tb, data):
    try:
        coll = db[tb]
        coll.insert(data)
        logging.info('Insert weather information to mongodb success')
        return 0
    except Exception as f:
        logging.warning(f)
        return 1


def judge(latest_info, newtest_info):
    if latest_info == newtest_info:
        logging.info('Already release weather information to app.')
        return 1
    else:
        logging.info('Starting release weather informaton to app.')
        weather_data = newtest_data(old_data, weather_info)
        mongo_insert_doc(db, 'announcement', weather_data)
        logging.info('Successful release weather inforamtion to app.')
        return 0


if __name__ == '__main__':
    soup = web_data(airport_url)
    weather_info = spider(soup, airport_url)
    db = mongo_db_conn(user='user', passwd='passwd', host='host', port=port, db='db')
    old_data = latest_data(db, 'announcement')
    judge(old_data['content'], weather_info)