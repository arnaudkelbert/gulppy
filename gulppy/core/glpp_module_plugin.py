# -*- coding: utf-8 -*-
"""
Gulppy Module Plugin class definition
"""
from pathlib import Path
from typing import NoReturn, List, Dict, Tuple
import types
from gulppy.core.glpp_abstract_plugin import GlppAbstractPlugin, safe_python_path, GlppPluginLoadStatus
from gulppy.core.glpp_plugin_factory import GlppPluginFactory
from gulppy.core.glpp_module_loader import load_module
from gulppy.config import GLPP_LOGGER



@GlppPluginFactory.register('module')
class GlppModulePlugin(GlppAbstractPlugin):
    """
    Module plugin class implementation

    This implementation is based on an explicit declaration of the modules that have to be imported.
    Therefore it does not import python modules that may be present in the package and not somehow used by
    the declared modules.
    """
    IMMUTABLE_SYS_PATH_MODULE = True

    def __init__(self,
                 plugin_desc: str,
                 load: bool = True) -> None:
        super().__init__(plugin_desc, load)

    def _load(self):
        """
        Method to load all python modules declared as main modules in description file
        This implementation overrides AbstractPlugin.load abstract method.
        :return:
        """
        self._load_all_modules(self.desc_main_modules)

    def _load_module(self, module_name: str, file: str) -> Tuple[types.ModuleType, List]:
        """
        Load a python module file.

        If IMMUABLE_SYS_PATH_MODULE is set to True (default behaviour), the sys.path and sys.modules variables are not
        impacted by the new loaded module. Then the new loaded module cannot be accessed by sys.modules., but by the
        local class member self._modules using the module_tag as a key (@see _load_all_modules)

        :param module_tag: the module name that will be used as the module name.
        :param file: path of the module
        :return: a tuple containing the module and the list of added modules (dependancies)
        """
        GLPP_LOGGER.debug('Loading module <{}> from file {}...'.format(module_name, file))
        file = safe_python_path(path=file, root=Path(self.plugin_desc).resolve().parent)
        module, context_modules = load_module(module_fullname=module_name,
                                              module_path=file,
                                              module_root_path=self.python_path,
                                              immutable=self.__class__.IMMUTABLE_SYS_PATH_MODULE)
        return module, context_modules

    def _load_all_modules(self, main_modules_desc: Dict[str, str]) -> NoReturn:
        """
        Load all modules declared in the main_modules_desc dictionary

        This method add the _indirect_modules member as a list. It contains all modules that are inserted as dependancies
        for all the independantly loaded modules.
        Note : _indirect_modules and _modules members could have intersections.

        :param main_modules_desc: dictionary containing the modules to load as key=module_tag and value=module_file
        :return: None
        """
        self._indirect_modules = []
        self._modules = {}
        for module_tag, module_file in main_modules_desc.items():
            module, context_modules = self._load_module(module_name=module_tag, file=module_file)
            self._modules[module_tag] = module
            self._indirect_modules.extend(context_modules)
        self._i_modules = {k: v for k, v in self._indirect_modules if k not in self._modules}
        self._load_status = GlppPluginLoadStatus.LOADED

