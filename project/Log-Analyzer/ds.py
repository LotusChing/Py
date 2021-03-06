# -*- coding:utf-8 -*-
import re
import sys
import datetime
import threading


def read_log(path):
    with open(path) as f:
        yield from f


def parse(path):
    # TODO use re parse nginx log
    o = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) .* .* \[(?P<time>.*)\] "(?P<method>\w+) (?P<url>[^\s]*) (?P<version>[\w|/\d\.]*)" (?P<status>\d{3}) (?P<length>\d+) "(?P<referer>[^\s]*)" "(?P<ua>.*)"')
    for line in read_log(path):
        m = o.search(line.rstrip('\n'))
        if m:
            data = m.groupdict()
            now = datetime.datetime.now()
            data['time'] = now.strftime('%d/%b/%Y:%H:%M:%S %z')
            yield data


def data_source(src, dst, event):
    while not event.is_set():
        with open(dst, 'a') as f:
            for item in parse(src):
                line = '{ip} - - [{time}] "{method} {url} {version}" {status} {length} "{referer}" "{ua}"\n'.format(**item)
                f.write(line)
                event.wait(0.1)

if __name__ == '__main__':
    e = threading.Event()
    try:
        data_source('access.log', 'generated', e)
    except KeyboardInterrupt:
        e.set()