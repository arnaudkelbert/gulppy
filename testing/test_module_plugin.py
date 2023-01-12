# -*- coding: utf-8 -*-
"""
Test for the Gulppy module plugin core class
"""
import unittest
import sys
import traceback
from gulppy.core.glpp_module_plugin import GlppModulePlugin
from gulppy.config import GLPP_LOGGER, init_logger
init_logger()


def force_flush_log(function):
    def wrapper(*args):
        f = function(*args)
        #GLPP_LOGGER.getLogger().handlers[0].flush()
        return f
    return wrapper


class TestModulePlugin(unittest.TestCase):

    @force_flush_log
    def test_module_plugin_1_immutable(self):
        """
        """
        GLPP_LOGGER.info('\n\n>>  test_module_plugin_1_immutable\n')
        GLPP_LOGGER.info('Description : load a plugin with no sys.path and sys.modules alterations')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        file_path = "../testing_data/normal/repo_1/plugin_1/descr.yaml"
        try:
            o_plug = GlppModulePlugin(plugin_desc=file_path,
                                      load=True)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            o_plug.display_modules()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))

    @force_flush_log
    def test_module_plugin_1_mutable(self):
        """
        """
        GLPP_LOGGER.info('\n\n>>  test_module_plugin_1_mutable\n')
        GLPP_LOGGER.info('Description : load a plugin with sys.path and sys.modules alterations')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))

        #change IMMUTABLE_SYS_PATH_MODULE default behaviour
        # Please note that when using PluginRepository or PluginManager this is done
        # through the context manager
        GlppModulePlugin.IMMUTABLE_SYS_PATH_MODULE = False
        file_path = "../testing_data/normal/repo_1/plugin_1/descr.yaml"
        try:
            o_plug = GlppModulePlugin(plugin_desc=file_path,
                                      load=True)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            o_plug.display_modules()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))
            #restore IMMUTABLE_SYS_PATH_MODULE default behaviour
            GlppModulePlugin.IMMUTABLE_SYS_PATH_MODULE = True

    @force_flush_log
    def test_module_plugin_1_mutable_bis(self):
        """
        """
        GLPP_LOGGER.info('\n\n>>  test_module_plugin_1_mutable\n')
        GLPP_LOGGER.info('Description : load a plugin with sys.path and sys.modules alterations')
        GLPP_LOGGER.info('! This is a reload to force an exception to occure')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))

        #change IMMUTABLE_SYS_PATH_MODULE default behaviour
        # Please note that when using PluginRepository or PluginManager this is done
        # through the context manager
        GlppModulePlugin.IMMUTABLE_SYS_PATH_MODULE = False
        file_path = "../testing_data/anomaly/repo_1/plugin_1/descr.yaml"
        try:
            o_plug = GlppModulePlugin(plugin_desc=file_path,
                                      load=True)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            o_plug.display_modules()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))

            #restore IMMUTABLE_SYS_PATH_MODULE default behaviour
            GlppModulePlugin.IMMUTABLE_SYS_PATH_MODULE = True


if __name__ == '__main__':
    unittest.main()