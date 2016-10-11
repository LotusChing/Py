# coding:utf-8
import os
import re
import sys
import requests
import datetime
import threading

o = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) .* .* \[(?P<time>.*)\] "(?P<method>\w+) (?P<url>[^\s]*) (?P<version>[\w|/\d\.]*)" (?P<status>\d{3}) (?P<length>\d+) "(?P<referer>[^\s]*)" "(?P<ua>.*)"')


def read_log(path):
    offset = 0
    event = threading.Event()
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
        m = o.search(line.rstrip('\n'))
        if m:
            data = m.groupdict()
            '''
            data 结构
            {
                'status': '200',
                'length': '112',
                'url': '',
                'time': '10/Aug/2016:09:52:26 +0800',
                'version': 'HTTP/1.1',
                'ip': '114.111.166.248',
                'ua': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
                'method': 'POST',
                'referer': 'http://www.178linux.com/wp-admin/post.php?post=32351&action=edit'
            }
            '''
            yield data


def agg(path, interval=10):
    count, traffic, error = 0, 0, 0
    # 记录开始时间
    start = datetime.datetime.now()
    for item in parse(path):
        # 统计访问量
        count += 1
        # 统计流量
        traffic += int(item['length'])
        # 统计错误量
        if int(item['status']) >= 300:
            error += 1
        # 记录当前时间
        current = datetime.datetime.now()
        # 如果开始和结束时间间隔超过10s则发送统计数据到influxdb
        if (current - start).total_seconds() >= interval:
            # 计算错误率
            error_rate = error / count
            # 调用send发送各metric数据
            send(count, traffic, error_rate)
            # 重置起始时间
            start = current
            # 重置统计信息
            count, traffic, error = 0, 0, 0


def send(count, traffic, error_rate):
    # 这里逗号后面不要用空格，不然会出错
    line = 'access_log count={},traffic={},error_rate={}'.format(count, traffic, error_rate)
    # post数据到influxdb里面的Da库去
    res = requests.post('http://127.0.0.1:8086/write', data=line, params={'db': 'Da'})
    # 如果post异常则输出异常日志
    if res.status_code >= 300:
        print(res.content)

if __name__ == '__main__':
    agg(sys.argv[1])
