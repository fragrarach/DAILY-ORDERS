import smtplib
import datetime
import shutil
import pdfkit
from sigm import *
from os.path import dirname, abspath
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


parent_dir = dirname(abspath(__file__))

# HTML to PDF convert location
path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)


# Change alignment in HTML file, expandable
def format_html(html_path):
    with open(html_path, "r") as file:
        file_data = file.read()
    file_data = file_data.replace('align=center', 'align=left')

    with open(html_path, "w") as file:
        file.write(file_data)


# Send formatted email body to defined recipients, include attachment if exists
def send_email(email_body, salesman, attachments=None):
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


# Run VBS script which runs Excel (VBA) file, which generates HTML files
def html_generator():
    vbs_file = r'\VBA\DAILY ORDERS.vbs'
    vbs_path = f'{parent_dir}{vbs_file}'
    os.system(f'"{vbs_path}"')


def email_body_generator(grouping, salesman, email_body):
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

    return email_body


# Pass email body to pdfkit to create a PDF, return dict of name/file
def pdf_generator(email_body):
    time_stamp = datetime.datetime.now().strftime('%H00-%d-%m-%Y')
    pdf_name = f'Daily Orders ({time_stamp}).pdf'
    pdf_file = f'{parent_dir}\\PDF\\{pdf_name}'
    pdfkit.from_string(email_body, pdf_file, configuration=config)
    pdf = {'name': pdf_name, 'file': pdf_file}

    return pdf


def delete_pdf_file(pdf):
    os.remove(pdf['file'])


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

            if salesman == 'MARK STACHOWSKI':
                if not dev_check():
                    send_email(email_body, 'mark.s@quatroair.com', attachments)
                else:
                    send_email(email_body, 'jan.z@quatroair.com', attachments)
            elif salesman == 'GREG PHILLIPS':
                if not dev_check():
                    send_email(email_body, 'greg.p@quatroair.com', attachments)
                else:
                    send_email(email_body, 'jan.z@quatroair.com', attachments)

                delete_pdf_file(email_pdf)
        else:
            if datetime.datetime.today().weekday() not in (5, 6):
                email_body = 'No orders entered for current report time frame.'
                if salesman == 'MARK STACHOWSKI':
                    send_email(email_body, 'mark.s@quatroair.com')
                elif salesman == 'GREG PHILLIPS':
                    send_email(email_body, 'greg.p@quatroair.com')


# TODO : Add a 'sent' boolean column to daily_orders log table instead of deleting sent orders
# Clear log of orders that are already sent, add orders to log that have just been sent
def exclusion_log():
    sql_exp = f'DELETE FROM daily_orders'
    log_db_cursor.execute(sql_exp)

    grouping_view_list = ['', '_quotes', '_pending']

    for grouping in grouping_view_list:
        sql_exp = f'SELECT ord_no FROM daily_orders{grouping}'
        sigm_db_cursor.execute(sql_exp)
        result_set = sigm_db_cursor.fetchall()

        for row in result_set:
            for cell in row:
                ord_no = cell
                sql_exp = f'INSERT INTO daily_orders (ord_no) VALUES ({ord_no})'
                log_db_cursor.execute(sql_exp)


# TODO : Add a 'sent' boolean column to daily_orders_updated log table instead of deleting sent updated orders
# Clear log of updated orders
def clear_updated():
    sql_exp = f'DELETE FROM daily_orders_updated'
    log_db_cursor.execute(sql_exp)


def main():
    global sigm_connection, sigm_db_cursor, log_connection, log_db_cursor
    sigm_connection, sigm_db_cursor = sigm_connect()
    log_connection, log_db_cursor = log_connect()

    html_generator()
    email_handler()
    if not dev_check():
        exclusion_log()
        clear_updated()


main()
