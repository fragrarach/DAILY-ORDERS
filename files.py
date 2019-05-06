import os
import shutil
import pdfkit
import datetime
from config import Config


# Change alignment in HTML file, expandable
def format_html(html_path):
    with open(html_path, "r") as file:
        file_data = file.read()
    file_data = file_data.replace('align=center', 'align=left')

    with open(html_path, "w") as file:
        file.write(file_data)


# Run VBS script which runs Excel (VBA) file, which generates HTML files
def html_generator():
    vbs_file = r'\files\vba\DAILY ORDERS.vbs'
    vbs_path = f'{Config.PARENT_DIR}{vbs_file}'
    os.system(f'"{vbs_path}"')


def time_stamp_generator():
    return datetime.datetime.now().strftime('%H00-%d-%m-%Y')


# Pass email body to pdfkit to create a PDF, return dict of name/file
def pdf_generator(email_body):
    time_stamp = time_stamp_generator()
    pdf_name = f'Daily Orders ({time_stamp}).pdf'
    pdf_file = f'{Config.PARENT_DIR}\\files\\pdf\\{pdf_name}'
    pdfkit.from_string(email_body, pdf_file, configuration=Config.PDF_CONFIG)
    pdf = {'name': pdf_name, 'file': pdf_file}
    return pdf


def delete_pdf_file(pdf):
    os.remove(pdf['file'])


def email_body_generator(grouping, salesman, email_body):
    header_file = f'{Config.PARENT_DIR}\\files\\html\\{grouping}.html'
    html_file = f'\\files\\vba\\{salesman} {grouping}.html'
    html_folder = f'\\files\\vba\\{salesman} {grouping}_files\\'
    html_folder_path = f'{Config.PARENT_DIR}{html_folder}'
    html_path = f'{Config.PARENT_DIR}{html_file}'

    if os.path.exists(html_path):
        with open(header_file) as file:
            email_body += file.read()
        format_html(html_path)
        with open(html_path) as file:
            email_body += file.read()
        os.remove(html_path)
        shutil.rmtree(html_folder_path)

    return email_body


if __name__ == "__main__":
    html_generator()
