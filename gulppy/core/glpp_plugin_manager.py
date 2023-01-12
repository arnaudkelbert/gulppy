# -*- coding: utf-8 -*-
"""
Gulppy Plugin manager definition
"""
import pandas as pd
from typing import NoReturn, Dict
from enum import Enum
from core.glpp_abstract_plugin import GlppPluginLoadStatus, GlppAbstractPlugin
from core.glpp_plugin_repository import GlppPluginRepository
from core.glpp_plugin_factory import MutableModeEnum
from core import glpp_exceptions
from config import GLPP_LOGGER


class GlppPluginDuplicatePolicy(Enum):
    """
    Policies defined if plugin duplicates are encountered across multiples plugin repositories.
    """
    ERROR = 1
    """
    An error is raised if duplicates plugins are found across multiples repositories.
    """
    IGNORE = 2
    """
    Ignore the duplicate and keep the first plugin of its name and version.
    """
    OVERLOAD = 3
    """
    Take the new duplicate as the reference plugin for name and version.
    """


class GlppPluginManager(object):
    """
    A Plugin manager for plugins and repositories management.
    This is a high level class.
    """
    def __init__(self) -> None:
        self.repositories = []
        self.plugins = {}

    def add_repository(self, repo_path: str, repo_tag: str = None) -> bool:
        """
        Add a repository to the manager
        :param repo_path: the path of the repository to add
        :param repo_tag: the tag to use for the repository
        :return: True if repository is added to the context, False otherwise (in case of duplicate)
        """
        GLPP_LOGGER.info('Adding plugin repository : {}'.format(repo_path))
        # Create the repository object (does not load the python modules inside)
        if not repo_path in [r.repo_path for r in self.repositories]:
            crepo = GlppPluginRepository(repo_path=repo_path, repo_tag=repo_tag)
            self.repositories.append(crepo)
            return True
        else:
            GLPP_LOGGER.info('Repository {} already exists in current context.'.format(repo_path))
            return False

    def load(self,
             plugin_duplicate_policy: GlppPluginDuplicatePolicy = GlppPluginDuplicatePolicy.ERROR,
             err_mod_dup: bool = True,
             err_import: bool = True,
             mutable_mode: MutableModeEnum = MutableModeEnum.DEFAULT) -> NoReturn:
        """
        Load all the repositories plugins

        :param plugin_duplicate_policy: option to manage duplicate plugins across different repositories. You should use
                                        ERROR in case of mutable mode otherwise you may have stange behaviour.
                                        (Please note that the mutable mode is not advised)
        :param err_mod_dup: An option flag to throw an exception in case of duplicates modules in sys.modules.
                            It is advised to set it to True.
        :param err_import: An option flag to throw an exception in case of an error during a module import.
                           It is advised to set it to True.
        :param mutable_mode: Mutable mode for plugins.
        :return:
        """
        self.plugins = {}
        for repo in self.repositories:
            # Load plugins in current repository
            # If mutable_mode is set to mutable and err_mod_dup is True : the load_plugins method will raise an
            # exception. We do not catch it here : its a fatal one that should be treated by the caller.
            # If there is an import error : its a fatal error that should be treated by the caller.
            repo.load_plugins(mutable_mode=mutable_mode, err_mod_dup=err_mod_dup, err_import=err_import)

            # Plugins should be uniquely defined by their name and version.
            # If multiples repositories contains the same unique plugin (regarding its name and version)
            # then this methods should raise an exception.
            # Note : a repositories cannot contains plugin duplicates (@see GlppPluginRepository.initialize())
            repo_df = repo.get_list_of_plugins_as_dataframe(only_loaded=True)
            plugins_df = self.get_list_of_plugins_as_dataframe(only_loaded=True)
            plugins_duplicates = pd.merge(plugins_df, repo_df, how='inner', on=['name', 'version'])
            plugins_duplicates.dropna(inplace=True)

            if len(plugins_duplicates) > 0:
                # There is atleast one duplicate !
                if plugin_duplicate_policy == GlppPluginDuplicatePolicy.ERROR:
                    # Raise an error according to the policy
                    dup_as_string = ','.join(['{}:{}'.format(*v) for v in plugins_duplicates[['name', 'version']].values])
                    raise glpp_exceptions.PluginDuplicateError(dup_as_string, repo.repo_path)

                elif plugin_duplicate_policy == GlppPluginDuplicatePolicy.IGNORE:
                    # We got to ignore the duplicates and add the others
                    plugin_to_add = {(cplugin_name, cplugin_version): (cplugin, repo)
                                     for (cplugin_name, cplugin_version), cplugin in repo.plugins.items()
                                     if not (cplugin_name, cplugin_version) in plugins_duplicates[['name', 'version']].values}
                    print('plugin to add: ', plugin_to_add)

                elif plugin_duplicate_policy == GlppPluginDuplicatePolicy.OVERLOAD:
                    # Add all plugins in the current repo. The dict update will overwrite the plugin associated
                    # with the key
                    plugin_to_add = {(cplugin_name, cplugin_version): (cplugin, repo)
                                     for (cplugin_name, cplugin_version), cplugin in repo.plugins.items()}
                    print('plugin to add: ', plugin_to_add)
            else:
                plugin_to_add = {(cplugin_name, cplugin_version): (cplugin, repo)
                                 for (cplugin_name, cplugin_version), cplugin in repo.plugins.items()}

            self.plugins.update(plugin_to_add)

    def get_list_of_plugins_as_dataframe(self, only_loaded : bool = False) -> pd.DataFrame:
        """
        Get the list of plugins as a pandas dataframe with the columns : name, version, status, repo_path and repo_tag
        :param only_loaded: a flag to filter loaded plugins
        :return: a pandas dataframe
        """
        data = {'name': [k[0] for k, _ in self.plugins.items()],
                'version': [k[1] for k, _ in self.plugins.items()],
                'status': [v[0].load_status for _, v in self.plugins.items()],
                'repo_path': [v[1].repo_path for _, v in self.plugins.items()],
                'repo_tag': [v[1].repo_tag for _, v in self.plugins.items()]}
        df = pd.DataFrame(data)
        if only_loaded:
            df = df[df["status"] == GlppPluginLoadStatus.LOADED]
        return df

    def display(self) -> NoReturn:
        """
        Display the list of plugins to stdout using a dataframe style
        :return:
        """
        GLPP_LOGGER.info('Managed plugins : ')
        df = self.get_list_of_plugins_as_dataframe()
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        GLPP_LOGGER.info(df.to_string(index=False))

    def get_plugins_as_dict(self) -> Dict:
        """
        Get the list of managed plugins as a python dictionnary.
        :return: {(name:str, version:str): (plugin:GlppAbstractPlugin, repository:GlppPluginRepository)}
        """
        return self.plugins

    def get_plugin_by_name_and_version(self, plugin_name: str, plugin_version: str) -> GlppAbstractPlugin:
        """
        Get plugin by its name and version
        :param plugin_name: the plugin name
        :param plugin_version: the plugin version
        :return:
        """
        try:
            return self.get_plugins_as_dict()[(plugin_name, plugin_version)][0]
        except KeyError as e:
            raise glpp_exceptions.PluginNotFound(plugin_name, plugin_version) from e
