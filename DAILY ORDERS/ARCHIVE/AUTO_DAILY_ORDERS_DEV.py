import smtplib
import psycopg2.extensions
import re
import datetime
import os
import shutil
from os.path import dirname, abspath
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

conn_sigm = psycopg2.connect("host='192.168.0.250' dbname='QuatroAir' user='SIGM' port='5493'")
conn_sigm.set_client_encoding("latin1")
conn_sigm.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

sigm_query = conn_sigm.cursor()

conn_log = psycopg2.connect("host='192.168.0.57' dbname='LOG' user='SIGM' port='5493'")
conn_log.set_client_encoding("latin1")
conn_log.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

log_query = conn_log.cursor()

parent_dir = dirname(abspath(__file__))


def format_html(html_path):
    with open(html_path, "r") as file:
        file_data = file.read()
    file_data = file_data.replace('align=center', 'align=left')

    with open(html_path, "w") as file:
        file.write(file_data)


def send_email(email_body, salesman):
    from_str = 'noreply@quatroair.com'
    to_list = [salesman]
    cc_list = ['sanjay.m@quatroair.com']
    bcc_list = ['jan.z@quatroair.com']

    to_str = ', '.join(to_list)
    cc_str = ', '.join(cc_list)

    msg = MIMEMultipart('alternative')
    msg['From'] = from_str
    msg['To'] = to_str
    msg['CC'] = cc_str
    msg['Subject'] = "Daily Orders"
    msg.attach(MIMEText(email_body, 'html'))
    text = msg.as_string()

    s = smtplib.SMTP('aerofil-ca.mail.protection.outlook.com')
    s.starttls()

    s.sendmail(from_str, to_list + cc_list + bcc_list, text)
    s.quit()


def html_generator():
    vbs_file = r'\VBA\DAILY ORDERS.vbs'
    vbs_path = f'{parent_dir}{vbs_file}'
    os.system(f'"{vbs_path}"')


def email_handler():
    mark_salesmen = ['CHRISTOPHER FRASER',
                     'CASEY KURYLOWICZ',
                     'VINCE PARLAVECHIO',
                     'THIERRY DESPAUX',
                     'MARK CASTANHEIRO',
                     'MARK STACHOWSKI']

    greg_salesmen = ['GREG PHILLIPS',
                     'CALIFORNIA (SHERTEC)',
                     'ESPITECH']

    master_list = [mark_salesmen, greg_salesmen]

    for salesmen_list in master_list:
        email_body = ''
        for salesman in salesmen_list:
            html_file = f'\VBA\\{salesman}.html'
            html_folder = f'\VBA\\{salesman}_files\\'
            html_folder_path = f'{parent_dir}{html_folder}'
            html_path = f'{parent_dir}{html_file}'
            if os.path.exists(html_path):
                format_html(html_path)
                with open(html_path) as file:
                    email_body += file.read()
                os.remove(html_path)
                shutil.rmtree(html_folder_path)
        if email_body != '':
            if salesmen_list == mark_salesmen:
                send_email(email_body, 'mark.s@quatroair.com')
            elif salesmen_list == greg_salesmen:
                send_email(email_body, 'greg.p@quatroair.com')


def exclusion_log():
    sql_exp = f'SELECT ord_no FROM daily_orders'
    sigm_query.execute(sql_exp)
    result_set = sigm_query.fetchall()

    for row in result_set:
        for cell in row:
            sql_exp = f'INSERT INTO daily_orders (ord_no) VALUES ({cell})'
            log_query.execute(sql_exp)


html_generator()
email_handler()
exclusion_log()
