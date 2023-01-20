# -*- coding: utf-8 -*-
"""
Test for the Gulppy plugin factory
"""
import unittest
import traceback
import sys
from gulppy.core.glpp_plugin_factory import GlppPluginFactory, MutableModeEnum
from gulppy.config import GLPP_LOGGER, init_logger
init_logger()


class TestPlugin(unittest.TestCase):

    def test_module_plugin_1_immutable(self):
        """
        """
        GLPP_LOGGER.info('\n\n>>  test_module_plugin_1_immutable\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        file_path = "../testing_data/normal/repo_1/plugin_1/descr.yaml"
        try:
            o_plug = GlppPluginFactory.create_plugin(plugin_desc=file_path,
                                   load=True,
                                   mutable_mode=MutableModeEnum.IMMUTABLE)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            o_plug.display_modules()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))


    def test_module_plugin_1_mutable(self):
        """
        """
        GLPP_LOGGER.info('\n\n>>  test_module_plugin_1_mutable\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        #change IMMUTABLE_SYS_PATH_MODULE default behaviour
        file_path = "../testing_data/normal/repo_1/plugin_1/descr.yaml"
        try:
            o_plug = GlppPluginFactory.create_plugin(plugin_desc=file_path,
                                   load=True,
                                   mutable_mode=MutableModeEnum.MUTABLE)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            o_plug.display_modules()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))


    def test_module_plugin_1_mutable_bis(self):
        """
        """
        GLPP_LOGGER.info('\n\n>>  test_module_plugin_1_mutable_bis\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        #change IMMUTABLE_SYS_PATH_MODULE default behaviour
        file_path = "../testing_data/anomaly/repo_1/plugin_1/descr.yaml"
        try:
            o_plug = GlppPluginFactory.create_plugin(plugin_desc=file_path,
                                   load=True,
                                   mutable_mode=MutableModeEnum.MUTABLE)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            o_plug.display_modules()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))


if __name__ == '__main__':
    unittest.main()