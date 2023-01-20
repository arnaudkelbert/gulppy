# -*- coding: utf-8 -*-
"""
Gulppy Plugin factory
"""
from pathlib import Path
from typing import Generator, Callable
from contextlib import contextmanager
from enum import Enum
from gulppy.config import GLPP_LOGGER
from gulppy.core import glpp_exceptions
from gulppy.core.glpp_abstract_plugin import GlppAbstractPlugin


class MutableModeEnum(Enum):
    """
    Enumeration for sys.modules context alteration mode
    """
    DEFAULT = 1
    """
    Use the class specific defined mutable mode. That is the one setted by the class variable IMMUTABLE_SYS_PATH_MODULE
    """
    MUTABLE = 2
    """
    Use a mutable mode.
    """
    IMMUTABLE = 3
    """
    Use a immutable mode
    """


@contextmanager
def mutable_context(plugin_cls: GlppAbstractPlugin,
                    mutable_mode: MutableModeEnum) -> Generator[str, None, None]:
    """
    Create a context using a specific mutable mode
    :param plugin_cls: the plugin class to use in the context
    :param mutable_mode: the mutable mode to activate
    :return:
    """
    mutable_default_value = plugin_cls.IMMUTABLE_SYS_PATH_MODULE
    if mutable_mode == MutableModeEnum.DEFAULT:
        pass
    elif mutable_mode == MutableModeEnum.IMMUTABLE:
        plugin_cls.IMMUTABLE_SYS_PATH_MODULE = True
    elif mutable_mode == MutableModeEnum.MUTABLE:
        plugin_cls.IMMUTABLE_SYS_PATH_MODULE = False
    else:
        pass
    yield
    plugin_cls.IMMUTABLE_SYS_PATH_MODULE = mutable_default_value


class GlppPluginFactory(object):
    GLPP_PLUGIN_REGISTRY = {}
    # A plugin factory method
    @classmethod
    def create_plugin(cls,
                      plugin_desc: str or Path,
                      load: bool = True,
                      mutable_mode: MutableModeEnum = MutableModeEnum.DEFAULT) -> GlppAbstractPlugin:
        """
        A function to create a plugin from its description file
        :param plugin_desc: plugin description file
        :param load: boolean flag to load modules at creation
        :param mutable_mode: mutable mode to use for the plugin load
        :return: a plugin instance
        """
        plugin_mode = GlppAbstractPlugin.get_plugin_mode(plugin_desc)
        try:
            plugin_cls = cls.GLPP_PLUGIN_REGISTRY[plugin_mode]
        except KeyError:
            raise glpp_exceptions.UnknownPluginMode(plugin_mode)
        else:
            with mutable_context(plugin_cls=plugin_cls, mutable_mode=mutable_mode):
                return plugin_cls(plugin_desc=plugin_desc, load=load)


    @classmethod
    def register(cls, name: str) -> Callable:
        """
        Class method to register a plugin class in the factory
        This is aimed to be used as a decorator of plugin classes.

        :param name: name of the plugin class
        :return: the plugin class itself
        """
        def inner_wrapper(wrapped_class: GlppAbstractPlugin) -> Callable:
            if name in cls.GLPP_PLUGIN_REGISTRY:
                GLPP_LOGGER.warning("Plugin class {} is already registered in the factory. "
                                    "It will be overwritten.".format(name))
            cls.GLPP_PLUGIN_REGISTRY[name] = wrapped_class
            return wrapped_class

        return inner_wrapper
