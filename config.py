from quatro import sigm_connect, log_connect
from os.path import dirname, abspath
import pdfkit
import calendar


class Config:
    LISTEN_CHANNEL = 'daily_orders'

    def __init__(self, main_file_path):
        self.main_file_path = main_file_path
        self.parent_dir = dirname(abspath(main_file_path))
        self.sigm_connection = None
        self.sigm_db_cursor = None
        self.log_connection = None
        self.log_db_cursor = None

    def sql_connections(self):
        self.sigm_connection, self.sigm_db_cursor = sigm_connect(Config.LISTEN_CHANNEL)
        self.log_connection, self.log_db_cursor = log_connect()

    PATH_WKTHMLTOPDF = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    PDF_CONFIG = pdfkit.configuration(wkhtmltopdf=PATH_WKTHMLTOPDF)

    TASK_SCHEDULE = {
        'daily_orders_task': [
            {
                'name': 'morning',
                'hour': 12,
                'minute': 0
            },
            {
                'name': 'afternoon',
                'hour': 16,
                'minute': 55
            }
        ],
        'weekly_pending_task': [
            {
                'name': 'monday morning',
                'weekday': calendar.MONDAY,
                'hour': 7,
                'minute': 0
            }
        ]
    }

    CHANGED_ORDERS = []

    SALESMEN = ['MARK STACHOWSKI', 'GREG PHILLIPS']

    GROUPINGS = [
        'NEW',
        'NEW PENDING',
        'UPDATED PENDING',
        'OLD PENDING',
        'QUOTES',
        'UPDATED',
        'UPDATED QUOTES',
        'CANCELLED'
    ]

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
