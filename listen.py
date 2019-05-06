from sigm import *
from config import Config
from sql import converted_order, added_part, price_changed, removed_part, printed_packing_slip


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


def listen():
    while 1:
        try:
            Config.SIGM_CONNECTION.poll()
        except:
            print('Database cannot be accessed, PostgreSQL service probably rebooting')
            try:
                Config.SIGM_CONNECTION.close()
                Config.SIGM_CONNECTION, Config.SIGM_DB_CURSOR = sigm_connect(Config.LISTEN_CHANNEL)
                Config.LOG_CONNECTION.close()
                Config.LOG_CONNECTION, Config.LOG_DB_CURSOR = log_connect()
            except:
                pass
        else:
            Config.SIGM_CONNECTION.commit()
            while Config.SIGM_CONNECTION.notifies:
                notify = Config.SIGM_CONNECTION.notifies.pop()
                raw_payload = notify.payload

                change_type, ord_no = base_payload_handler(raw_payload)

                if change_type in ('CONVERTED QUOTE', 'CONVERTED PENDING'):
                    converted_order(change_type, ord_no)

                elif change_type == 'ADDED PART':
                    orl_id = added_part_payload_handler(raw_payload)
                    added_part(change_type, ord_no, orl_id)

                elif change_type == 'PRICE CHANGED':
                    orl_id, orl_price = price_changed_payload_handler(raw_payload)
                    price_changed(change_type, ord_no, orl_id, orl_price)

                elif change_type == 'REMOVED PART':
                    orl_id, orl_price, prt_no, orl_quantity, prt_dscnt = removed_part_payload_handler(raw_payload)
                    removed_part(change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt)

                elif change_type == 'PACKING SLIP':
                    printed_packing_slip(change_type, ord_no)


if __name__ == "__main__":
    listen()
