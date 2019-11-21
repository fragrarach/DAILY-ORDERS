from quatro import configuration as c
import re
import files
import emails
import statements


# Split base variables from payload string, return named variables
def base_payload_handler(payload):
    change_type = payload.split('], [')[0][1:]
    if payload.split('], [')[1].endswith(']'):
        ord_no = payload.split('], [')[1][:-1]
    else:
        ord_no = payload.split('], [')[1]
    return change_type, ord_no


# Split added part variables from payload string, return named variables
def added_part_payload_handler(payload):
    orl_id = payload.split('], [')[2][:-1]
    return orl_id


# Split price changed variables from payload string, return named variables
def price_changed_payload_handler(payload):
    orl_id = payload.split('], [')[2]
    orl_price = payload.split('], [')[3][:-1]
    return orl_id, orl_price


# Split removed part variables from payload string, return named variables
def removed_part_payload_handler(payload):
    orl_id = payload.split('], [')[2]
    orl_price = payload.split('], [')[3]
    prt_no = payload.split('], [')[4]
    orl_quantity = payload.split('], [')[5]
    prt_dscnt = payload.split('], [')[6][:-1]
    return orl_id, orl_price, prt_no, orl_quantity, prt_dscnt


def changed_order(ord_no):
    if ord_no not in c.config.CHANGED_ORDERS:
        c.config.CHANGED_ORDERS.append(ord_no)


def saved_order(ord_no, payload):
    if ord_no in c.config.CHANGED_ORDERS:
        c.config.CHANGED_ORDERS.remove(ord_no)
        files.html_generator(ord_no)

        sigm_string = payload.split('], [')[-1][:-1]
        user = re.findall(r'(?<=aSIGMWIN\.EXE u)(.*)(?= m)', sigm_string)[0]

        creator = statements.get_order_creator(ord_no)
        if creator:
            email_to = c.config.EMAILS[f'{creator}']
            email_cc = c.config.EMAILS[f'{user}']
        elif user in c.config.EMAILS:
            email_to = c.config.EMAILS[f'{user}']
            email_cc = ''
        else:
            email_to = c.config.EMAILS['DEFAULT']
            email_cc = ''
        emails.order_email(ord_no, email_to, email_cc)


def clear_order(ord_no):
    if ord_no not in c.config.CHANGED_ORDERS:
        c.config.CHANGED_ORDERS.remove(ord_no)
