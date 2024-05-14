import logging

def filter_below(level):
    level = getattr(logging, level)
    return lambda record: record.levelno <= level
