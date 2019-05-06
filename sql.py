from config import Config


# Insert converted quote data into 'daily_orders_updated' table
def converted_order(change_type, ord_no):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no) ' \
              f'VALUES (\'{change_type}\', {ord_no})'
    print(sql_exp)
    Config.LOG_DB_CURSOR.execute(sql_exp)


# Insert added part data into 'daily_orders_updated' table
def added_part(change_type, ord_no, orl_id):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no, orl_id) ' \
              f'VALUES (\'{change_type}\', {ord_no}, {orl_id})'
    print(sql_exp)
    Config.LOG_DB_CURSOR.execute(sql_exp)


# Insert price changed data into 'daily_orders_updated' table
def price_changed(change_type, ord_no, orl_id, orl_price):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no, orl_id, orl_price) ' \
              f'VALUES (\'{change_type}\', {ord_no}, {orl_id}, {orl_price})'
    print(sql_exp)
    Config.LOG_DB_CURSOR.execute(sql_exp)


# Insert removed part data into 'daily_orders_updated' table
def removed_part(change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt) ' \
              f'VALUES (\'{change_type}\', {ord_no}, {orl_id}, {orl_price}, \'{prt_no}\', {orl_quantity}, {prt_dscnt})'
    print(sql_exp)
    Config.LOG_DB_CURSOR.execute(sql_exp)


def printed_packing_slip(change_type, ord_no):
    sql_exp = f'INSERT INTO daily_orders_updated ' \
              f'(change_type, ord_no) ' \
              f'VALUES (\'{change_type}\', {ord_no})'
    print(sql_exp)
    Config.LOG_DB_CURSOR.execute(sql_exp)


# TODO : Add a 'sent' boolean column to daily_orders log table instead of deleting sent orders
# Clear log of orders that are already sent, add orders to log that have just been sent
def exclusion_log():
    sql_exp = f'DELETE FROM daily_orders'
    Config.LOG_DB_CURSOR.execute(sql_exp)
    print('Cleared daily_orders table on log DB')

    grouping_view_list = ['', '_quotes', '_pending']

    for grouping in grouping_view_list:
        sql_exp = f'SELECT ord_no FROM daily_orders{grouping}'
        Config.SIGM_DB_CURSOR.execute(sql_exp)
        result_set = Config.SIGM_DB_CURSOR.fetchall()

        for row in result_set:
            for cell in row:
                ord_no = cell
                sql_exp = f'INSERT INTO daily_orders (ord_no) VALUES ({ord_no})'
                print('Added order ord_no to daily_orders table on log DB')
                Config.LOG_DB_CURSOR.execute(sql_exp)


# TODO : Add a 'sent' boolean column to daily_orders_updated log table instead of deleting sent updated orders
# Clear log of updated orders
def clear_updated():
    sql_exp = f'DELETE FROM daily_orders_updated'
    Config.LOG_DB_CURSOR.execute(sql_exp)
    print('Cleared daily_orders_updated table on log DB')


if __name__ == "__main__":
    exclusion_log()
    clear_updated()
