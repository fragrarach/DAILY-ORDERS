import smtplib
import psycopg2.extensions
import re
import datetime
import os
import shutil
import pdfkit
from os.path import dirname, abspath
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

conn_sigm = psycopg2.connect("host='192.168.0.250' dbname='QuatroAir' user='SIGM' port='5493'")
conn_sigm.set_client_encoding("latin1")
conn_sigm.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

sigm_query = conn_sigm.cursor()

conn_log = psycopg2.connect("host='192.168.0.250' dbname='LOG' user='SIGM' port='5493'")
conn_log.set_client_encoding("latin1")
conn_log.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

log_query = conn_log.cursor()

parent_dir = dirname(abspath(__file__))

path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)


def format_html(html_path):
    with open(html_path, "r") as file:
        file_data = file.read()
    file_data = file_data.replace('align=center', 'align=left')

    with open(html_path, "w") as file:
        file.write(file_data)


def send_email(email_body, salesman, attachment=None, attachment_name=None):
    from_str = 'noreply@quatroair.com'
    to_list = [salesman]
    cc_list = ['sanjay.m@quatroair.com', 'david.f@quatroair.com']
    bcc_list = ['jan.z@quatroair.com']

    to_str = ', '.join(to_list)
    cc_str = ', '.join(cc_list)

    msg = MIMEMultipart('alternative')
    msg['From'] = from_str
    msg['To'] = to_str
    msg['CC'] = cc_str
    msg['Subject'] = "Daily Orders"
    msg.attach(MIMEText(email_body, 'html'))

    if attachment and attachment_name:
        fp = open(attachment, 'rb')
        att = MIMEApplication(fp.read(), _subtype="pdf")
        fp.close()
        att.add_header('Content-Disposition', 'attachment', filename=attachment_name)
        msg.attach(att)

    s = smtplib.SMTP('aerofil-ca.mail.protection.outlook.com')
    s.starttls()

    s.sendmail(from_str, to_list + cc_list + bcc_list, msg.as_string())
    s.quit()


def html_generator():
    vbs_file = r'\VBA\DAILY ORDERS.vbs'
    vbs_path = f'{parent_dir}{vbs_file}'
    os.system(f'"{vbs_path}"')


def email_handler():
    salesmen_list = ['MARK STACHOWSKI', 'GREG PHILLIPS']
    grouping_list = ['NEW', 'QUOTES', 'PENDING', 'UPDATED', 'UPDATED QUOTES']

    for salesman in salesmen_list:
        email_body = ''
        for grouping in grouping_list:
            header_file = f'{parent_dir}\\HTML\\{grouping}.html'
            html_file = f'\\VBA\\{salesman} {grouping}.html'
            html_folder = f'\\VBA\\{salesman} {grouping}_files\\'
            html_folder_path = f'{parent_dir}{html_folder}'
            html_path = f'{parent_dir}{html_file}'

            if os.path.exists(html_path):
                with open(header_file) as file:
                    email_body += file.read()
                format_html(html_path)
                with open(html_path) as file:
                    email_body += file.read()
                os.remove(html_path)
                shutil.rmtree(html_folder_path)

        if email_body != '':
            time_stamp = datetime.datetime.now().strftime('%H00-%d-%m-%Y')
            pdf_name = f'Daily Orders ({time_stamp}).pdf'
            pdf_file = f'{parent_dir}\\PDF\\{pdf_name}'
            pdfkit.from_string(email_body, pdf_file, configuration=config)

            if salesman == 'MARK STACHOWSKI':
                send_email(email_body, 'mark.s@quatroair.com', pdf_file, pdf_name)
            elif salesman == 'GREG PHILLIPS':
                send_email(email_body, 'greg.p@quatroair.com', pdf_file, pdf_name)

            os.remove(pdf_file)
        else:
            if datetime.datetime.today().weekday() not in (5, 6):
                email_body = 'No orders entered for current report time frame.'
                if salesman == 'MARK STACHOWSKI':
                    send_email(email_body, 'mark.s@quatroair.com')
                elif salesman == 'GREG PHILLIPS':
                    send_email(email_body, 'greg.p@quatroair.com')


def exclusion_log():
    sql_exp = f'DELETE FROM daily_orders'
    log_query.execute(sql_exp)

    grouping_view_list = ['', '_quotes', '_pending']

    for grouping in grouping_view_list:
        sql_exp = f'SELECT ord_no FROM daily_orders{grouping}'
        sigm_query.execute(sql_exp)
        result_set = sigm_query.fetchall()

        for row in result_set:
            for cell in row:
                ord_no = cell
                sql_exp = f'INSERT INTO daily_orders (ord_no) VALUES ({ord_no})'
                log_query.execute(sql_exp)


def clear_updated():
    sql_exp = f'DELETE FROM daily_orders_updated'
    log_query.execute(sql_exp)


html_generator()
email_handler()
exclusion_log()
clear_updated()
