# -*- coding: utf-8 -*-
"""
Test for the Gulppy plugin manager core class
"""
import unittest
import sys
import traceback
from gulppy.core.glpp_plugin_factory import MutableModeEnum
from gulppy.core.glpp_plugin_manager import GlppPluginManager, GlppPluginDuplicatePolicy
from gulppy.config import GLPP_LOGGER, init_logger
init_logger()


class TestPluginManager(unittest.TestCase):

    def test_normal_repo_1_repo_3_immutable(self):
        """
        We use testing_data/normal/repo_1 and repo_3
        Size of sys.modules should be kept unchanged

        TIPS : the immutable context is the best practice !
        """
        GLPP_LOGGER.info('\n\n>>  test_normal_repo_1_repo_3_immutable\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        repos = [ "../testing_data/normal/repo_1",
                  "../testing_data/normal/repo_3"]
        try:
            pmanager = GlppPluginManager()
            for i, repo_path in enumerate(repos):
                pmanager.add_repository(repo_path=repo_path, repo_tag="tag-{}".format(i+1))
            pmanager.load(plugin_duplicate_policy=GlppPluginDuplicatePolicy.ERROR,
                          err_mod_dup=True,
                          err_import=True,
                          mutable_mode=MutableModeEnum.IMMUTABLE)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            pmanager.display()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))
            # Not optimal - This is only for test purpose
            for (pname, pversion) in pmanager.get_plugins_as_dict().keys():
                GLPP_LOGGER.info('** Plugin {} {}'.format(pname, pversion))
                cplugin = pmanager.get_plugin_by_name_and_version(plugin_name=pname, plugin_version=pversion)
                cplugin.display_modules()
                GLPP_LOGGER.info('Call current plugin <*.call_lib_function()>')
                # This part is specific to the plugins modules implementation
                # All plugins here share the same architecture
                cplugin.get_module('my_plugin.plugin_1_main').call_lib_function()

    def test_normal_repo_1_repo_2_immutable_duplicate_error_policy(self):
        """
        We use testing_data/normal/repo_1 and repo_2
        Size of sys.modules should be kept unchanged
        Those two repositories have duplicate plugins
        => With "ERROR" policy an Exception should be raised

        TIPS : the immutable context is the best practice !
        """
        GLPP_LOGGER.info('\n\n>>  test_normal_repo_1_repo_2_immutable_duplicate_error_policy\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        repos = [ "../testing_data/normal/repo_1",
                  "../testing_data/normal/repo_2"]
        try:
            pmanager = GlppPluginManager()
            for i, repo_path in enumerate(repos):
                pmanager.add_repository(repo_path=repo_path, repo_tag="tag-{}".format(i+1))
            pmanager.load(plugin_duplicate_policy=GlppPluginDuplicatePolicy.ERROR,
                          err_mod_dup=True,
                          err_import=True,
                          mutable_mode=MutableModeEnum.IMMUTABLE)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            pmanager.display()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))
            # Not optimal - This is only for test purpose
            for (pname, pversion) in pmanager.get_plugins_as_dict().keys():
                GLPP_LOGGER.info('** Plugin {} {}'.format(pname, pversion))
                cplugin = pmanager.get_plugin_by_name_and_version(plugin_name=pname, plugin_version=pversion)
                cplugin.display_modules()
                GLPP_LOGGER.info('Call current plugin <*.call_lib_function()>')
                # This part is specific to the plugins modules implementation
                # All plugins here share the same architecture
                cplugin.get_module('my_plugin.plugin_1_main').call_lib_function()

    def test_normal_repo_1_repo_2_immutable_duplicate_ignore_policy(self):
        """
        We use testing_data/normal/repo_1 and repo_2
        Size of sys.modules should be kept unchanged
        Those two repositories have duplicate plugins
        => With "IGNORE" policy the duplicates plugin should be ignored

        TIPS : the immutable context is the best practice !
        """
        GLPP_LOGGER.info('\n\n>>  test_normal_repo_1_repo_2_immutable_duplicate_ignore_policy\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        repos = [ "../testing_data/normal/repo_1",
                  "../testing_data/normal/repo_2"]
        try:
            pmanager = GlppPluginManager()
            for i, repo_path in enumerate(repos):
                pmanager.add_repository(repo_path=repo_path, repo_tag="tag-{}".format(i+1))
            pmanager.load(plugin_duplicate_policy=GlppPluginDuplicatePolicy.IGNORE,
                          err_mod_dup=True,
                          err_import=True,
                          mutable_mode=MutableModeEnum.IMMUTABLE)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            pmanager.display()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))
            # Not optimal - This is only for test purpose
            for (pname, pversion) in pmanager.get_plugins_as_dict().keys():
                GLPP_LOGGER.info('** Plugin {} {}'.format(pname, pversion))
                cplugin = pmanager.get_plugin_by_name_and_version(plugin_name=pname, plugin_version=pversion)
                cplugin.display_modules()
                GLPP_LOGGER.info('Call current plugin <*.call_lib_function()>')
                # This part is specific to the plugins modules implementation
                # All plugins here share the same architecture
                cplugin.get_module('my_plugin.plugin_1_main').call_lib_function()

    def test_normal_repo_1_repo_2_immutable_duplicate_overload_policy(self):
        """
        We use testing_data/normal/repo_1 and repo_2
        Size of sys.modules should be kept unchanged
        Those two repositories have duplicate plugins
        => With "OVERLOAD" policy the duplicates plugin should replace the former one

        TIPS : the immutable context is the best practice !
        """
        GLPP_LOGGER.info('\n\n>>  test_normal_repo_1_repo_2_immutable_duplicate_overload_policy\n')
        GLPP_LOGGER.info('Size of sys.modules before load : {}'.format(len(sys.modules)))
        repos = [ "../testing_data/normal/repo_1",
                  "../testing_data/normal/repo_2"]
        try:
            pmanager = GlppPluginManager()
            for i, repo_path in enumerate(repos):
                pmanager.add_repository(repo_path=repo_path, repo_tag="tag-{}".format(i+1))
            pmanager.load(plugin_duplicate_policy=GlppPluginDuplicatePolicy.OVERLOAD,
                          err_mod_dup=True,
                          err_import=True,
                          mutable_mode=MutableModeEnum.IMMUTABLE)
        except Exception as e:
            GLPP_LOGGER.error('Encountered exception : \n{}'.format(e))
            GLPP_LOGGER.error(traceback.format_exc())
        else:
            pmanager.display()
        finally:
            GLPP_LOGGER.info('Size of sys.modules after load : {}'.format(len(sys.modules)))
            # Not optimal - This is only for test purpose
            for (pname, pversion) in pmanager.get_plugins_as_dict().keys():
                GLPP_LOGGER.info('** Plugin {} {}'.format(pname, pversion))
                cplugin = pmanager.get_plugin_by_name_and_version(plugin_name=pname, plugin_version=pversion)
                cplugin.display_modules()
                GLPP_LOGGER.info('Call current plugin <*.call_lib_function()>')
                # This part is specific to the plugins modules implementation
                # All plugins here share the same architecture
                cplugin.get_module('my_plugin.plugin_1_main').call_lib_function()


if __name__ == '__main__':
    unittest.main()