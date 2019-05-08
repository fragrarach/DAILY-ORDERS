from sigm import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import datetime
from files import email_body_generator, pdf_generator, time_stamp_generator, delete_pdf_file


# Send formatted email body to defined recipients, include attachment if exists
def send_email(email_body, salesman, attachments=None, subject=None):
    from_str = 'noreply@quatroair.com'
    to_list = [salesman]
    cc_list = ['sanjay.m@quatroair.com']
    bcc_list = ['jan.z@quatroair.com']

    to_str = ', '.join(to_list)
    cc_str = ', '.join(cc_list)

    subject_str = subject if subject else "Daily Orders"

    msg = MIMEMultipart('alternative')
    msg['From'] = from_str
    msg['To'] = to_str
    msg['CC'] = cc_str
    msg['Subject'] = subject_str
    msg.attach(MIMEText(email_body, 'html'))

    if attachments:
        for attachment in attachments:
            fp = open(attachment['file'], 'rb')
            att = MIMEApplication(fp.read(), _subtype="pdf")
            fp.close()
            att.add_header('Content-Disposition', 'attachment', filename=attachment['name'])
            msg.attach(att)

    s = smtplib.SMTP('aerofil-ca.mail.protection.outlook.com')
    s.starttls()

    s.sendmail(from_str, to_list + cc_list + bcc_list, msg.as_string())
    s.quit()


# Insert HTML files into email body, clean HTML folders, generate PDFs, send emails
def email_handler():
    salesmen_list = ['MARK STACHOWSKI', 'GREG PHILLIPS']
    grouping_list = ['NEW', 'QUOTES', 'PENDING', 'UPDATED', 'UPDATED QUOTES']

    for salesman in salesmen_list:
        email_body = ''
        for grouping in grouping_list:
            email_body = email_body_generator(grouping, salesman, email_body)

        if email_body != '':
            attachments = []
            email_pdf = pdf_generator(email_body)
            attachments.append(email_pdf)

            time_stamp = time_stamp_generator()
            subject = f'{salesman} {time_stamp}'

            if salesman == 'MARK STACHOWSKI':
                if not dev_check():
                    send_email(email_body, 'mark.s@quatroair.com', attachments, subject=subject)
                else:
                    send_email(email_body, 'jan.z@quatroair.com', attachments, subject=subject)
            elif salesman == 'GREG PHILLIPS':
                if not dev_check():
                    send_email(email_body, 'greg.p@quatroair.com', attachments, subject=subject)
                else:
                    send_email(email_body, 'jan.z@quatroair.com', attachments, subject=subject)

                delete_pdf_file(email_pdf)
        else:
            if datetime.datetime.today().weekday() not in (5, 6):
                email_body = 'No orders entered for current report time frame.'
                if salesman == 'MARK STACHOWSKI':
                    if not dev_check():
                        send_email(email_body, 'mark.s@quatroair.com')
                    else:
                        send_email(email_body, 'jan.z@quatroair.com')
                elif salesman == 'GREG PHILLIPS':
                    if not dev_check():
                        send_email(email_body, 'greg.p@quatroair.com')
                    else:
                        send_email(email_body, 'jan.z@quatroair.com')


if __name__ == "__main__":
    email_handler()
