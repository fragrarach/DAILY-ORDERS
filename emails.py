from quatro import log, send_email, configuration as c
import datetime
import files


def order_email(ord_no, email_to, email_cc):
    email_body = ''
    email_body = files.email_body_generator(email_body, ord_no, header=None)
    # email_pdf = files.pdf_generator(email_body)
    # attachments = [email_pdf]
    time_stamp = files.time_stamp_generator()
    subject = f'{ord_no} {time_stamp}'
    send_email(email_body, [email_to], [email_cc],
               # attachments,
               subject=subject)
    # files.delete_pdf_file(email_pdf)


# Insert HTML files into email body, clean HTML folders, generate PDFs, send emails
def salesman_emails(cc_override=None, pending_orders=False):
    log('Starting salesmen emails')
    for salesman in c.config.SALESMEN:
        email_body = ''
        for grouping in c.config.GROUPINGS:
            file_name = f'{salesman} {grouping}'
            email_body = files.email_body_generator(email_body, file_name, header=grouping)

        if email_body != '':
            # email_pdf = files.pdf_generator(email_body)
            # attachments = [email_pdf]

            time_stamp = files.time_stamp_generator()
            subject = f'{salesman} {time_stamp}'

            if salesman == 'MARK STACHOWSKI':
                cc_list = cc_override if cc_override is not None else ['ceni.t@quatroair.com']
                send_email(email_body, ['mark.s@quatroair.com'], cc_list,
                           # attachments,
                           subject=subject)
            elif salesman == 'GREG PHILLIPS':
                if pending_orders is False:
                    send_email(email_body, ['greg.p@quatroair.com'], ['burnie.s@quatroair.com'],
                               # attachments,
                               subject=subject)
            # files.delete_pdf_file(email_pdf)
        else:
            if datetime.datetime.today().weekday() not in (5, 6):
                email_body = 'No orders entered for current report time frame.'
                if salesman == 'MARK STACHOWSKI':
                    send_email(email_body, ['mark.s@quatroair.com'], [''])
                elif salesman == 'GREG PHILLIPS':
                    if pending_orders is False:
                        send_email(email_body, ['greg.p@quatroair.com'], ['burnie.s@quatroair.com'])


def pending_emails():
    log('Starting pending email')
    email_body = ''
    email_body = files.email_body_generator(email_body, 'MARK STACHOWSKI OLD PENDING', header='OLD PENDING')
    email_body = files.email_body_generator(email_body, 'MARK STACHOWSKI OLD QUOTES', header='OLD QUOTES')
    send_email(email_body, ['jan.z@quatroair.com'], ['jan.z@quatroair.com'], subject='PENDING ORDERS TO BE REVISED')
