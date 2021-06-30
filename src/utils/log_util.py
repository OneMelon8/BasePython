import datetime
import sys

from src.data.settings import VERBOSE_LEVEL, STDERR_LEVEL

LEVEL_DISPLAY = {
    0: "DEBUG",
    1: "INFO",
    5: "WARNING",
    10: "ERROR"
}


def debug(message, flush=False):
    _print(0, message, flush=flush)


def info(message, flush=False):
    _print(1, message, flush=flush)


def warning(message, flush=False):
    _print(5, message, flush=flush)


def error(message, flush=False):
    _print(10, message, flush=flush)


def _print(level, message, flush=False):
    if level < VERBOSE_LEVEL:
        return

    file = sys.stdout
    if level >= STDERR_LEVEL:
        file = sys.stderr

    now = datetime.datetime.now()
    date = f"{now.month}/{now.day}/{now.year}"
    time = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}:{int(now.microsecond / 1000):03d}"
    print(f"[{LEVEL_DISPLAY[level]}] {date} {time} >> {message}", file=file, flush=flush)
