# -*- coding: utf-8 -*-
"""
reference:
https://github.com/icoxfog417/mlimages/blob/master/mlimages/util/log_api.py
https://github.com/borntyping/python-colorlog
"""
import colorlog
from colorlog import getLogger
from colorlog import StreamHandler
from logging import DEBUG, INFO


def create_logger(name, debug=True):
    logger = None
    logger = getLogger(name)
    handler = StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s:%(name)s:%(message)s'))
    level = DEBUG if debug else INFO
    handler.setLevel(level)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
