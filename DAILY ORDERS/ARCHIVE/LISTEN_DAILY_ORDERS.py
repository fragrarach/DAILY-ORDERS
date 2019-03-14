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

old_payload = ''
new_payload = ''
old_ord_no = ''
new_ord_no = ''
while 1:
    conn_sigm.poll()
    conn_sigm.commit()
    while conn_sigm.notifies:
        notify = conn_sigm.notifies.pop()
        raw_payload = notify.payload
        print(raw_payload)

        if raw_payload.split(", ")[0] == 'OLD':
            old_ord_no = raw_payload.split(", ")[1]
            old_payload = raw_payload.split(", ")[2]
        elif raw_payload.split(", ")[0] == 'NEW':
            new_ord_no = raw_payload.split(", ")[1]
            new_payload = raw_payload.split(", ")[2]
        elif raw_payload.split(", ")[0] == 'LINE':
            new_ord_no = raw_payload.split(", ")[1]
            old_ord_no = raw_payload.split(", ")[1]
            old_payload = '0'
            new_payload = '1'

    if old_payload != new_payload \
            and old_ord_no == new_ord_no \
            and old_ord_no != '' \
            and new_ord_no != '' \
            and old_payload != '' \
            and new_payload != '':
        print(old_payload)
        print(new_payload)
        sql_exp = f'INSERT INTO daily_orders_updated (ord_no, time_stamp) ' \
                  f'VALUES (\'{new_ord_no}\', NOW()::DATE)'
        log_query.execute(sql_exp)
        print(sql_exp)
        sql_exp = f'DELETE FROM daily_orders WHERE ord_no = {new_ord_no}'
        log_query.execute(sql_exp)
        print(sql_exp)
        old_payload = ''
        new_payload = ''
        old_ord_no = ''
        new_ord_no = ''
