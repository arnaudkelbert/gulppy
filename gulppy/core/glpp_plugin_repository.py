# -*- coding: utf-8 -*-
"""
Gulppy Plugin repository definition
"""
import pathlib
import pandas as pd
from typing import NoReturn, List
from gulppy.core.glpp_abstract_plugin import GlppAbstractPlugin, DESCR_FILENAME, GlppPluginLoadStatus
from gulppy.core.glpp_plugin_factory import create_plugin, MutableModeEnum, mutable_context
from gulppy.core import glpp_exceptions
from gulppy.config import GLPP_LOGGER


class GlppPluginRepository(object):
    """
    A Plugin repository represents a storage space containing one or more plugins.
    """
    def __init__(self, repo_path: str, repo_tag: str) -> None:
        self.repo_path = repo_path
        self.repo_tag = repo_tag
        self.initialize()

    @property
    def repo_path(self):
        """
        Get _repo_path
        """
        return self._repo_path

    @repo_path.setter
    def repo_path(self, value):
        self._repo_path = value

    @property
    def repo_tag(self):
        """
        Get _repo_tag
        """
        return self._repo_tag

    @repo_tag.setter
    def repo_tag(self, value):
        self._repo_tag = value

    def add_plugin(self, plugin: GlppAbstractPlugin) -> None:
        """
        Add a plugin to the current repository plugin list
        :param plugin: plugin to add in the repository
        :return:
        """
        self.plugins_to_load.append(plugin)

    def initialize(self) -> None:
        """
        Initialize plugin in repository.
        :return:
        """
        t_unique = []
        self.plugins_to_load = []
        self.plugins = {}
        desc_list = list(pathlib.Path(self.repo_path).glob('**/{0}'.format(DESCR_FILENAME)))
        if len(desc_list) == 0:
            GLPP_LOGGER.debug('No plugin found in repository {}'.format(self.repo_path))
        else:
            GLPP_LOGGER.debug('Found {} plugin description(s) in repository {}'.format(len(desc_list), self.repo_path))
        for desc_file in desc_list:
            GLPP_LOGGER.debug('Found plugin : {}'.format(desc_file))
            GLPP_LOGGER.debug('Initializing plugin : {}'.format(desc_file))
            try:
                # Here we create the plugin without loading it
                # No need to specify the mutable_mode parameters as it has no effective effect (even if the context
                # is changed in the create_plugin method)
                cplugin = create_plugin(plugin_desc=desc_file,
                                        load=False,
                                        )
            except:
                # TODO : manage exception we want to pass...
                raise
            else:
                GLPP_LOGGER.debug(' -> Plugin : name = {0} - version = {1}'.format(cplugin.name, cplugin.version))
                # Here we manage duplicates error
                if cplugin.get_unique_id() in t_unique:
                    # Duplicate found - force raise an exception here -> cannot predict which plugin to use
                    raise glpp_exceptions.PluginRepositoryDuplicateError(cplugin.name,
                                                                         cplugin.version,
                                                                         self.repo_path)
                else:
                    self.add_plugin(cplugin)
                    t_unique.append(cplugin.get_unique_id())

    def get_list_of_plugins_id(self) -> List[str]:
        """
        Get the list of unique plugin ids in the repository
        :return: the list of unique plugin ids
        """
        return [module.get_unique_id() for module in self.plugins_to_load]

    def get_list_of_plugins_as_dataframe(self, only_loaded: bool = False) -> pd.DataFrame:
        """
        Get the list of plugins described in a pandas dataframe
        :param only_loaded: only consider plugins that have a status equals to LOADED
        :return: a dataframe
        """
        data = {"name": [p.name for p in self.plugins_to_load],
                "version": [p.version for p in self.plugins_to_load],
                "status": [p.load_status for p in self.plugins_to_load]}
        df = pd.DataFrame(data)
        if only_loaded:
            df = df[df["status"] == GlppPluginLoadStatus.LOADED]
        return df

    def display(self) -> NoReturn:
        """
        Display plugins to stdout
        :return: 
        """
        GLPP_LOGGER.info('Repository <{0}> : {1}'.format(self.repo_tag, self.repo_path))
        df = self.get_list_of_plugins_as_dataframe()
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        GLPP_LOGGER.info(df.to_string(index=False))

    def check_duplicates(self) -> bool:
        """
        Check if there are duplicates plugins in the repository
        :return: True
        """
        # by conception there cannot be duplicates of plugins
        # in a repository (@see load_plugins implementation)
        return True

    def load_plugins(self,
                     mutable_mode: MutableModeEnum = MutableModeEnum.DEFAULT,
                     err_mod_dup: bool = True,
                     err_import: bool = True) -> NoReturn:
        """
        Load all plugins found in repository
        :param mutable_mode: Mutable mode for plugins.
        :param err_mod_dup: An option flag to throw an exception in case of duplicates modules in sys.modules.
                            It is advised to set it to True.
        :param err_import: An option flag to throw an exception in case of an error during a module import.
                           It is advised to set it to True.
        :return:
        """
        GLPP_LOGGER.debug('Load plugins for repo {}'.format(self.repo_path))
        self.plugins = {}
        for cplugin in self.plugins_to_load:
            try:
                with mutable_context(plugin_cls=cplugin.__class__, mutable_mode=mutable_mode):
                    cplugin.load()
            except glpp_exceptions.PluginModuleSysModuleDuplicateError as e:
                GLPP_LOGGER.error(str(e))
                if err_mod_dup:
                    raise
                else:
                    # ignore error : module is just not loaded
                    pass
            except glpp_exceptions.PluginImportError as e:
                if err_import:
                    raise
                else:
                    GLPP_LOGGER.warning(str(e))
            else:
                self.plugins[(cplugin.name, cplugin.version)] = cplugin

    def get_plugin_by_name_and_version(self, plugin_name: str, plugin_version: str) -> GlppAbstractPlugin:
        """
        Get plugin by its name and version
        :param plugin_name: name of the plugin
        :param plugin_version: version of the plugin
        :return: the plugin if it exists
        """
        try:
            return self.plugins[(plugin_name, plugin_version)]
        except KeyError:
            raise glpp_exceptions.PluginNotExistsInRepository(plugin_name, plugin_version, self.repo_path)
