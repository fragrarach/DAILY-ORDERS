from quatro import init_app_log_dir, log, add_sql_files, configuration as c
from config import Config
from tasks import scheduler_task


def main():
    c.config = Config(__file__)
    init_app_log_dir()
    log(f'Starting {__file__}')
    c.config.sql_connections()
    add_sql_files()
    scheduler_task(scheduler_task)


if __name__ == "__main__":
    main()
