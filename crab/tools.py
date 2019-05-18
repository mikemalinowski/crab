import factories

from . import utils
from . import constants


# -- We do not want to re-populate the tool factories
# -- continously, therefore we cache them globally and
# -- re-use them.
_rig_library = None
_anim_library = None


# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
class AnimTool(object):
    """
    This is the base class of all Animation Tools. To expose an animation
    tool to crab you should reimplement this class. 
    
    Exposed animation tools can be access using the following:
    
    ..code-block:: python
    
        >>> import crab
        >>> 
        >>> for tool in crab.tools.animation().plugins():
        ...     print(tool.identifier)
    
    You can also access specific tools directly and run them using
    the example below.
    
    ..code-block:: python
    
        >>> import crab
        >>> 
        >>> tool = crab.tools.animation().request('Select : All')
        >>> tool().run()
    
    Some tools offer options to tailor their behaviour. The example
    below shows a tool which generates a single mesh made up of a cube
    per joint. This tool allows you to specify the size of the cubes
    being generated.
    
    ..code-block:: python
    
        >>> import crab
        >>> 
        >>> # -- Instance the tool 
        >>> tool = crab.tools.animation().request('Meshes : Generate Cubes')()
        >>> 
        >>> # -- Change the options of the tool
        >>> tool.options.size = 10
        >>> 
        >>> # -- Run the tool
        >>> tool.run()
        
    """
    identifier = ''
    version = 1
    icon = None

    PRIORITY_SHOW = 1
    ALWAYS_SHOW = 2
    DONT_SHOW = 0

    # --------------------------------------------------------------------------
    def __init__(self):
        """
        If you choose to expose additional options to your tool you 
        can add options (key value pairs) to the options dictionary
        by re-implementing and super'ing this function
        """
        self.options = utils.types.AttributeDict()

    # --------------------------------------------------------------------------
    def run(self):
        """
        This is the main exection function for your tool. You may inspect
        the options dictionary of the tool to tailor the behaviour of your
        tool.
        
        :return: True of successful. 
        """
        return True

    # --------------------------------------------------------------------------
    @classmethod
    def viable(cls, node):
        """
        This can be utilised if the tool in question is only viable to
        operate on specific nodes.

        :param node: Node to test viability against.

        :return: Show enum
        """
        return cls.ALWAYS_SHOW


# ------------------------------------------------------------------------------
class RigTool(object):
    """
    This is the base class of all Rigging Tools. To expose a rigging
    tool to crab you should re-implement this class. 
    
    Exposed rigging tools can be access using the following:
    
    ..code-block:: python
    
        >>> import crab
        >>> 
        >>> for tool in crab.tools.rigging().plugins():
        ...     print(tool.identifier)
    
    You can also access specific tools directly and run them using
    the example below.
    
    ..code-block:: python
    
        >>> import crab
        >>> 
        >>> tool = crab.tools.animation().request('Joints : Mirror')
        >>> tool().run()
    
    Some tools offer options to tailor their behaviour. The example
    below shows a tool which generates a single mesh made up of a cube
    per joint. This tool allows you to specify the size of the cubes
    being generated.
    
    ..code-block:: python
    
        >>> import crab
        >>> 
        >>> # -- Instance the tool 
        >>> tool = crab.tools.animation().request('Meshes : Generate Cubes')()
        >>> 
        >>> # -- Change the options of the tool
        >>> tool.options.size = 10
        >>> 
        >>> # -- Run the tool
        >>> tool.run()
        
    """

    identifier = ''
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self):
        """
        If you choose to expose additional options to your tool you 
        can add options (key value pairs) to the options dictionary
        by re-implementing and super'ing this function
        """
        self.options = utils.types.AttributeDict()

    # --------------------------------------------------------------------------
    def run(self):
        """
        This is the main exection function for your tool. You may inspect
        the options dictionary of the tool to tailor the behaviour of your
        tool.
        
        :return: True of successful. 
        """
        return True


# ------------------------------------------------------------------------------
def rigging():
    """
    This function gives access to the rigging tools factory - allowing you
    to access all the tools available. 
    
    Note: This will not re-instance the factory on each call, the factory
    is instanced only on the first called and cached thereafter.
    
    :return: factories.Factory
    """

    # -- If we already have a cached factory return that
    global _rig_library
    if _rig_library:
        return _rig_library

    # -- Instance a new factory
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
    """
    This function gives access to the animation tools factory - allowing you
    to access all the tools available. 
    
    Note: This will not re-instance the factory on each call, the factory
    is instanced only on the first called and cached thereafter.
    
    :return: factories.Factory
    """

    # -- If we already have a cached factory return that
    global _anim_library
    if _anim_library:
        return _anim_library

    # -- Instance a new factory
    _anim_library = factories.Factory(
        abstract=AnimTool,
        plugin_identifier='identifier',
        versioning_identifier='version',
        envvar=constants.PLUGIN_ENVIRONMENT_VARIABLE,
        paths=constants.PLUGIN_LOCATIONS,
    )

    return _anim_library
