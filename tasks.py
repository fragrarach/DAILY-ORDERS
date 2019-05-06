from sigm import dev_check
from threading import Timer
import datetime
from files import html_generator
from emails import email_handler
from sql import exclusion_log, clear_updated


def start_timer():
    secs = set_timer()
    snap_timer = Timer(secs, task)
    snap_timer.start()


def set_timer():
    now = datetime.datetime.today()
    hour = 12 if now.hour < 12 else 16
    minute = 0 if now.hour < 12 else 45
    then = now.replace(day=now.day, hour=hour, minute=minute, second=0, microsecond=0)

    delta = then - now
    secs = delta.seconds
    hours = round((secs / 60) / 60, 2)
    print(f'Order report scheduled for {hours} hours from now.')
    return secs


def task():
    html_generator()
    email_handler()
    if not dev_check():
        exclusion_log()
        clear_updated()


if __name__ == "__main__":
    start_timer()
    set_timer()
    task()
