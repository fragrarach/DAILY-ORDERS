import os
import psycopg2.extensions


# Check whether app should reference dev or prod server/db
def dev_check():
    raw_filename = os.path.basename(__file__)
    removed_extension = raw_filename.split('.')[0]
    last_word = removed_extension.split('_')[-1]
    if last_word == 'DEV':
        return True
    else:
        return False


# Initialize production DB connection, listen cursor and query cursor
def sigm_conn():
    global conn_sigm, sigm_query
    if dev_check():
        conn_sigm = psycopg2.connect("host='192.168.0.57' dbname='DEV' user='SIGM' port='5493'")
    else:
        conn_sigm = psycopg2.connect("host='192.168.0.250' dbname='QuatroAir' user='SIGM' port='5493'")
    conn_sigm.set_client_encoding("latin1")
    conn_sigm.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    sigm_listen = conn_sigm.cursor()
    sigm_listen.execute("LISTEN daily_orders;")
    sigm_query = conn_sigm.cursor()

    return conn_sigm, sigm_query


# Initialize log DB connection, listen cursor and query cursor
def log_conn():
    global conn_log, log_query
    if dev_check():
        conn_log = psycopg2.connect("host='192.168.0.57' dbname='LOG' user='SIGM' port='5493'")
    else:
        conn_log = psycopg2.connect("host='192.168.0.250' dbname='LOG' user='SIGM' port='5493'")
    conn_log.set_client_encoding("latin1")
    conn_log.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    log_query = conn_log.cursor()

    return conn_log, log_query


# PostgreSQL DB connection configs
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


# Split base variables from payload string, return named variables
def base_payload_handler(payload):
    change_type = payload.split(', ')[0]
    ord_no = payload.split(', ')[1]
    return change_type, ord_no


# Split added part variables from payload string, return named variables
def added_part_payload_handler(payload):
    orl_id = payload.split(', ')[2]
    return orl_id


# Split price changed variables from payload string, return named variables
def price_changed_payload_handler(payload):
    orl_id = payload.split(', ')[2]
    orl_price = payload.split(', ')[3]
    return orl_id, orl_price


# Split removed part variables from payload string, return named variables
def removed_part_payload_handler(payload):
    orl_id = payload.split(', ')[2]
    orl_price = payload.split(', ')[3]
    prt_no = payload.split(', ')[4]
    orl_quantity = payload.split(', ')[5]
    prt_dscnt = payload.split(', ')[6]
    return orl_id, orl_price, prt_no, orl_quantity, prt_dscnt


# Insert converted quote data into 'daily_orders_updated' table
def converted_quote(change_type, ord_no):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no) ' \
              f'VALUES (\'{change_type}\', {ord_no})'
    print(sql_exp)
    log_query.execute(sql_exp)


# Insert added part data into 'daily_orders_updated' table
def added_part(change_type, ord_no, orl_id):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no, orl_id) ' \
              f'VALUES (\'{change_type}\', {ord_no}, {orl_id})'
    print(sql_exp)
    log_query.execute(sql_exp)


# Insert price changed data into 'daily_orders_updated' table
def price_changed(change_type, ord_no, orl_id, orl_price):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no, orl_id, orl_price) ' \
              f'VALUES (\'{change_type}\', {ord_no}, {orl_id}, {orl_price})'
    print(sql_exp)
    log_query.execute(sql_exp)


# Insert removed part data into 'daily_orders_updated' table
def removed_part(change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt) ' \
              f'VALUES (\'{change_type}\', {ord_no}, {orl_id}, {orl_price}, \'{prt_no}\', {orl_quantity}, {prt_dscnt})'
    print(sql_exp)
    log_query.execute(sql_exp)


def main():
    global conn_sigm, sigm_query, conn_log, log_query
    conn_sigm, sigm_query = sigm_conn()
    conn_log, log_query = log_conn()
    while 1:
        try:
            conn_sigm.poll()
        except:
            print('Database cannot be accessed, PostgreSQL service probably rebooting')
            try:
                conn_sigm.close()
                conn_sigm, sigm_query = sigm_conn()
                conn_log.close()
                conn_log, log_query = log_conn()
            except:
                pass
        else:
            conn_sigm.commit()
            while conn_sigm.notifies:
                notify = conn_sigm.notifies.pop()
                raw_payload = notify.payload

                change_type, ord_no = base_payload_handler(raw_payload)

                if change_type == 'CONVERTED QUOTE':
                    converted_quote(change_type, ord_no)

                elif change_type == 'ADDED PART':
                    orl_id = added_part_payload_handler(raw_payload)
                    added_part(change_type, ord_no, orl_id)

                elif change_type == 'PRICE CHANGED':
                    orl_id, orl_price = price_changed_payload_handler(raw_payload)
                    price_changed(change_type, ord_no, orl_id, orl_price)

                elif change_type == 'REMOVED PART':
                    orl_id, orl_price, prt_no, orl_quantity, prt_dscnt = removed_part_payload_handler(raw_payload)
                    removed_part(change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt)


main()
