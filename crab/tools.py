import factories


from . import utils
from . import constants


# -- Cache the library
_rig_library = None
_anim_library = None


# ------------------------------------------------------------------------------
class AnimTool(object):

    identifier = ''
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self):
        self.options = utils.types.AttributeDict()

    # --------------------------------------------------------------------------
    def run(self):
        return True


# ------------------------------------------------------------------------------
class RigTool(object):

    identifier = ''
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self):
        self.options = utils.types.AttributeDict()

    # --------------------------------------------------------------------------
    def run(self):
        return True


# ------------------------------------------------------------------------------
def rigging():
    global _rig_library
    if _rig_library:
        return _rig_library

    _rig_library = factories.Factory(
        abstract=RigTool,
        plugin_identifier='identifier',
        versioning_identifier='version',
        envvar=constants.PLUGIN_ENVIRONMENT_VARIABLE,
        paths=constants.PLUGIN_LOCATIONS,
    )

    return _rig_library


# ------------------------------------------------------------------------------
def animation():
    global _anim_library
    if _anim_library:
        return _anim_library

    _anim_library = factories.Factory(
        abstract=AnimTool,
        plugin_identifier='identifier',
        versioning_identifier='version',
        envvar=constants.PLUGIN_ENVIRONMENT_VARIABLE,
        paths=constants.PLUGIN_LOCATIONS,
    )

    return _anim_library
