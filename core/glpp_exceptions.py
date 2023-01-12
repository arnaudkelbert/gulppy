# -*- coding: utf-8 -*-
"""
Gulppy dynamic exceptions definition
"""
import json
import inspect
import os
from typing import Type

LOCAL_PATH = os.path.normpath(os.path.join(os.path.abspath(inspect.stack()[0][1]), '..'))
EXCEPTIONS_DESC_FILE = os.path.join(LOCAL_PATH, "exceptions.json")
EXCEPTIONS_MSG = {}


class GlppException(Exception):
    """
    A gulppy exception class
    """
    pass


with open(EXCEPTIONS_DESC_FILE, 'r') as fp:
    for type_name, info in json.load(fp).items():
        message = info['message']
        if len(info['descr']) > 0:
            message += '\n--------------------------------------------\n'\
                   'Exception description :\n{}'.format(info['descr'])
        EXCEPTIONS_MSG[type_name] = message


def create_exception(type_name: str) -> Type:
    """
    Exception factory
    :param type_name: name for the created class
    :return: a GlppException class type
    """
    def init(self, *args):
        self.msg_args = args
        msg = EXCEPTIONS_MSG[type_name].format(*args)
        return GlppException.__init__(self, msg)
    cls = type(type_name, (GlppException,), {'__init__': init})
    return cls


# Let's call the factory for each entry declared in exceptions.json
# We could have done here a dynamic class creation but we declare them
# explicitly here in order to not generate pylint warning !
ModuleAlreadyExistsError = create_exception("ModuleAlreadyExistsError")
PluginDuplicateError = create_exception("PluginDuplicateError")
PluginRepositoryDuplicateError = create_exception("PluginRepositoryDuplicateError")
PluginModuleSysModuleDuplicateError = create_exception("PluginModuleSysModuleDuplicateError")
PluginImportError = create_exception("PluginImportError")
PluginNotFound = create_exception("PluginNotFound")
PluginNotExistsInRepository = create_exception("PluginNotExistsInRepository")
UnknownModuleError = create_exception("UnknownModuleError")
PluginDescriptionMissingProperty = create_exception("PluginDescriptionMissingProperty")
UnknownPluginMode = create_exception("UnknownPluginMode")


