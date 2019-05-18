"""
This module contains the Rig class which is typically the main
entry point to accessing and editing rigs.
"""
import json
import uuid
import factories
import pymel.core as pm

from . import meta
from . import utils
from . import config
from . import create
from . import process
from . import component
from . import constants
from . import behaviour

from .constants import log


# ------------------------------------------------------------------------------
class Rig(object):
    """
    The rig class represents the main interfacing class for a crab rig. From
    here you can apply new components or behaviours as well as gain access
    to applied components.
    
    This example shows how to build a new rig
    
    ..code-block:: python
        
        >>> import crab
        >>> 
        >>> new_rig = crab.Rig.create(name='MyRig')
    
    You can then use this variable to add new components
    
    ..code-block:: python
    
        >>> import crab
        >>> 
        >>> # -- Build a new rig
        >>> new_rig = crab.Rig.create(name='MyRig')
        >>>
        >>> # -- Add a component to the rig
        >>> new_rig.add_component('SRT')
        >>>
        >>> # -- Build the rig
        >>> new_rig.build()
        >>>
        >>> # -- Return the rig to an editable state
        >>> new_rig.edit()
    """

    # --------------------------------------------------------------------------
    def __init__(self, node):

        # -- This is a library of all the components available
        # -- to the rig
        self.components = factories.Factory(
            abstract=component.Component,
            plugin_identifier='identifier',
            versioning_identifier='version',
            paths=constants.PLUGIN_LOCATIONS,
            envvar=constants.PLUGIN_ENVIRONMENT_VARIABLE,
        )

        # -- This stores all the process plugins. These are plugins
        # -- which have the oppotunity to run before and after a rig
        # -- build.
        self.processes = factories.Factory(
            abstract=process.Process,
            plugin_identifier='identifier',
            versioning_identifier='version',
            paths=constants.PLUGIN_LOCATIONS,
            envvar=constants.PLUGIN_ENVIRONMENT_VARIABLE,
        )

        # -- This is a library of all the behaviours which are available
        # -- to the rig
        self.behaviours = factories.Factory(
            abstract=behaviour.Behaviour,
            plugin_identifier='identifier',
            versioning_identifier='version',
            paths=constants.PLUGIN_LOCATIONS,
            envvar=constants.PLUGIN_ENVIRONMENT_VARIABLE,
        )

        # -- Find the rig root to allow all our functionality to
        # -- interact with it
        self.root = meta.get_meta_root(
            node,
            specific_type=config.RIG_TYPE,
        )

    # --------------------------------------------------------------------------
    @classmethod
    def create(cls, name=None):
        """
        This allows you to create a new rig instance. By calling this
        a rig structure will be generated which Crab relies on and an 
        instance of this class will be returned.

        :return: crab.Rig instance
        """
        # -- Create the node which all others will go under
        rig_root = create.generic(
            node_type='transform',
            prefix=config.RIG_ROOT,
            description=name or 'CrabRig',
            side=config.MIDDLE,
        )

        # -- Create our sub-category nodes. These allow us to create
        # -- clear distinctions between our control rig, skeleton and
        # -- guides.
        control_root = create.generic(
            node_type='transform',
            prefix=config.ORG,
            description='ControlRig',
            side=config.MIDDLE,
            parent=rig_root,
        )

        skeleton_root = create.generic(
            node_type='transform',
            prefix=config.ORG,
            description='Skeleton',
            side=config.MIDDLE,
            parent=rig_root,
        )

        guide_root = create.generic(
            node_type='transform',
            prefix=config.ORG,
            description='Guide',
            side=config.MIDDLE,
            parent=rig_root,
        )

        geometry_root = create.generic(
            node_type='transform',
            prefix=config.ORG,
            description='Geometry',
            side=config.MIDDLE,
            parent=rig_root,
        )

        # -- Add the behaviour attribute to the rig node, this is where
        # -- we store a list of all the behaviours assigned to the rig
        rig_root.addAttr(
            config.BEHAVIOUR_DATA,
            dt='string',
        )
        rig_root.attr(config.BEHAVIOUR_DATA).set('[]')

        # -- We now need to create a meta node. Crab uses meta nodes
        # -- to define important root objects. In this instance we need
        # -- to create a meta node tagged as being a rig node type
        meta.create(
            config.RIG_TYPE,
            rig_root,
        )

        # -- The meta system also allows us to store and search by
        # -- label links, therefore we store a link to the three
        # -- category nodes we have just created to allow other processes
        # -- easy access to them.
        meta.tag(
            control_root,
            'ControlRoot',
            rig_root,
        )

        meta.tag(
            skeleton_root,
            'SkeletonRoot',
            rig_root,
        )

        meta.tag(
            guide_root,
            'GuideRoot',
            rig_root,
        )

        meta.tag(
            geometry_root,
            'GeometryRoot',
            rig_root,
        )

        # -- Select the rig root
        pm.select(skeleton_root)

        # -- Debug build information
        log.debug('Created new Crab Rig')

        return Rig(rig_root)

    # --------------------------------------------------------------------------
    def add_component(self, component_type, parent=None, version=None, **options):
        """
        This will add the given component type to the rig as a child
        of the parent. The component type must be available in the 
        component library.
        
        Any options given (keyword arguments outside of the three
        defined ones) will be passed as options to the component instance
        which is generated.
        
        :param component_type: Type of component to add
        :type component_type: str
        
        :param parent: Node to make the component a child of
        :type parent: pm.nt.DagNode
        
        :param version: Optional declaration of the version you want
            to apply to the rig.
        :type version: int or None
        
        :param options: Catch all for any keyword arguments being passed which
            will then be passed directly to the component's option dictionary.
        
        :return: component plugin instance
        """
        # -- Get the skeleton root
        skeleton_root = self.find('SkeletonRoot')[0]
        parent = parent or skeleton_root

        # -- Attempt to get the segment class
        if component_type not in self.components.identifiers():
            log.error(
                (
                    '%s is not a recognised component_type type. Check your '
                    'plugin paths.'
                ) % component_type
            )
            return None

        # -- Instance the segment and update its options
        plugin_type = self.components.request(component_type, version=version)
        plugin = plugin_type()
        plugin.options.update(options)

        # -- Now we request the segment to build its guide
        result = plugin.create_skeleton(parent=parent)

        if not result:
            return plugin

        with utils.contexts.RestoredSelection():
            # -- Get the guide root
            guide_root = self.find('GuideRoot')[0]

            # -- Create the guide, generating a guide root and passing
            # -- that through as the parent
            guide_base = plugin.create_guide_base(guide_root, plugin.root)
            guide_plugin = plugin_type(guide_base)
            guide_plugin.options.update(options)

            guide_plugin.create_guide(
                parent=guide_base,
                skeleton_component=plugin_type(plugin.root)
            )

            # -- We assume failure if we do not get a positive return
            # -- value, in which case log an error
            if not result:
                log.error(
                    'The %s segment failed to create its guide successfully' % (
                        component_type,
                    ),
                )
                return None

            # -- Add a debug message to denote the success of the
            # -- component addition
            log.debug('Successfully created component of type: %s' % component_type)

            return plugin

    # --------------------------------------------------------------------------
    def edit(self):
        """
        Puts the rig into an editable state - removing the control rig
        and exposing the skeleton as well as triggering any guides.
        
        During this process all the stored process plugins will have their
        snapshot and pre functions called.
        
        :return: True if the rig enters edit mode successfully
        """
        # -- If we're already in an editable state we do not need
        # -- to do anything more
        if not self.control_roots():
            log.info('Rig is already editable.')
            return True

        # -- Before removing the control rig we need to give all our
        # -- processes to the oppotunity to snapshop the rig and
        # -- perform any pre-processes
        for proc in self.processes.plugins():
            proc(self).snapshot()

        # -- Now we must remove the control rig
        pm.delete(self.control_roots())

        for proc in self.processes.plugins():
            proc(self).post_edit()

        # -- Show all guides
        for guide_root in self.find('GuideRoot')[0].getChildren():
            guide_root.visibility.set(True)

        return True

    # --------------------------------------------------------------------------
    def build(self):
        """
        This builds the rig. It first places the rig into an editable
        state and removes any guide infrastructure. It will then proceed
        to build the control rig before executing the post functions of
        all the stored processes.
        
        :return: True if the build was successful
        """
        # -- Log the action of starting a rig build
        log.info('Commencing rig build.')

        # -- Ensure the rig is in an editable state
        self.edit()

        for proc in self.processes.plugins():
            proc(self).pre_build()

        # -- Finally we can start cycling components and requested
        # -- a control build
        for component_root in self.skeleton_roots():

            # -- Get the type of component to build
            component_type = meta.get_identifier(component_root)

            # -- Check we have a plugin to build that type
            if component_type not in self.components.identifiers():
                raise Exception('No plugin found for %s' % component_type)

            # -- Instance a plugin for access to all the
            # -- skeletal elements
            skeleton_plugin = self.components.request(component_type)()
            skeleton_plugin.define_root(component_root)

            # -- Instance a plugin for the rig
            rig_plugin = self.components.request(component_type)()

            # -- Update the rig options based on the options
            # -- for the guide
            rig_plugin.options.update(skeleton_plugin.options)

            # -- Attempt to find the parent
            rig_parent = self.find('ControlRoot')[0]
            component_parent = component_root.getParent()

            if component_parent.hasAttr(config.BOUND):
                for potential in component_parent.attr(config.BOUND).inputs():
                    rig_parent = potential
                    break

            guide_plugin = skeleton_plugin.guide()

            # -- Now request a build of the component
            rig_plugin.create_rig(
                parent=rig_plugin.create_control_base(rig_parent),
                skeleton_component=skeleton_plugin,
                guide_component=guide_plugin,
            )

        # -- Now we need to apply any behaviours
        for behaviour_block in self.assigned_behaviours():

            # -- Instance the behaviour
            behaviour_plugin = self.behaviours.request(behaviour_block['type'])(self)

            # -- Update the options for the behaviour plugin
            behaviour_plugin.options.update(behaviour_block['options'])

            # -- Finally apply the behaviour
            behaviour_plugin.apply()

        # -- Hide all guides
        for guide_root in self.find('GuideRoot')[0].getChildren():
            guide_root.visibility.set(False)

        # -- Now the rig has been fully built we can run any post build
        # -- processes
        for proc in self.processes.plugins():
            proc(self).post_build()

    # --------------------------------------------------------------------------
    # noinspection PyTypeChecker
    def add_behaviour(self, behaviour_type, index=-1, **options):
        """
        Adds a behaviour to a rig. A behaviour is different to a component
        in that a a behaviour does not need a skeletal structure and they 
        are built in sequence after all components are built.
        
        Behaviours are typically used to create behaviours which utilise or
        link multiple components together.
        
        Note: This method *does not* invoke the behaviour build it simply
        adds the behaviour to the list of behaviours to be generated when the
        rig is built.
        
        :param behaviour_type: Type of behaviour to apply
        :type behaviour_type: str
        
        :param index: Where is the behaviour list you want the behaviour
            to be placed. By default the behaviour is added to the end
            of the list.
        :type index: int
        
        :param options: Any keyword arguments to be passed down to the 
            behaviour.
        :return: 
        """
        # -- Check to ensure we have a control rig
        # if not self.control_roots():
        #     log.warning('Cannot apply behaviours when not in rig mode')

        # -- Ensure the behaviour is accessible
        if behaviour_type not in self.behaviours.identifiers():
            log.error('%s could not be found.' % behaviour_type)
            return False

        # -- Get the current behaviour data
        current_data = self.assigned_behaviours()

        # -- Create a data block to add it to
        behaviour_data = dict(
            type=behaviour_type,
            options=options,
            id=str(uuid.uuid4()),
        )

        # -- Assign our data into the current data
        current_data.insert(index, behaviour_data)

        # -- Write the updated data back into the attribute
        self.store_behaviour_data(current_data)

        return True

    # --------------------------------------------------------------------------
    def remove_behaviour(self, behaviour_id):
        """
        This will remove the behaviour with the given id. The id's of behaviours
        can be found by calling ```rig.assigned_behaviours()```.
        
        :param behaviour_id: uuid of the behaviour to remove
        :type behaviour_id: str
        
        :return: True if the behaviour was removed
        """
        # -- Get the current behaviour manifest
        current_data = self.assigned_behaviours()

        # -- Look for a behaviour with the given behaviour id
        for idx, behaviour_data in enumerate(current_data):
            if behaviour_data['id'] == behaviour_id:
                current_data.pop(idx)

                self.store_behaviour_data(current_data)
                return True

        return False

    # --------------------------------------------------------------------------
    def shift_behaviour_order(self, behaviour_id, shift_offset):
        """
        Behaviours are built in sequence, this method allows you to shift
        a behaviour forward or backward in the sequence.
        
        :param behaviour_id: The uuid of the behaviour you want to shift, 
            which can be found by calling ```rig.assigned_behaviours()```
        :type behaviour_id: str
        
        :param shift_offset: The offset you want to shift by, so a value
            of 1 would shift it down the list by one, whilst a value of -1
            would shift it up once in the list
        :type shift_offset: int
        
        :return: True if the operation was successful 
        """
        # -- Get the current behaviour manifest
        current_data = self.assigned_behaviours()

        # -- Look for a behaviour with the given behaviour id
        for idx, behaviour_data in enumerate(current_data):
            if behaviour_data['id'] == behaviour_id:

                # -- Offset the data be the required amount
                current_data.insert(
                    current_data.index(behaviour_data) + shift_offset,
                    current_data.pop(current_data.index(behaviour_data)),
                )

                self.store_behaviour_data(current_data)
                return True

        return False

    # --------------------------------------------------------------------------
    def store_behaviour_data(self, behaviour_data):
        """
        Convenience function for storing the entire behaviour list data
        back into the rig. This is useful if you want to make direct 
        modifications to the data.
        
        :param behaviour_data: data structure to the same standards of that
            returned by calling ```rig.assigned_behaviours()```
        :type behaviour_data: list
        
        :return: None 
        """
        # -- Now write the data into the attribute
        self.root.attr(config.BEHAVIOUR_DATA).set(
            json.dumps(behaviour_data),
        )

    # --------------------------------------------------------------------------
    def tag(self, target, label):
        """
        Shortcut for tagging to the Rigs meta root
        
        :param target: Target object to tag 
        :param label: Label to tag with 
        
        :return: None 
        """
        meta.tag(
            target=target,
            label=label,
            meta_root=self.root,
        )

    # --------------------------------------------------------------------------
    def find(self, label):
        """
        Convenience function for performing a meta find against
        the component.
         
        :param label: 
        :return: 
        """
        return meta.find(
            label,
            self.root,
        )

    # --------------------------------------------------------------------------
    def guide_roots(self):
        """
        Returns all the active guide roots within the rig.
        
        :return: list of all the guide roots
        """
        results = list()

        # -- Get the skeleton root
        start_from = self.find('GuideRoot')[0]
        
        for child in reversed(start_from.getChildren(allDescendents=True)):
            if meta.has_meta(child, specific_type=config.COMPONENT_GUIDE_TYPE):
                results.append(child)

        return results

    # --------------------------------------------------------------------------
    def control_roots(self):
        """
        Returns all the component roots within the control hierarchy
        of the rig
        
        :return: list (pm.nt.DagNode, ...)
        """
        results = list()

        # -- Get the skeleton root
        start_from = self.find('ControlRoot')[0]
        
        for child in reversed(start_from.getChildren(allDescendents=True)):
            if meta.has_meta(child, specific_type=config.COMPONENT_RIG_TYPE):
                results.append(child)

        return results

    # --------------------------------------------------------------------------
    def skeleton_roots(self):
        """
        Returns all the component roots within the skeletal hierarchy
        of the rig
        
        :return: list(pm.nt.DagNode, ...)
        """
        results = list()

        # -- Get the skeleton root
        start_from = self.find('SkeletonRoot')[0]

        for child in reversed(start_from.getChildren(allDescendents=True)):
            if meta.has_meta(child, specific_type=config.COMPONENT_SKELETON_TYPE):
                results.append(child)

        return results

    # --------------------------------------------------------------------------
    def assigned_behaviours(self):
        """
        Returns the list of behaviours assigned to the rig. Each behaviour
        is represented by a dictionary.
        
        :return: list(behaviour_dictionary, ...) 
        """
        return json.loads(self.root.attr(config.BEHAVIOUR_DATA).get())

    # --------------------------------------------------------------------------
    @classmethod
    def all(cls):
        """
        Returns all the crab rigs within the scene
        
        :return: list(crab.Rig, crab.Rig, ...) 
        """
        return [
            Rig(attr.node().attr(config.LINK).inputs()[0])
            for attr in pm.ls('*.%s' % config.META_TYPE)
            if attr.get() == config.RIG_TYPE
        ]
