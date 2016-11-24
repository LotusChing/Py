# coding:utf-8

import json
import requests


def post_api(method=None, data=None, url=None):
    api_name = url.split('/')[-1]
    resp = requests.request(method=method, params=data, url=url)
    text = json.loads(resp.text)
    if resp.status_code != 200 or text['code'] != 1:
        print('{}  Failed.'.format(api_name))
        print(resp.text)
    else:
        print('{}  Successful.'.format(api_name))


def orders(data, order_id):
    order_data = {}
    requests_data = data['requests']
    for request in requests_data:
        if request['id'] == order_id:
            order_data['url'] = request['url'].replace('{{host}}', 'http://106.14.37.210/UAirServer/app/')
            order_data['method'] = request['method']
            if request['data'] is None:
                order_data['data'] = 'None'
            else:
                order_data['data'] = {item['key']: item['value'] for item in request['data']}
            post_api(order_data['method'], order_data['data'], order_data['url'])
    return order_data


def floders(data):
    floders_data = data['folders']
    for floder in floders_data:
        floder_name = floder['name']
        floder_order = floder['order']
        print(floder_name)
        for order_id in floder_order:
            order_data = orders(data, order_id)
           # print('\t', order_data)
    return 0

if __name__ == '__main__':
    with open('UAirServer.postman_collection') as f:
        data = json.load(f)
        project_name = data['name']
        floder_data = floders(data)
