# -*- coding: utf-8 -*-
"""
Gulppy Package Plugin class definition
-- NOT YET AVAILABLE --
"""
from core.glpp_abstract_plugin import GlppAbstractPlugin


class GlppPackagePlugin(GlppAbstractPlugin):
    """
    Package plugin class implementation

    This implementation automatically import recursively all modules in the package tree.
    """
    PLUGIN_MODE = 'package'
    IMMUTABLE_SYS_PATH_MODULE = True

    def __init__(self,
                 plugin_desc: str,
                 load: bool = True) -> None:
        super().__init__(plugin_desc, load)

    def _load(self):
        """
        Method to load all python modules in the package
        This implementation overrides AbstractPlugin.load abstract method.
        :return:
        """
        # TODO
        raise NotImplemented
