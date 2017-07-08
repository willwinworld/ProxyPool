#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""实现proxy代理接口"""
import requests
from datetime import datetime
from pyquery import PyQuery as Pq
from dialogue.dumblog import dlog
from proxy_model import ProxyTable


logger = dlog(__file__, console='debug')


class Proxy(object):
    def __init__(self):
        self.proxy_url = 'http://cn-proxy.com/'

    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = {1}'.format(k, v) for k, v in self.__dict__.items())
        return '<{0}: \n  {1}\n>'.format(class_name, '\n  '.join(properties))

    def fetch(self):
        r = requests.get(self.proxy_url)
        d = Pq(r.content)
        block = d('.sortable')
        container = []
        for i in block.items():
            inner_block = i('tr:gt(1)')
            for j in inner_block.items():
                ip = j('td:eq(0)').text()
                # print ip
                port = j('td:eq(1)').text()
                # print port
                address = j('td:eq(2)').text().encode('ISO-8859-1', 'ignore')
                # print address
                check_time = j('td:eq(4)').text()
                container.append({'ip': ip, 'port': port, 'address': address, 'check_time': check_time, 'country': 'china'})

                # print check_time
                # print j('td').text().encode('ISO-8859-1', 'ignore')
        return container

    def speed(self):
        baidu_url = 'http://www.baidu.com/'
        fetch_container = self.fetch()
        container = []
        for c in fetch_container:
            start_time = datetime.now()
            proxies = {'http': c['ip']+':'+c['port'],
                       'https': c['ip']+':'+c['port'],
                       'ftp': c['ip']+':'+c['port']}
            try:
                r = requests.get(baidu_url, proxies=proxies, timeout=4)
                if r.status_code == 200:
                    end_time = datetime.now()
                    time_diff = end_time - start_time
                    logger.info(c['address'])
                    logger.info(c['ip'] + ':' + c['port'])
                    logger.info(time_diff)
                    c['time_diff'] = time_diff
                    c['proxies'] = proxies
                    container.append(c)
                else:
                    continue
            except Exception as err:
                logger.info(err)
                continue
        # print container
        return container

    def sort_and_save(self):
        speed_container = self.speed()
        result = sorted(speed_container, key=lambda k: k['time_diff'])
        for e in result:
            ProxyTable.create(**e)


if __name__ == '__main__':
    proxy = Proxy()
    proxy.fetch()
    proxy.speed()
    proxy.sort_and_save()
