from threading import Timer
import datetime
from sigm import dev_check
from config import Config
from files import html_generator
from emails import email_handler
from sql import exclusion_log, clear_updated


def start_timer():
    secs = set_timer()
    snap_timer = Timer(secs, task)
    snap_timer.start()


def schedule_handler(now):
    then = now
    for schedule in Config.TASK_SCHEDULE:
        if 'weekday' in schedule.keys():
            if now.weekday() == schedule['weekday']:
                if now.hour < schedule['hour'] or (now.hour == schedule['hour'] and now.minute < schedule['minute']):
                    minute = schedule['minute']
                    hour = schedule['hour']
                    day = then.day
                    month = then.month
                    year = then.year
                    print(f"Scheduling task for this {schedule['name']}")
                    return minute, hour, day, month, year
            elif now.weekday() < schedule['weekday']:
                while then.weekday() != schedule['weekday']:
                    then += datetime.timedelta(days=1)
                minute = schedule['minute']
                hour = schedule['hour']
                day = then.day
                month = then.month
                year = then.year
                print(f"Scheduling task for this {schedule['name']}")
                return minute, hour, day, month, year
        else:
            if now.hour < schedule['hour'] or (now.hour == schedule['hour'] and now.minute < schedule['minute']):
                minute = schedule['minute']
                hour = schedule['hour']
                day = now.day
                month = now.month
                year = now.year
                print(f"Scheduling task for this {schedule['name']}")
                return minute, hour, day, month, year

    if 'weekday' in Config.TASK_SCHEDULE[0].keys():
        while then.weekday() != Config.TASK_SCHEDULE[0]['weekday']:
            then += datetime.timedelta(days=1)
    else:
        then = now + datetime.timedelta(days=1)

    minute = Config.TASK_SCHEDULE[0]['minute']
    hour = Config.TASK_SCHEDULE[0]['hour']
    day = then.day
    month = then.month
    year = then.year
    print(f"Scheduling task for next {Config.TASK_SCHEDULE[0]['name']}")
    return minute, hour, day, month, year


def set_timer():
    now = datetime.datetime.today()

    minute, hour, day, month, year = schedule_handler(now)

    then = now.replace(year=year, month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0)

    delta = then - now
    secs = delta.seconds
    hours = round((secs / 60) / 60, 2)
    print(f'Order report scheduled for {hours} hours from now.')
    return secs


def task():
    print('Starting scheduled task.')
    html_generator()
    email_handler()
    if not dev_check():
        exclusion_log()
        clear_updated()
    start_timer()


if __name__ == "__main__":
    start_timer()
    set_timer()
    task()
