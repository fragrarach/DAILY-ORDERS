from quatro import init_app_log_dir, log, add_sql_files, configuration as c
from config import Config
from tasks import daily_orders_task, weekly_pending_task


def main():
    c.config = Config(__file__)
    init_app_log_dir()
    log(f'Starting {__file__}')
    c.config.sql_connections()
    add_sql_files()
    # daily_orders_task()
    weekly_pending_task()


if __name__ == "__main__":
    main()
