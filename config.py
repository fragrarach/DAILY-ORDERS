from quatro import sigm_connect, log_connect, dev_check
from os.path import dirname, abspath
import pdfkit


class Config:
    LISTEN_CHANNEL = 'alert'

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
                'hour': 16,
                'minute': 55
            }
        ]
    else:
        TASK_SCHEDULE = [
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
        ]
