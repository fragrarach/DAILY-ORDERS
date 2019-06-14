import quatro


# Insert converted quote data into 'daily_orders_updated' table
def converted_order(config, change_type, ord_no):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no) ' \
              f'VALUES (\'{change_type}\', {ord_no})'
    print(sql_exp)
    config.log_db_cursor.execute(sql_exp)


# Insert added part data into 'daily_orders_updated' table
def added_part(config, change_type, ord_no, orl_id):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no, orl_id) ' \
              f'VALUES (\'{change_type}\', {ord_no}, {orl_id})'
    print(sql_exp)
    config.log_db_cursor.execute(sql_exp)


# Insert price changed data into 'daily_orders_updated' table
def price_changed(config, change_type, ord_no, orl_id, orl_price):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no, orl_id, orl_price) ' \
              f'VALUES (\'{change_type}\', {ord_no}, {orl_id}, {orl_price})'
    print(sql_exp)
    config.log_db_cursor.execute(sql_exp)


# Insert removed part data into 'daily_orders_updated' table
def removed_part(config, change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt) ' \
              f'VALUES (\'{change_type}\', {ord_no}, {orl_id}, {orl_price}, \'{prt_no}\', {orl_quantity}, {prt_dscnt})'
    print(sql_exp)
    config.log_db_cursor.execute(sql_exp)


def printed_packing_slip(config, change_type, ord_no):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no) ' \
              f'VALUES (\'{change_type}\', {ord_no})'
    print(sql_exp)
    config.log_db_cursor.execute(sql_exp)


def get_order_creator(config, ord_no):
    sql_exp = f"SELECT user_name FROM order_header WHERE ord_no = {ord_no} AND tg_op = 'INSERT'"
    result_set = quatro.sql_query(sql_exp, config.log_db_cursor)
    creator = quatro.scalar_data(result_set)
    return creator


# TODO : Add a 'sent' boolean column to daily_orders log table instead of deleting sent orders
# Clear log of orders that are already sent, add orders to log that have just been sent
def exclusion_log(config):
    sql_exp = f'DELETE FROM daily_orders'
    config.log_db_cursor.execute(sql_exp)
    print('Cleared daily_orders table on log DB')

    grouping_view_list = ['', '_quotes', '_pending', '_updated']

    for grouping in grouping_view_list:
        sql_exp = f'SELECT ord_no FROM daily_orders{grouping}'
        config.sigm_db_cursor.execute(sql_exp)
        result_set = config.sigm_db_cursor.fetchall()

        for row in result_set:
            for cell in row:
                ord_no = cell
                sql_exp = f'INSERT INTO daily_orders (ord_no) VALUES ({ord_no})'
                print(f'Added order {ord_no} to daily_orders table on log DB')
                config.log_db_cursor.execute(sql_exp)


# TODO : Add a 'sent' boolean column to daily_orders_updated log table instead of deleting sent updated orders
# Clear log of updated orders
def clear_updated(config):
    sql_exp = f'DELETE FROM daily_orders_updated'
    config.log_db_cursor.execute(sql_exp)
    print('Cleared daily_orders_updated table on log DB')


def ord_no_view(config, view):
    sql_exp = f'SELECT DISTINCT ord_no FROM {view}'
    result_set = quatro.sql_query(sql_exp, config.sigm_db_cursor)
    ord_nos = quatro.tabular_data(result_set)
    return ord_nos
