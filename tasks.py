from quatro import log, dev_check
import files
import emails
import statements
import data


def scheduler_task(config):
    log('Starting scheduled task.')
    files.html_generator(config)
    emails.salesman_emails(config)
    if not dev_check():
        statements.exclusion_log(config)
        statements.clear_updated(config)


def listen_task(config, notify):
    raw_payload = notify.payload

    log(raw_payload)

    change_type, ord_no = data.base_payload_handler(raw_payload)

    if change_type in ('CONVERTED QUOTE', 'CONVERTED PENDING'):
        statements.converted_order(config, change_type, ord_no)

    elif change_type == 'ADDED PART':
        orl_id = data.added_part_payload_handler(raw_payload)
        statements.added_part(config, change_type, ord_no, orl_id)

    elif change_type == 'PRICE CHANGED':
        orl_id, orl_price = data.price_changed_payload_handler(raw_payload)
        statements.price_changed(config, change_type, ord_no, orl_id, orl_price)

    elif change_type == 'REMOVED PART':
        orl_id, orl_price, prt_no, orl_quantity, prt_dscnt = data.removed_part_payload_handler(raw_payload)
        statements.removed_part(config, change_type, ord_no, orl_id, orl_price, prt_no, orl_quantity, prt_dscnt)

    elif change_type == 'PACKING SLIP':
        statements.printed_packing_slip(config, change_type, ord_no)

    elif change_type == 'CANCELLED ORDER':
        pass

    elif change_type == 'CHANGED ORDER':
        data.changed_order(config, ord_no)

    elif change_type == 'SAVED ORDER':
        data.saved_order(config, ord_no, raw_payload)

    elif change_type == 'CLEAR ORDER':
        data.clear_order(config, ord_no)
