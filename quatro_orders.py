import quatro
import config
import tasks


def main():
    orders_config = config.Config()
    quatro.add_sql_files(orders_config)
    quatro.start_scheduler(orders_config, tasks.scheduler_task)
    quatro.listen(orders_config, tasks.listen_task)


if __name__ == "__main__":
    main()
