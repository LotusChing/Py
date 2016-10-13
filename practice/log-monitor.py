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

data = {
    'client': [0, 0, 0],
    'server': [0, 0, 0]
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
                if client_error_rate > trigger_rules['client']:
                    logging.info('client problem, count: {} client_error_rate: {} server_error_rate: {}'.format(count, client_error_rate, server_error_rate))
                    judge('client', 0)
                else:
                    judge('client', 1)
                if server_error_rate > trigger_rules['server']:
                    logging.info('server problem, count: {} client_error_rate: {} server_error_rate: {}'.format(count, client_error_rate, server_error_rate))
                    judge('server', 0)
                else:
                    judge('server', 1)
                start = current
                count, traffic, client_error, server_error = 0, 0, 0, 0

            # 每隔10s写入汇总数据到influxdb
            # if (current - start).total_seconds() >= write_db_interval:
            #     send(count, traffic, client_error/count, server_error/count)
            #     logging.info('Sending nginx metric data to influxdb...')
            #     start = current
            #     count, traffic, client_error, server_error = 0, 0, 0, 0


def judge(item, flag):
    # 如果出现错误count+1
    logging.info('Item: {} Count: {}'.format(item, data[item][0]))
    if flag == 0:
        data[item][0] += 1
    else:
        # 如果flag为其他值则表示指标已恢复，设置统计位为0，标志位为0
        data[item][1] = 0
        data[item][0] = 0

    # 如果count>=3则将状态设置为1, 1为异常
    if data[item][0] >= 3:
        data[item][1] = 1
        logging.info('found {} error {} time, set status is no.'.format(item, data[item][0]))

    # 如果状态位为1并且通知位为0，则表示一出现问题，还未通知，则开始触发通知
    if data[item][1] == 1 and data[item][2] == 0:
        logging.info('found {} error, start error notification.'.format(item, data[item][0]))
        notification(item, 'Found {} have error, check server status.'.format(item))
        data[item][2] = 1

    # 如果通知位为1，状态位为0，则表示之前出过问题，现在已经恢复，发送恢复通知
    if data[item][1] == 0 and data[item][2] == 1:
        notification(item, 'Found {} recovery, current status is ok.'.format(item))
        data[item][2] = 0
        logging.info('found {} recovery, start ok notification.'.format(item))


def notification(subject, content):
    smtp_server = 'smtp.139.com'
    mail_user = '13521095342@139.com'
    mail_pass = '13521095342lc'
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


def send(*args):
    tb_data = 'access_log count={},traffic={},client_error={},server_error={}'.format(*args)
    res = requests.post('http://127.0.0.1:8086/write', data=tb_data, params={'db': 'Da'})
    if res.status_code >= 300:
        print(res.content)


if __name__ == '__main__':
    try:
        agg(sys.argv[1])
    except KeyboardInterrupt:
        event.set()