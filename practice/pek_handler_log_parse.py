import os
import re
import sys
import time
import json
import logging
import requests
import threading

event = threading.Event()
logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s [%(threadName)s] - %(message)s')
p = re.compile(r'(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) \[(?P<thread>.*)\] (?P<level>\w{4}) (?P<class>.*) - (?P<remark>.*)')


def read_log(path, t):
    offset = 0
    while getattr(t, "do_run", True):
        with open(path, encoding='utf8') as f:
            if offset > os.stat(path).st_size:
                offset = 0
            f.seek(offset)
            yield from f
            offset = f.tell()
        event.wait(1)


def parse(path, t):
    try:
        for line in read_log(path, t):
            m = p.search(line.rstrip('\n'))
            if m:
                data = m.groupdict()
                yield data
                logging.info('parse log done.')
    except Exception as f:
        logging.info(f)


def agg(path):
    try:
        t = threading.current_thread()
        print('Agg Thread: ', id(threading.current_thread()))
        while getattr(t, "do_run", True):
            logging.info('Starting agg metric data...')
            for item in parse(path, t):
                print('{} {}'.format(fn, item['remark']))
                # if item['level'] == 'WARN':
                #     alert_resp = alert('trigger', str(int(time.time())), '{time} - {remark}'.format(**item))
                #     logging.info('!!!Server maybe has problem!!!')
                #     if json.loads(alert_resp.decode())['result'] == 'success':
                #         logging.info('Send alert event to oneAlert platform success.')
                #     else:
                #         logging.info('Send alert event to oneAlert platform failed!!!')
    except Exception as f:
        logging.info(f)

if __name__ == '__main__':
    current_dt = time.strftime('%Y-%m-%d')
    dt = time.strftime('%Y-%m-%d')
    fn = '{}'.format(dt+'.log')
    print('Start Create init thread...')
    current_thread = threading.Thread(target=agg, args=(fn,), name=dt)
    current_thread.start()
    while True:
        dt = time.strftime('%Y-%m-%d')
        print('{} Waiting for date change...'.format(dt))
        fn = '{}'.format(dt+'.log')
        if os.path.isfile(fn):
            if dt != current_dt:
                current_thread.do_run = False
                print('Start create new thread to read log...')
                current_thread = threading.Thread(target=agg, name=dt, args=(fn,))
                current_thread.start()
                current_dt = dt
                print(threading.enumerate())
        else:
            print('File not found...')
        print(threading.enumerate())
        time.sleep(10)
