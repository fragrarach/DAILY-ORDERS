import os
from subprocess import call
import shutil
import pdfkit
import datetime
from quatro import log, configuration as c


# Change alignment in HTML file, expandable
def format_html(html_path):
    log(f'Formatting HTML file ({html_path})')
    with open(html_path, "r") as file:
        file_data = file.read()
    file_data = file_data.replace('align=center', 'align=left')

    with open(html_path, "w") as file:
        file.write(file_data)
    log(f'Done formatting HTML file ({html_path})')


# Run VBS script which runs Excel (VBA) file, which generates HTML files
def html_generator(ord_no=None, pending=None):
    if ord_no:
        os.environ['ORDER_NUMBER'] = ord_no
        log(f'Generating HTML file for order #: {ord_no}')
    elif pending:
        os.environ['PENDING_ORDERS'] = 'TRUE'
        log(f'Generating HTML file for pending orders')
    else:
        log(f'Generating HTML files for salesmen')

    # vbs_file = r'\files\vba\DAILY ORDERS.vbs'
    vbs_file = r'\files\vba\DAILY ORDERS DEV.vbs'
    vbs_path = f'{c.config.parent_dir}{vbs_file}'
    call(f'"{vbs_path}"', shell=True)

    if ord_no:
        os.environ['ORDER_NUMBER'] = ''
        log(f'HTML file generation complete for order #: {ord_no}')
    elif pending:
        os.environ['PENDING_ORDERS'] = ''
        log(f'HTML file generation complete for pending orders')
    else:
        log(f'HTML file generation complete for salesmen')


# TODO : Move time_stamp_generator to data module
def time_stamp_generator():
    return datetime.datetime.now().strftime('%H00-%d-%m-%Y')


# Pass email body to pdfkit to create a PDF, return dict of name/file
def pdf_generator(email_body):
    log('Generating PDF file')
    time_stamp = time_stamp_generator()
    pdf_name = f'Daily Orders ({time_stamp}).pdf'
    pdf_file = f'{c.config.parent_dir}\\files\\pdf\\{pdf_name}'
    pdfkit.from_string(email_body, pdf_file, configuration=c.config.PDF_CONFIG)
    pdf = {'name': pdf_name, 'file': pdf_file}
    log('Done generating PDF file')
    return pdf


def delete_pdf_file(pdf):
    log('Deleting PDF file')
    os.remove(pdf['file'])
    log('Done deleting PDF file')


def email_body_generator(email_body, file_name, header=None):
    html_file = f'\\files\\vba\\{file_name}.html'
    html_folder = f'\\files\\vba\\{file_name}_files\\'
    html_folder_path = f'{c.config.parent_dir}{html_folder}'
    html_path = f'{c.config.parent_dir}{html_file}'

    if os.path.exists(html_path):
        if header:
            log(f'Adding {header} header to HTML file')
            header_file = f'{c.config.parent_dir}\\files\\html\\{header}.html'
            with open(header_file) as file:
                email_body += file.read()
            log(f'Done adding {header} header to HTML file')

        format_html(html_path)
        log(f'Adding "{html_path}" HTML file to email body')
        with open(html_path) as file:
            email_body += file.read()
        log(f'Done adding "{html_path}" HTML file to email body')

        log(f'Deleting HTML file/folder ("{html_path}" and "{html_folder_path}")')
        os.remove(html_path)
        shutil.rmtree(html_folder_path)
        log(f'Done deleting HTML file/folder ("{html_path}" and "{html_folder_path}")')

    return email_body
