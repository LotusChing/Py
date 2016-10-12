# coding:utf-8

import os
import re
import sys
import smtplib
import logging
import datetime
import requests
import threading
from email.mime.text import MIMEText

sa = ['13521095342@139.com']
event = threading.Event()
logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s [%(threadName)s] - %(message)s')
p = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) \[(?P<time>.*)\] "(?P<method>\w+) (?P<url>[^\s]+) '
               + '(?P<version>\w+/\d\.\d)" (?P<status>\d+) (?P<request_length>\d+) (?P<process_time>\d+\.\d+) '
               + '(?P<response_size>\d+) (?P<upstream_server>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+) '
               + '(?P<referer>[^\s]+) (?P<ua>.*)')


trigger_rules = {
    'client': 0.5,
    'server': 0.3
}


def read_log(path):
    # TODO multi thread
    offset = 0
    while not event.is_set():
        with open(path) as f:
            if offset > os.stat(path).st_size:
                offset = 0
            f.seek(offset)
            yield from f
            offset = f.tell()
        event.wait(0.1)


def parse(path):
    for line in read_log(path):
        m = p.search(line.rstrip('\n'))
        if m:
            data = m.groupdict()
            yield data


def agg(path, write_db_interval=10, check_error_interval=5):
    count, traffic, client_error, server_error = 0, 0, 0, 0
    start = datetime.datetime.now()
    while not event.is_set():
        logging.info('Starting agg metric data...')
        for item in parse(path):
            count += 1
            traffic += int(item['response_size'])
            if item['status'][0] == '4':
                client_error += 1
            if item['status'][0] == '5':
                server_error += 1
            current = datetime.datetime.now()

            # 每隔5s判断Web服务运行状态
            if (current - start).total_seconds() >= check_error_interval:
                client_error_rate = client_error / count
                server_error_rate = server_error / count
                print('Count: {} Traffic: {}  4xx: {}  5xx: {}'.format(count, traffic, client_error_rate, server_error_rate))
                if client_error_rate >= trigger_rules['client']:
                    notification('4xx Problem', 'Found server have {} 4xx problem, Please check server status.'.format(trigger_rules['client']))
                if server_error_rate >= trigger_rules['server']:
                    notification('5xx Problem', 'Ferver server have {} 5xx problem, Please check server status.'.format(trigger_rules['server']))
                start = current
                count, traffic, client_error, server_error = 0, 0, 0, 0

            # 每隔10s写入汇总数据到influxdb
            # if (current - start).total_seconds() >= write_db_interval:
            #     send(count, traffic, client_error/count, server_error/count)
            #     logging.info('Sending nginx metric data to influxdb...')
            #     start = current
            #     count, traffic, client_error, server_error = 0, 0, 0, 0


def send(*args):
    tb_data = 'access_log count={},traffic={},client_error={},server_error={}'.format(*args)
    res = requests.post('http://127.0.0.1:8086/write', data=tb_data, params={'db': 'Da'})
    if res.status_code >= 300:
        print(res.content)


def notification(subject, content):
    smtp_server = 'smtp.139.com'
    mail_user = 'user'
    mail_pass = 'pass'
    me = mail_user+"<"+mail_user+">"
    msg = MIMEText(content, _charset='gbk')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ";".join(sa)
    try:
        s = smtplib.SMTP()
        s.connect(smtp_server)
        s.login(mail_user, mail_pass)
        s.sendmail(me, sa, msg.as_string())
        s.close()
    except Exception as e:
        logging.warning(e)


if __name__ == '__main__':
    try:
        agg(sys.argv[1])
    except KeyboardInterrupt:
        event.set()
