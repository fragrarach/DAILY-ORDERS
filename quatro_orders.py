from quatro import init_app_log_dir, log, add_sql_files, start_scheduler, listen
import config
from tasks import scheduler_task, listen_task


def main():
    init_app_log_dir()
    log(f'Starting {__file__}')
    orders_config = config.Config()
    add_sql_files(orders_config)
    start_scheduler(orders_config, scheduler_task)
    listen(orders_config, listen_task)


if __name__ == "__main__":
    main()
