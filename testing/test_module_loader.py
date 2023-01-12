# -*- coding: utf-8 -*-
"""
Test for the Gulppy module loader core module
"""
import unittest
import sys
from gulppy.core import glpp_module_loader
from gulppy.config import GLPP_LOGGER, init_logger
init_logger()


def force_flush_log(function):
    def wrapper(*args):
        f = function(*args)
        #GLPP_LOGGER.getLogger().handlers[0].flush()
        return f
    return wrapper


class TestModuleLoader(unittest.TestCase):

    @force_flush_log
    def test_module_loader_mutable(self):
        """
        """
        GLPP_LOGGER.info('\n\n>>  test_module_loader_mutable\n')
        GLPP_LOGGER.info('Description : load a single python module with sys.path and sys.modules alterations')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))

        mod1, added_modules_1 = glpp_module_loader.load_module(
            module_fullname="my_plugin.plugin_1_main",
            module_path="../testing_data/normal/repo_1/plugin_1/my_plugin/plugin_1_main.py",
            module_root_path=["../testing_data/normal/repo_1/plugin_1/", ],
            immutable=False)
        #mod1 = sys.modules['my_plugin.plugin_1_main']
        GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))
        GLPP_LOGGER.info('Loaded package : {}'.format(mod1.__package__))

        s_info = '\n'.join([' - {} : {}'.format(mod[0], mod) for mod in added_modules_1])
        GLPP_LOGGER.info('List of added modules in sys.modules : \n{}'.format(s_info))
        GLPP_LOGGER.info('Call <mod1.call_lib_function()>')
        mod1.call_lib_function()

    @force_flush_log
    def test_module_loader_immutable(self):
        """
        """
        GLPP_LOGGER.info('\n\n>>  test_module_loader_immutable\n')
        GLPP_LOGGER.info('Description : load a single python module with no sys.path and sys.modules alterations')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))

        mod1, added_modules_1 = glpp_module_loader.load_module(
            module_fullname="my_plugin.plugin_1_main",
            module_path="../testing_data/normal/repo_1/plugin_1/my_plugin/plugin_1_main.py",
            module_root_path=["../testing_data/normal/repo_1/plugin_1/", ],
            immutable=True)
        #mod1 = sys.modules['my_plugin.plugin_1_main']
        GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))
        GLPP_LOGGER.info('Loaded package : {}'.format(mod1.__package__))

        s_info = '\n'.join([' - {} : {}'.format(mod[0], mod) for mod in added_modules_1])
        GLPP_LOGGER.info('List of added modules in sys.modules : \n{}'.format(s_info))
        GLPP_LOGGER.info('Call <mod1.call_lib_function()>')
        mod1.call_lib_function()


if __name__ == '__main__':
    unittest.main()