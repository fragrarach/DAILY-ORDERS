import os
import select
import datetime
import sys
import re
import ast
import psycopg2
import psycopg2.extras
import psycopg2.extensions
from os.path import dirname, abspath

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

conn_sigm = psycopg2.connect("host='192.168.0.57' dbname='DEV' user='SIGM' port='5493'")
conn_sigm.set_client_encoding("latin1")
conn_sigm.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

sigm_listen = conn_sigm.cursor()
sigm_listen.execute("LISTEN daily_orders;")
sigm_query = conn_sigm.cursor()

conn_log = psycopg2.connect("host='192.168.0.57' dbname='LOG' user='SIGM' port='5493'")
conn_log.set_client_encoding("latin1")
conn_log.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

log_query = conn_log.cursor()

while 1:
    conn_sigm.poll()
    conn_sigm.commit()
    while conn_sigm.notifies:
        notify = conn_sigm.notifies.pop()
        raw_payload = notify.payload

        change_type = raw_payload.split(', ')[0]
        ord_no = raw_payload.split(', ')[1]

        if change_type == 'CONVERTED QUOTE':
            sql_exp = f'INSERT INTO daily_orders_updated_dev ' \
                      f'(change_type, ord_no) ' \
                      f'VALUES (\'{change_type}\', {ord_no})'
            print(sql_exp)
            log_query.execute(sql_exp)
        elif change_type == 'ADDED PART':
            orl_id = raw_payload.split(', ')[2]
            sql_exp = f'INSERT INTO daily_orders_updated_dev ' \
                      f'(change_type, ord_no, orl_id) ' \
                      f'VALUES (\'{change_type}\', {ord_no}, {orl_id})'
            print(sql_exp)
            log_query.execute(sql_exp)
        elif change_type == 'PRICE CHANGED':
            orl_id = raw_payload.split(', ')[2]
            orl_price = raw_payload.split(', ')[3]
            sql_exp = f'INSERT INTO daily_orders_updated_dev ' \
                      f'(change_type, ord_no, orl_id, orl_price) ' \
                      f'VALUES (\'{change_type}\', {ord_no}, {orl_id}, {orl_price})'
            print(sql_exp)
            log_query.execute(sql_exp)
        elif change_type == 'REMOVED PART':
            orl_id = raw_payload.split(', ')[2]
            orl_price = raw_payload.split(', ')[3]
            prt_no = raw_payload.split(', ')[4]
            orl_quantity = raw_payload.split(', ')[5]
            prt_dscnt = raw_payload.split(', ')[6]
            sql_exp = f'INSERT INTO daily_orders_updated_dev ' \
                      f'(change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt) ' \
                      f'VALUES (\'{change_type}\', {ord_no}, {orl_id}, {orl_price}, \'{prt_no}\', {orl_quantity}, {prt_dscnt})'
            print(sql_exp)
            log_query.execute(sql_exp)

        # sql_exp = f'INSERT INTO daily_orders_updated_dev (ord_no, change_type) VALUES ({ord_no}, \'{change_type}\')'
        # print(sql_exp)
        # log_query.execute(sql_exp)
