import quatro
import datetime
import files


# Insert HTML files into email body, clean HTML folders, generate PDFs, send emails
def email_handler():
    # TODO : Move salesmen and groupings to config class
    salesmen_list = ['MARK STACHOWSKI', 'GREG PHILLIPS']
    grouping_list = ['NEW', 'QUOTES', 'PENDING', 'UPDATED', 'UPDATED QUOTES']

    for salesman in salesmen_list:
        email_body = ''
        for grouping in grouping_list:
            email_body = files.email_body_generator(grouping, salesman, email_body)

        if email_body != '':
            attachments = []
            email_pdf = files.pdf_generator(email_body)
            attachments.append(email_pdf)

            time_stamp = files.time_stamp_generator()
            subject = f'{salesman} {time_stamp}'

            if salesman == 'MARK STACHOWSKI':
                quatro.send_email(email_body, ['mark.s@quatroair.com'], ['sanjay.m@quatroair.com'],
                                  [attachments], subject=subject)
            elif salesman == 'GREG PHILLIPS':
                quatro.send_email(email_body, ['greg.p@quatroair.com'], ['sanjay.m@quatroair.com'],
                                  [attachments], subject=subject)
            files.delete_pdf_file(email_pdf)
        else:
            if datetime.datetime.today().weekday() not in (5, 6):
                email_body = 'No orders entered for current report time frame.'
                if salesman == 'MARK STACHOWSKI':
                    quatro.send_email(email_body, ['mark.s@quatroair.com'], ['sanjay.m@quatroair.com'])
                elif salesman == 'GREG PHILLIPS':
                    quatro.send_email(email_body, ['greg.p@quatroair.com'], ['sanjay.m@quatroair.com'])


if __name__ == "__main__":
    email_handler()
