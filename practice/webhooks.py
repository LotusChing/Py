from flask import Flask, abort, request
import json
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s [%(processName)s] '
                            + '[%(threadName)s] - %(message)s')
app = Flask(__name__)


def build_jobs(branch):
	user = 'user'
	pass = 'pass'
    host = 'host'
	port = 'port'
    jobs_url = 'http://user:pass@host:port/job/{}/build'.format(branch)
    print(jobs_url)
    requests.post(jobs_url)


@app.route('/webhooks', methods=['POST'])
def webhooks():
    if not request.form:
        abort(400)
    data = request.form['hook']
    push_data = json.loads(data)
    branch = push_data['push_data']['ref'].split('/')[2]
    repository = push_data['push_data']['repository']['name']
    print('Starting Build {} Jobs'.format(branch))
    build_jobs('{}-{}'.format(repository, branch))
    return data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
