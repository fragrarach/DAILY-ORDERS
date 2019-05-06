from sigm import *
from listen import listen
from tasks import start_timer


def main():
    add_sql_files()
    start_timer()
    listen()


if __name__ == "__main__":
    main()
