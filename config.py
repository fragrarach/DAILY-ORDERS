from quatro import sigm_connect, log_connect, dev_check
from os.path import dirname, abspath
import pdfkit


class Config:
    LISTEN_CHANNEL = 'daily_orders'

    def __init__(self):
        self.sigm_connection, self.sigm_db_cursor = sigm_connect(Config.LISTEN_CHANNEL)
        self.log_connection, self.log_db_cursor = log_connect()

    PARENT_DIR = dirname(abspath(__file__))

    PATH_WKTHMLTOPDF = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    PDF_CONFIG = pdfkit.configuration(wkhtmltopdf=PATH_WKTHMLTOPDF)

    if not dev_check():
        TASK_SCHEDULE = [
            {
                'name': 'morning',
                'hour': 12,
                'minute': 0
             },
            {
                'name': 'afternoon',
                'hour': 17,
                'minute': 2
            }
        ]
    else:
        TASK_SCHEDULE = [
            {
                'name': 'morning',
                'hour': 10,
                'minute': 37
            },
            {
                'name': 'afternoon',
                'hour': 16,
                'minute': 55
            }
        ]

    CHANGED_ORDERS = []

    SALESMEN = ['MARK STACHOWSKI', 'GREG PHILLIPS']
    GROUPINGS = ['NEW', 'QUOTES', 'PENDING', 'UPDATED', 'UPDATED QUOTES']

    # TODO : Convert to table on LOG DB
    EMAILS = {
        'DEFAULT': 'sales@quatroair.com',
        'BURNIE': 'sales@quatroair.com',
        'CENI': 'sales@quatroair.com',
        'JAN': 'jan.z@quatroair.com',
        'SANJAY': 'sanjay.m@quatroair.com',
        'CARMY': 'carmy.m@quatroair.com',
        'HENRY': 'henry.h@quatroair.com',
        'GERRY': 'gerry.b@aerofil.ca',
        'GREG': 'greg.p@quatroair.com',
        'MARK': 'mark.s@quatroair.com'
    }
