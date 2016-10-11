# -*- coding:utf-8 -*-
import re
import sys
import time
import pygal
import pprint
import datetime

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
            data['time'] = datetime.datetime.strptime(data['time'], '%d/%b/%Y:%H:%M:%S %z')
            yield data

def window(time):
    pass


def count(key, data):
    if key not in data.keys():
        data[key] = 0
    data[key] += 1
    return data


def analyze(path):
    ret = {}
    # start = datetime.datetime(2016, 8, 10, 3, 20)
    # end = datetime.datetime(2016, 8, 10, 23, 30)

    def init_data():
        return {
            'ip': {},
            'url': {},
            'ua': {},
            'status': {},
            'throughput': 0
        }
    for item in parse(path):
        time = item['time'].strftime('%Y%m%d%H%M')
        if time not in ret.keys():
            ret[time] = init_data()
        data = ret[time]
        for key, value in data.items():
            if key != 'throughput':
                data[key] = count(item[key], value)
        data['throughput'] += int(item['length'])
    return ret


def render():
    pass


def render_line(name, labels, data):
    line = pygal.Line()
    line.title = name
    line.x_labels = labels
    line.add(name, data)
    return line.render(is_unicode=True)


def render_bar(name, data):
    pass


def render_pip(name, data):
    pass


def top(data, key, num):
    print('TOP {} {}: '.format(num, key))
    sorted_keys = list(data[key].items())
    sorted_keys.sort(key=lambda x: x[1], reverse=True)
    for key, count in sorted_keys[:num]:
        print('    {} ==> {}'.format(key, count))


def main():
    # data = analyze(sys.argv[1])
    data = analyze('access.log')
    # render_line('throughput', data['throughput'])
    rs = list(data.items())
    rs.sort(key=lambda x: x[0], reverse=True)
    labels = [x[0] for x in rs]
    throughput = [x[1]['throughput'] for x in rs]
    svg = render_line('throughput', labels=labels, data=throughput)
    with open('throughput.svg', 'w', encoding='utf8') as f:
        f.write(svg)

if __name__ == '__main__':
    main()
