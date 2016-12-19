# coding:utf-8

import json
import time
import requests
from pprint import pprint


def post_api(method=None, data=None, url=None):
    # 请求api，返回响应码、接口响应时间
    start_time = time.time()
    resp = requests.request(method=method, params=data, url=url)
    status = {
        'http_code': resp.status_code,
        'time': time.time() - start_time
    }
    return status


def get_api_info(request_data, order_id):
    # 获取api的method、url、以及参数数据
    api_info = {}
    for request in request_data:
        if request['id'] == order_id:
            api_info['url'] = request['url'].replace('{{host}}', 'https://host.domain.com.cn/project/')
            api_info['api_name'] = request['url'].split('/')[-1]
            api_info['method'] = request['method']
            if request['data'] is None:
                api_info['data'] = 'None'
            else:
                api_info['data'] = {item['key']: item['value'] for item in request['data']}
    return api_info


if __name__ == '__main__':
    # 读取Postman export的json文件
    with open('/prodata/scripts/zabbix/uair_api.json', encoding='utf8') as f:
        data = json.load(f)
        project_name = data['name']
        all_data = {}
        for floder_data in data['folders']:
            floder_name = floder_data['name']
            all_data[floder_name] = {}
            for order_id in floder_data['order']:
                order_info = get_api_info(data['requests'], order_id)
                all_data[floder_name][order_info['api_name']] = post_api(order_info['method'], order_info['data'], order_info['url'])
        f = open('/prodata/scripts/zabbix/api_status.json', 'w')
        f.write(json.dumps(all_data))
