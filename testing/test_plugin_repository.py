# -*- coding: utf-8 -*-
"""
Test for the Gulppy plugin repository core class
"""
import unittest
import sys
import traceback
from gulppy.core.glpp_plugin_factory import MutableModeEnum
from gulppy.core.glpp_plugin_repository import GlppPluginRepository
from gulppy.config import GLPP_LOGGER, init_logger
init_logger()


class TestPluginRepository(unittest.TestCase):

    def test_normal_repo_1_immutable(self):
        """
        We use testing_data/normal/repo_1 :
        This repo contains 2 plugins representing the same plugin but for different versions.
        The modules names are the same but as we are in an immutable context, no exception should be raised.
        Size of sys.modules should be kept unchanged

        TIPS : the immutable context is the best practice !
        """
        GLPP_LOGGER.info('\n\n>>  test_normal_repo_1_immutable\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        repo_path = "../testing_data/normal/repo_1"
        try:
            o_repo = GlppPluginRepository(repo_path=repo_path,
                                          repo_tag="normal_repo_1")
            o_repo.load_plugins(mutable_mode=MutableModeEnum.IMMUTABLE,
                                err_mod_dup=True,
                                err_import=True)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            o_repo.display()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))

    def test_normal_repo_1_mutable_with_exception(self):
        """
        We use testing_data/normal/repo_1 :
        This repo contains 2 plugins representing the same plugin but for different versions.
        The modules names are the same and we are in an mutable context : an exception should be raised.
        (the err_mod_dup is set to True so that exceptions are not treated silently !)

        TIPS : the immutable context is the best practice !
        """
        GLPP_LOGGER.info('\n\n>>  test_normal_repo_1_mutable_with_exception\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        repo_path = "../testing_data/normal/repo_1"
        try:
            o_repo = GlppPluginRepository(repo_path=repo_path,
                                          repo_tag="normal_repo_1")
            GLPP_LOGGER.info('We expect an exception to occure because of module names duplicates')
            o_repo.load_plugins(mutable_mode=MutableModeEnum.MUTABLE,
                                err_mod_dup=True, # Exception will be raised because of the 2 modules with same names
                                err_import=True)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            o_repo.display()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))

    def test_normal_repo_1_mutable_with_non_blocking_error(self):
        """
        We use testing_data/normal/repo_1 :
        This repo contains 2 plugins representing the same plugin but for different versions.
        The modules names are the same and we are in an mutable context : an exception should be raised.
        (the err_mod_dup is set to False so that exceptions is treated silently as a non blocking error !)
        Only one module should be imported (the first to be proceed => we dont know which one !)

        TIPS : the immutable context is the best practice !
        """
        GLPP_LOGGER.info('\n\n>>  test_normal_repo_1_mutable_with_non_blocking_error\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        repo_path = "../testing_data/normal/repo_1"
        try:
            o_repo = GlppPluginRepository(repo_path=repo_path,
                                          repo_tag="normal_repo_1")
            GLPP_LOGGER.info('We expect a warning to occure because of module names duplicates')
            o_repo.load_plugins(mutable_mode=MutableModeEnum.MUTABLE,
                                # Exception will be treated as a non blocking error
                                # But only one plugin should be fully loaded
                                err_mod_dup=False,
                                err_import=True)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            o_repo.display()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))


if __name__ == '__main__':
    unittest.main()