# -*- coding: utf-8 -*-
"""
Gulppy Abstract Plugin class definition
"""
from abc import ABCMeta, abstractmethod
import yaml
from pathlib import Path
from typing import NoReturn
import types
import pandas as pd
from enum import Enum
from gulppy.core import glpp_exceptions, glpp_module_loader
from gulppy.config import GLPP_LOGGER

DESCR_FILENAME = 'descr.yaml'


def safe_python_path(path: str or Path, root: str or Path) -> Path:
    """
    Returns a safe python path from input argument
    :param path: input path
    :return: a safe path
    """
    if Path(path).is_absolute():
        return Path(path)
    else:
        return Path(root).joinpath(Path(path))


class GlppPluginLoadStatus(Enum):
    """
    Plugin load status enumeration
    """
    NOT_LOADED = 1
    """
    Not loaded status
    """
    LOADED = 2
    """
    Loaded status
    """


class GlppAbstractPlugin(object, metaclass=ABCMeta):
    """
    Abstract class for a Gulppy plugin.

    A Gulppy plugin can contain one or more dynamically loaded python module(s).
    A loaded module can be classified as a direct module or an internal modules :
    - direct module represents a module directly adressed by the plugin description.
    - internal module represents a module that is physically present in the plugin package but not directly adressed
      by the plugin description. They are needed as dependancies of the direct module.

    Direct modules are stored in the _modules member variable as a dictionnary.
    Internal modules are stored in the _i_modules member variable as a dictionnary.

    _modules and _i_modules should be constructed with no intersection !
    """
    IMMUTABLE_SYS_PATH_MODULE = True

    def __init__(self,
                 plugin_desc: str,
                 load: bool = True) -> None:
        """
        Constructor
        :param plugin_desc: path of the plugin description yaml file
        :param load: boolean flag to load modules at creation
        """
        self.name = None
        self.version = None
        self.desc_main_modules = None
        self.python_path = None
        self.plugin_desc = plugin_desc
        self.sys_context_callback_init = glpp_module_loader.sys_context_callback_init
        self.sys_context_callback_terminate = glpp_module_loader.sys_context_callback_terminate
        self.sys_context_callback_init_script = None
        self.sys_context_callback_terminate_script = None
        self._modules = {}
        self._i_modules = {}
        self._introspect()
        self._load_status = GlppPluginLoadStatus.NOT_LOADED
        if load:
            self.load()

    @property
    def plugin_desc(self):
        """
        Get _plugin_desc
        """
        return self._plugin_desc

    @plugin_desc.setter
    def plugin_desc(self, value):
        self._plugin_desc = value

    @property
    def name(self):
        """
        Get _name
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def version(self):
        """
        Get _plugin_desc
        """
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def desc_main_modules(self):
        """
        Get _desc_main_modules
        """
        return self._desc_main_modules

    @desc_main_modules.setter
    def desc_main_modules(self, value):
        self._desc_main_modules = value

    @property
    def python_path(self):
        """
        Get _python_path
        """
        return self._python_path

    @python_path.setter
    def python_path(self, value):
        self._python_path = value

    @property
    def load_status(self):
        """
        Get _load_status
        """
        return self._load_status

    @load_status.setter
    def load_status(self, value):
        self._load_status = value

    @classmethod
    def get_unique_id_cls(cls, plugin_name: str, plugin_version: str) -> str:
        """
        Construct a string label for a plugin given its name and version
        :param plugin_name: the plugin name
        :param plugin_version: the plugin version
        :return: a supposed unique id
        """
        return '{0}__{1}'.format(plugin_name, plugin_version)

    def get_unique_id(self) -> str:
        """
        Returns a plugin unique supposed id constructed with module name and version
        :return:
        """
        return self.__class__.get_unique_id_cls(self.name, self.version)

    def _introspect(self) -> NoReturn:
        """
        Introspection from yaml plugin description file
        :return: None
        """
        self.plugin_root = Path(self._plugin_desc).resolve().parent
        with open(Path(self._plugin_desc).resolve()) as fp:
            parsed = yaml.load(fp, Loader=yaml.FullLoader)
            self.name = parsed['plugin_name']
            self.version = parsed['plugin_version']
            self.desc_main_modules = parsed['plugin_main_modules']
            self.python_path = [safe_python_path(path=cpath, root=Path(self.plugin_desc).resolve().parent)
                                for cpath in parsed['python_path']]
            try:
                self.sys_context_callback_init_script = parsed["plugin_hacks"]["sys_context_callback_init"]
            except KeyError:
                self.sys_context_callback_init_script = None
            else:
                GLPP_LOGGER.debug("A hack is defined for sys_context_callback_init")
            try:
                self.sys_context_callback_terminate_script = parsed["plugin_hacks"]["sys_context_callback_terminate"]
            except KeyError:
                self.sys_context_callback_terminate_script = None
            else:
                GLPP_LOGGER.debug("A hack is defined for sys_context_callback_terminate")

    def get_path(self, path: str or Path) -> Path:
        """
        This return a path with variables changes
        """
        return Path(str(path).replace("@PLUGIN_ROOT@", str(self.plugin_root)))

    def load(self):
        """
        This method wraps the call of _load abstract method
        :return:
        """
        # We set here the sys_context hacks if defined
        if self.sys_context_callback_init_script is not None:
            sys_context_callback_init_script = self.get_path(path=self.sys_context_callback_init_script)
            with open(sys_context_callback_init_script, 'rb') as fp:
                c_locals = {}
                exec(compile(fp.read(), sys_context_callback_init_script, 'exec'), globals(), c_locals)
                self.sys_context_callback_init = c_locals['sys_context_callback_init']

        if self.sys_context_callback_terminate_script is not None:
            sys_context_callback_terminate_script = self.get_path(path=self.sys_context_callback_terminate_script)
            with open(sys_context_callback_terminate_script, 'rb') as fp:
                c_locals = {}
                exec(compile(fp.read(), sys_context_callback_terminate_script, 'exec'), globals(), c_locals)
                self.sys_context_callback_terminate = c_locals['sys_context_callback_terminate']

        try:
            self._load()
        except glpp_exceptions.ModuleAlreadyExistsError as e:
            raise glpp_exceptions.PluginModuleSysModuleDuplicateError(e.msg_args[0],
                                                                      self.name,
                                                                      self.version,
                                                                      self.plugin_desc,
                                                                      e.msg_args[1]) from e
        except Exception as e:
            raise glpp_exceptions.PluginImportError(self.name,
                                                    self.version,
                                                    self.plugin_desc,
                                                    str(e)) from e

    @abstractmethod
    def _load(self):
        """
        This method should implement the load of a plugin and set the load status member
        :return:
        """
        pass

    def get_module(self, key: str) -> types.ModuleType:
        """
        Get a module in the current plugin from its key
        First the method looks up in the direct modules dictionnary.
        If the key is not found, it is then looked up in the internal modules dictionnary.
        An exception is raised if the key is not found.
        :param key: the key of the module
        :return: a python module
        """
        try:
            return self._modules[key]
        except KeyError:
            try:
                return self._i_modules[key]
            except KeyError:
                raise glpp_exceptions.UnknownModuleError(self.name, self.version, key)

    def display_modules(self) -> NoReturn:
        """
        Display plugin modules informations
        :return:
        """
        names = [k for k, _ in self._modules.items()] + [k for k, _ in self._i_modules.items()]
        files = [v.__file__ for _, v in self._modules.items()] + [v.__file__ for _, v in self._i_modules.items()]
        flags = [True for k, _ in self._modules.items()] + [False for k, _ in self._i_modules.items()]
        df = pd.DataFrame({'name': names, 'files': files, 'main_flag': flags})
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        GLPP_LOGGER.info(df.to_string(index=False))

    @classmethod
    def get_plugin_mode(cls, plugin_desc: str or Path) -> str:
        """
        Get plugin mode from the plugin description file.
        :param plugin_desc:
        :return: the plugin mode
        """
        with open(str(plugin_desc), 'r') as fp:
            try:
                parsed = yaml.load(fp, Loader=yaml.FullLoader)
                return parsed['plugin_mode']
            except KeyError:
                raise glpp_exceptions.PluginDescriptionMissingProperty("plugin_mode", plugin_desc)
