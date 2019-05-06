import psycopg2.extensions
from sigm import sigm_connect, log_connect
from os.path import dirname, abspath
import pdfkit


# PostgreSQL DB connection configs
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


class Config:
    LISTEN_CHANNEL = 'daily_orders'

    SIGM_CONNECTION, SIGM_DB_CURSOR = sigm_connect(LISTEN_CHANNEL)
    LOG_CONNECTION, LOG_DB_CURSOR = log_connect()

    PARENT_DIR = dirname(abspath(__file__))

    PATH_WKTHMLTOPDF = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    PDF_CONFIG = pdfkit.configuration(wkhtmltopdf=PATH_WKTHMLTOPDF)
