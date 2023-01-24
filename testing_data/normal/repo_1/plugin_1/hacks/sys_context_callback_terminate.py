def sys_context_callback_terminate(**kwargs):
    from gulppy.config import GLPP_LOGGER
    from gulppy.core import glpp_module_loader
    GLPP_LOGGER.debug("calling a plugin specific sys_context_callback_terminate")
    glpp_module_loader.sys_context_callback_terminate(**kwargs)

