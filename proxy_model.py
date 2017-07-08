#! python2
# -*- coding: utf-8 -*-
from peewee import *
from datetime import datetime


db = SqliteDatabase('proxy.sqlite')


class BaseModel(Model):
    class Meta:
        database = db


class ProxyTable(BaseModel):
    """不写主键，将成为自增主键"""
    ip = CharField(null=True, max_length=255, verbose_name='ip')
    port = CharField(null=True, max_length=255, verbose_name='port')
    country = CharField(null=True, max_length=255, verbose_name='country')
    address = CharField(null=True, max_length=255, verbose_name='address')
    check_time = CharField(null=True, max_length=255, verbose_name='check_time')
    time_diff = CharField(null=True, max_length=255, verbose_name='time_diff')
    proxies = CharField(null=True, max_length=255, verbose_name='proxies')

    created_time = DateTimeField(default=datetime.now, verbose_name='created_time')

if __name__ == '__main__':
    ProxyTable.create_table()