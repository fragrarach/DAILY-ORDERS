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
