#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：scripts
@File    ：logger.py
@Author  ：alex
@Date    ：2022/10/18 9:55 上午
"""

import logging
from werkzeug.local import LocalProxy

# PIPELINE_LOGGER_LEVEL = 'DEBUG'
LOGGER_LEVEL = 'INFO'
LOGGER_FORMAT = logging.Formatter('%(asctime)s %(levelname)8s: \n%(message)s\n')

_logger: logging.Logger = None
logger = LocalProxy(lambda: _get_logger())


def _get_logger():
    global _logger
    if _logger is None:
        _logger = logging.getLogger('logger')
        log_handler = logging.StreamHandler()
        log_handler.setLevel(LOGGER_LEVEL)
        log_handler.setFormatter(LOGGER_FORMAT)
        _logger.addHandler(log_handler)
        _logger.setLevel(LOGGER_LEVEL)
    return _logger
