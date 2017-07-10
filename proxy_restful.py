#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
from peewee import RawQuery
from flask import make_response, url_for
from dialogue.dumblog import dlog
from flask import Flask, jsonify, abort, request
from proxy_model import ProxyTable
from flask_httpauth import HTTPBasicAuth
from restful_password import password

app = Flask(__name__)
auth = HTTPBasicAuth()
logger = dlog(__file__, console='debug')
# app.config['JSON_AS_ASCII'] = False
"""
实现restful接口
http://127.0.0.1:8000/count=10&country=china
'/todo/api/v1.0/tasks/<int:task_id>'
curl http://localhost:5000/todo/api/v1.0/tasks/2
"""


@auth.get_password
def get_password(username):
    if username == 'root':
        return password['key']
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/count', methods=['GET'])
def get_count():  # 测试接口成功
    count = ProxyTable.select().count()
    return jsonify({'count': count})


@app.route('/count/<int:num>/country/<string:country>/area/<string:area>', methods=['GET'])
def get_tasks(num, country, area):  # 测试接口成功
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
@auth.login_required
def create_task():  # 插入新记录
    """
    使用postman发送JSON(application/json)数据
    post_url: 127.0.0.1:5000/add_proxy
    点击BODY处,选中raw参数，{"ip": "test", "port": "test"},箭头处选择JSON(application/json)
    """
    if not request.json or 'ip' not in request.json or 'port' not in request.json:
        abort(400)
    task = {
        'ip': request.json['ip'],
        'port': request.json['port']
    }
    ProxyTable.create(ip=task['ip'], port=task['port'])
    return jsonify({'task': task}), 201


@app.route('/update_proxy/<string:ip>/port/<string:port>', methods=['PUT'])
@auth.login_required
def update_task(ip, port):  # 更新原有记录
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
            query = ProxyTable.update(ip=ip, port=port, proxies=proxies)
            query.save()
    except Exception as err:
        logger.info(err)


@app.route('/delete_proxy/<string:ip>/<string:port>', methods=['DELETE'])
@auth.login_required
def delete_task(ip, port):
    """
    在postman里面选择DELETE方法
    然后输入127.0.0.1:5000/delete_proxy/test/test即可
    """
    query = ProxyTable.delete().where((ProxyTable.ip == ip) & (ProxyTable.port == port))
    query_response = query.execute()
    if query_response:
        # 如果返回非零的值，在页面上显示被删除的ip
        return jsonify({'delete_ip': ip, 'delete_port': port})
    else:
        # 其它返回404
        abort(404)


@app.route('/', methods=['GET'])
def homepage():
    total = []
    for row in ProxyTable.select():
        total.append({'ip': row.id, 'port': row.port, 'country': row.country,
                      'address': row.address, 'check_time': row.check_time,
                      'time_diff': row.time_diff, 'proxies': [row.proxies],
                      'created_time': row.created_time})
    return jsonify(total)


if __name__ == '__main__':
    app.run(debug=True)
