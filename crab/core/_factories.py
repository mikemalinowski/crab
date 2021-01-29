import json

from .component import Component
from .behaviour import Behaviour
from .process import Process

from .. import config
from .. import constants
from ..vendor import factories


_FACTORY_MANAGER = None


class ComponentFactory(factories.Factory):
    """
    Inherited factory which exposes additional functionality to resolve the component
    plugin from a node in maya
    """

    # --------------------------------------------------------------------------
    @classmethod
    def find_from_node(cls, node):
        """
        Convenience function for intantiating a Component class which is
        representative of the given node.

        :param node: Node to generate a component instance for
        :type node: pm.nt.Transform

        :return: crab.Component instance
        """
        while True:

            meta = Component.is_component_root(node)

            if not meta:
                node = node.getParent()
                continue

            component_type = meta.attr(config.META_IDENTIFIER).get()

            if component_type not in factory_manager().components.identifiers():
                return None

            plugin = factory_manager().components.request(component_type)(node)

            plugin.options.update(
                json.loads(meta.attr(config.META_OPTIONS).get()),
            )
            return plugin


# ------------------------------------------------------------------------------
class Factories(object):
    """
    This holds all three factories which a crab rig workflow relies upon
    """

    # --------------------------------------------------------------------------
    def __init__(self):

        # -- This is a library of all the components available
        # -- to the rig
        self.components = ComponentFactory(
            abstract=Component,
            plugin_identifier='identifier',
            versioning_identifier='version',
            paths=constants.PLUGIN_LOCATIONS,
            envvar=constants.PLUGIN_ENVIRONMENT_VARIABLE,
        )

        # -- This stores all the process plugins. These are plugins
        # -- which have the oppotunity to run before and after a rig
        # -- build.
        self.processes = factories.Factory(
            abstract=Process,
            plugin_identifier='identifier',
            versioning_identifier='version',
            paths=constants.PLUGIN_LOCATIONS,
            envvar=constants.PLUGIN_ENVIRONMENT_VARIABLE,
        )

        # -- This is a library of all the behaviours which are available
        # -- to the rig
        self.behaviours = factories.Factory(
            abstract=Behaviour,
            plugin_identifier='identifier',
            versioning_identifier='version',
            paths=constants.PLUGIN_LOCATIONS,
            envvar=constants.PLUGIN_ENVIRONMENT_VARIABLE,
        )

    @property
    def component_abstract(self):
        return Component

    @property
    def behaviour_abstract(self):
        return Behaviour

    @property
    def process_abstract(self):
        return Process


# ------------------------------------------------------------------------------
def factory_manager():
    """
    Resolving large plugin banks for multiple factories can take time, therefore
    its not something we want to be doing too often. To minimise the overhead
    of this we use a cached factory and always return the cache.

    :return: Factories instance
    """
    global _FACTORY_MANAGER

    if _FACTORY_MANAGER:
        return _FACTORY_MANAGER

    _FACTORY_MANAGER = Factories()

    return _FACTORY_MANAGER
