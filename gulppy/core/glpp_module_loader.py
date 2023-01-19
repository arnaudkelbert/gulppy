# -*- coding: utf-8 -*-
"""
Gulppy module loading core functions
"""
from importlib import util as importlib_util
import sys
import os
from pathlib import Path
from typing import Generator, List, Tuple
import types
from contextlib import contextmanager
from gulppy.core import glpp_exceptions
from gulppy.config import GLPP_LOGGER, GLPP_SYS_PATH


@contextmanager
def sys_path_context(dir_path: str or List[str],
                     modules_changes: List,
                     immutable: bool = True) -> Generator[str, None, None]:
    """
    Context for sys.path and sys.modules management used while dynamic loading python modules.
    If immutable is True the state at call will be restored before exiting.
    Each path in dir_path is inserted at the beginning of sys.path. The paths will be inserted in reversing order
    so that the first path in list will be top priority.
    Regardless of the immutable argument value, the modules changes that occurred temporary or permanently are saved in
    the modules_changes buffer.

    Note : loading a module alters the sys.modules dictionary by adding entries for each module imported
    at module execution time.

    :param dir_path: list of paths to add to sys.path
    :param modules_changes: list to serve as a buffer to store the changes that have occurred to sys.modules
    :param immutable: boolean flag to restore sys.path and sys.modules states at exit
    :return:
    """
    if not is_sequence(dir_path):
        dir_path = [dir_path]
    # Extend dir_path to add to sys.path with config.GLPP_SYS_PATH
    # This mechanism can be used when integrating gulppy.
    dir_path.extend(GLPP_SYS_PATH)
    GLPP_LOGGER.debug('Context | sys.path and sys.modules : inserting {} to sys.path'.format(dir_path))

    # save the current states
    old_path = sys.path.copy()
    old_modules = sys.modules.copy()
    # Fix issue #1 - KeyError can occur when loading a module
    # sys.modules = old_modules.copy()

    for cpath in dir_path[::-1]:
        sys.path.insert(0, os.fspath(Path(cpath).resolve()))

    try:
        # Code will be played here
        yield
    finally:
        # store changes in modules_changes
        for k, v in sys.modules.items():
            if k not in old_modules:
                modules_changes.append((k, v))
                continue
            try:
                if v.__file__ != old_modules[k].__file__:
                    modules_changes.append((k, v))
            except AttributeError:
                pass

        # restore previous states
        if immutable:
            GLPP_LOGGER.debug('Context | sys.path and sys.modules : restore previous state'.format(dir_path))
            sys.path = old_path
            # Fix issue #1 - KeyError can occur when loading a module
            for k, v in old_modules.items():
                sys.modules[k] = v
            to_del = [k for k in sys.modules if k not in old_modules]
            for k in to_del:
                del sys.modules[k]


def is_sequence(iterable: List or str) -> bool:
    """
    Check if argument is a sequence (in opposite to a string)
    :param iterable: iterable argument
    :return: True if it is a sequence, False otherwise
    """
    try:
        iterable.strip()
        return False
    except AttributeError:
        return hasattr(iterable, "__getitem__")


def is_package(filename: str) -> bool:
    """
    Check if filename is a python package, ie a __init__.py file
    :param filename: filename
    :return: True if it is a python package, False otherwise
    """
    return os.path.basename(filename).startswith('__init__')


def is_in_package(filename: str) -> bool:
    """
    Check if filename is at first level in a python package, ie a __init__.py file is present in the same directory.
    :param filename: filename
    :return: True if it is in a python package, False otherwise
    """
    for cfile in Path(filename).parent.iterdir():
        if is_package(str(cfile)):
            return True
    return False


def load_module(module_fullname: str,
                module_path: Path or str,
                module_root_path: str or List[str] = (),
                immutable: bool = True) -> Tuple[types.ModuleType, List]:
    """
    Load a python module

    :param module_fullname: name of the loaded module. It can be defined as a '.' joining.
    :param module_root_path: path (or list of path) that needed to be (temporary if immutable) added to the sys.path
    for module loading.
    :param module_path: path of the python module. It is safer to provide an absolute path.
    :param immutable: boolean flag to not permanently alter sys.path and sys.modules
    :return: a tuple (module, added_modules) :
         - module : the effective loaded module
         - added_modules : list of modules added in the loading context. If immutable is True, those modules are
                           not presents in the output context.
    """
    # check if absolute path are given for module_path
    if not Path(module_path).is_absolute():
        old_ = module_path
        module_path = Path(module_path).resolve()
        GLPP_LOGGER.warning('Automatic conversion from relative to absolute path : {} -> {}.\n'
                            'Please provide absolute path'.format(old_, module_path))

    # also check if absolute path are given for module_path
    # first test if module_root_path is a single string or a sequence of paths
    if not is_sequence(module_root_path):
        module_root_path = [module_root_path]
    module_root_path_ = []
    for cpath in module_root_path:
        if not Path(cpath).is_absolute():
            old_ = cpath
            cpath = Path(cpath).resolve()
            GLPP_LOGGER.warning('Automatic conversion from relative to absolute path : {} -> {}.\n'
                                'Please provide absolute path'.format(old_, cpath))
        module_root_path_.append(cpath)
    module_root_path = module_root_path_

    # just to be sure : we replace / by . in module_fullname
    module_fullname = '.'.join(module_fullname.split(os.sep))
    GLPP_LOGGER.debug('Loading module {} from file {}...'.format(module_fullname, module_path))

    if module_fullname in sys.modules:
        # Module already exists in sys.modules
        # If we want sys.modules and sys.path to be mutable we cannot load this module
        if not immutable:
            if not Path(module_path).resolve().samefile(Path(sys.modules[module_fullname].__file__).resolve()):
                # Not the same file
                raise glpp_exceptions.ModuleAlreadyExistsError(module_fullname, sys.modules[module_fullname])
            else:
                # Already loaded
                return sys.modules[module_fullname], []
        else:
            if not Path(module_path).resolve().samefile(Path(sys.modules[module_fullname].__file__).resolve()):
                GLPP_LOGGER.warning('An existing module with the same name but pointing to an other file already exists'
                                    ' in sys.modules for module {}'.format(sys.modules[module_fullname]))

    # load module in a context in order to manage mutable or immutable sys.path and sys.module
    # if immutable is True : sys.path and sys.module will be restored to their previous state and no reference of the
    # newly loaded module will be done in these variables
    added_modules = []
    with sys_path_context(module_root_path, modules_changes=added_modules, immutable=immutable):
        spec = importlib_util.spec_from_file_location(module_fullname, module_path)
        module = importlib_util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # manually add the modules to the sys.modules
        sys.modules[module_fullname] = module

    if is_package(module_path):
        module.__path__ = [module_path]
        module.__package__ = module_fullname
    else:
        module_package, _, _ = module_fullname.rpartition('.')
        module.__package__ = module_package

    return module, added_modules
