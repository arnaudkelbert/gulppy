# -*- coding: utf-8 -*-
"""
Gulppy config
"""
import logging
import os
import sys
import inspect
GULPPY_ROOT_PATH = os.path.normpath(os.path.join(os.path.abspath(inspect.stack()[0][1]), '..'))

# Set a variable to store path to implicitly add at module loading
# @see glpp_module_loader.sys_context
GLPP_SYS_PATH = []

def register_path(path: str):
    GLPP_SYS_PATH.append(path)


# Set gulppy logger with a NullHandler
# In order to show something you will have to init the logger first, for instance
# by calling the above defined init_logger function
GLPP_LOGGER = logging.getLogger('gulppy')
GLPP_LOGGER.addHandler(logging.NullHandler())

def init_logger():
    """
    A util function to init a logger. You can use this one or use your own.
    This function is used for testing.
    :return:
    """
    # create console handler and set level to debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    GLPP_LOGGER.level = logging.DEBUG
    GLPP_LOGGER.addHandler(ch)
