#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
from peewee import RawQuery
from flask import make_response
from dialogue.dumblog import dlog
from flask import Flask, jsonify, abort, request
from proxy_model import ProxyTable

app = Flask(__name__)
logger = dlog(__file__, console='debug')
# app.config['JSON_AS_ASCII'] = False
"""
实现restful接口
http://127.0.0.1:8000/count=10&country=china
'/todo/api/v1.0/tasks/<int:task_id>'
curl http://localhost:5000/todo/api/v1.0/tasks/2
"""


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/count', methods=['GET'])
def get_count():
    count = ProxyTable.select().count()
    return jsonify({'count': count})


@app.route('/count/<int:num>/country/<string:country>/area/<string:area>', methods=['GET'])
def get_tasks(num, country, area):
    rq = RawQuery(ProxyTable, 'SELECT * FROM proxytable WHERE address like ? AND country = ? limit 0, ?', area+'%', country, num)
    rq_response = rq.execute()
    if len(list(rq_response)) == 0:
        abort(404)
    res = []
    for item in rq_response:
        res.append({'ip': item.ip, 'port': item.port, 'address': item.address,
                    'country': item.country,'check_time': item.check_time,
                    'time_diff': item.time_diff,'proxy': [item.proxies],
                    'created_time': item.created_time})
    return jsonify(res)


@app.route('/add_proxy', methods=['POST'])
def create_task():
    if not request.json or not 'ip' in request.json or not 'port' in request.json:
        abort(400)
    task = {
        'ip': request.json['ip'],
        'port': request.json['port']
    }
    ProxyTable.create(ip=task['ip'], port=task['port'])
    return jsonify({'task': task}), 201


@app.route('/update_proxy/<string:ip>/port/<string:port>', methods=['PUT'])
def update_task(ip, port):
    count = ProxyTable.select().count()
    if count == 0:
        # 如果数据库没有记录，根本不用更新
        abort(404)
    if not request.json:
        abort(404)
    if 'ip' not in request.json or 'port' not in request.json:
        abort(404)
    try:
        proxies = {'http': ip + ':' + port,
                   'https': ip + ':' + port,
                   'ftp': ip + ':' + port}
        r = requests.get('http://www.baidu.com/', proxies=proxies, timeout=4)
        if r.status_code == 200:
            query = ProxyTable.create(ip=ip, port=port, proxies=proxies)
            query.save()
    except Exception as err:
        logger.info(err)


@app.route('/delete_proxy/<string:ip>', methods=['DELETE'])
def delete_task(ip):
    query = ProxyTable.delete().where(ProxyTable.ip == ip)
    query_response = query.execute()
    if query_response:
        # 如果返回非零的值，在页面上显示被删除的ip
        return jsonify({'delete': ip})
    else:
        # 其它返回404
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)
