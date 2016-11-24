# coding:utf-8
import json
import requests
from flask import Flask, abort, request

app = Flask(__name__)


def build_jobs(branch):
    # 拼接jobs名称
    jobs_url = 'http://LotusChing:LotusChing@120.24.80.34:2222/job/{}/build'.format(branch)
    # 提交post
    requests.post(jobs_url)


@app.route('/webhooks', methods=['POST'])
def webhooks():
    if not request.form:
        abort(400)
    data = request.form['hook']
    hook_data = json.loads(data)
    # 取出远程分支
    branch = hook_data['push_data']['ref'].split('/')[2]
    # 取出远程仓库名称
    repository = hook_data['push_data']['repository']['name']
    print('Starting Build {} Jobs'.format(branch))
    # 提交项目及对应分支的构建请求
    build_jobs('{}-{}'.format(repository, branch))
    return data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
