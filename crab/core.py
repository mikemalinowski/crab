"""
This holds all the major classes utilised in crab. These are:

    * Rig
    This is the main class which represents a Crab Rig and is used
    to initiate edits and builds.

    * Component
    This represents the base class for all components which can be
    built and exposes a series of helper functionality for interacting
    with components.

    * Behaviour
    This is the base class which all Behaviour plugins are required
    to inherit from

    * Factories
    This holds all the plugin factories. This is a cached item to prevent
    constant reloading of plugins.

    * Process
    This is the base class for any process plugins
"""
import re
import json
import uuid
import pymel.core as pm

from . import utils
from . import config
from . import create
from . import constants
from .vendor import factories

from .constants import log


_FACTORY_MANAGER = None


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
        >>> new_rig.add_component('Location')
        >>>
        >>> # -- Build the rig
        >>> new_rig.build()
        >>>
        >>> # -- Return the rig to an editable state
        >>> new_rig.edit()
    """

    # --------------------------------------------------------------------------
    def __init__(self, node):

        self.factories = factory_manager()

        # -- Find the rig root to allow all our functionality to
        # -- interact with it
        self._meta = None
        self._reference = node

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

        # -- Create the node marker
        rig_meta = pm.createNode('network')
        rig_meta.rename(
            config.name(
                prefix=config.META,
                description=name,
                side=config.MIDDLE,
            )
        )

        # -- Add the attributes required for a component marker
        rig_meta.addAttr(
            config.RIG_ROOT_LINK_ATTR,
            at='message'
        )
        rig_root.message.connect(rig_meta.attr(config.RIG_ROOT_LINK_ATTR))

        # -- Add this various link attributes to the different
        # -- parts which make up the component
        rig_meta.addAttr(
            config.SKELETON_ROOT_LINK_ATTR,
            at='message',
        )

        rig_meta.addAttr(
            config.CONTROL_ROOT_LINK_ATTR,
            at='message',
        )

        rig_meta.addAttr(
            config.GUIDE_ROOT_LINK_ATTR,
            at='message',
        )
        rig_meta.addAttr(
            config.BEHAVIOUR_DATA,
            dt='string',
        )
        rig_meta.attr(config.BEHAVIOUR_DATA).set('[]')

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
        control_root.message.connect(
            rig_meta.attr(config.CONTROL_ROOT_LINK_ATTR),
        )

        skeleton_root = create.generic(
            node_type='transform',
            prefix=config.ORG,
            description='Skeleton',
            side=config.MIDDLE,
            parent=rig_root,
        )
        skeleton_root.message.connect(
            rig_meta.attr(config.SKELETON_ROOT_LINK_ATTR),
        )

        guide_root = create.generic(
            node_type='transform',
            prefix=config.ORG,
            description='Guide',
            side=config.MIDDLE,
            parent=rig_root,
        )
        guide_root.message.connect(
            rig_meta.attr(config.GUIDE_ROOT_LINK_ATTR),
        )

        create.generic(
            node_type='transform',
            prefix=config.ORG,
            description='Geometry',
            side=config.MIDDLE,
            parent=rig_root,
        )

        # -- Select the rig root
        pm.select(skeleton_root)

        # -- Debug build information
        log.debug('Created new Crab Rig')

        return Rig(rig_root)

    # --------------------------------------------------------------------------
    def meta(self):
        """
        This will attempt to return the meta node for the rig. Typically you
        should not need to interact with the meta node directly, but in
        situations where its desirable to do so this is the function to be
        used.

        The meta node for the Rig is used to point at the various
        sub-level organisational nodes.

        :return: pm.nt.DependNode
        """
        # -- If we already found the meta node once we do not
        # -- want to re-search
        if self._meta:
            return self._meta

        # -- We'll need to cycle up from the given reference node
        # -- so we declare a variable to do this
        node = self._reference

        while True:

            # -- If we have hit the scene root then there is nothing
            # -- more we can do
            if not node:
                return None

            # -- Cycle all the message connections looking for the
            # -- crab meta
            for attr in node.message.outputs(plugs=True):

                # -- We're looking specifically for the crab identifer
                if attr.name(includeNode=False) != config.RIG_ROOT_LINK_ATTR:
                    continue

                # -- Store the meta node so we do not have to search
                # -- against
                self._meta = attr.node()

                return self._meta

            # -- This node has no component markers, so lets go up
            # -- to the next parent
            node = node.getParent()

    # --------------------------------------------------------------------------
    def node(self):
        """
        This returns the Rig transform node. This is expected to be the
        highest node in the rig hierarchy.

        :return: pm.nt.Transform
        """
        return self.meta().attr(config.RIG_ROOT_LINK_ATTR).inputs()[0]

    # --------------------------------------------------------------------------
    def guide_org(self):
        """
        Returns the transform node which is used to store all the guide
        elements under.

        :return: pm.nt.Transform
        """
        return self.meta().attr(config.GUIDE_ROOT_LINK_ATTR).inputs()[0]

    # --------------------------------------------------------------------------
    def control_org(self):
        """
        Returns the transform which the control rig resides under.

        :return: pm.nt.Transform
        """
        return self.meta().attr(config.CONTROL_ROOT_LINK_ATTR).inputs()[0]

    # --------------------------------------------------------------------------
    def skeleton_org(self):
        """
        Returns the transform node which the skeletal hierarchy
        sits under.

        :return: pm.nt.Transform
        """
        return self.meta().attr(config.SKELETON_ROOT_LINK_ATTR).inputs()[0]

    # --------------------------------------------------------------------------
    def find_org(self, label):
        """
        This is a generic convenience function for finding org nodes which
        are directly under the rig but not managed.

        :param label: Descriptive element to search for
        :type label: str

        :return: pm.nt.Transform
        """
        for child in self.node().getChildren(type='transform'):
            if '_%s_' % label in child.name():
                return child

        return None

    # --------------------------------------------------------------------------
    def add_component(self,
                      component_type,
                      parent=None,
                      version=None,
                      **options):
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
        parent = parent or self.skeleton_org()

        # -- Attempt to get the segment class
        if component_type not in self.factories.components.identifiers():
            log.error(
                (
                    '%s is not a recognised component_type type. Check your '
                    'plugin paths.'
                ) % component_type
            )
            return None

        # -- Instance the segment and update its options
        plugin = self.factories.components.request(
            component_type,
            version=version,
        )()
        plugin.options.update(options)

        # -- Now we request the segment to build its guide
        result = plugin.create_skeleton(parent=parent)

        if not result:
            return plugin

        with utils.contexts.RestoredSelection():

            # -- Create the guide, generating a guide root and passing
            # -- that through as the parent
            result = plugin.create_guide(
                parent=plugin.create_guide_root(
                    self.guide_org(),
                    plugin.meta(),
                )
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

            # -- Link the two
            plugin.link_guide()

            # -- Add a debug message to denote the success of the
            # -- component addition
            log.debug(
                'Successfully created component of type: %s' % component_type)

            return plugin

    # --------------------------------------------------------------------------
    def remove_component(self, skeleton_node):
        """
        Removes the component from the rig (re-parenting any child components
        under the next available parent).

        :param component_root: Skeletal Component Root

        :return: None
        """
        Component(skeleton_node).remove()

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
        for proc in self.factories.processes.plugins():
            proc(self).snapshot()

        # -- Now we must remove the control rig
        pm.delete(self.control_roots())

        for proc in self.factories.processes.plugins():
            proc(self).post_edit()

        # -- Show all guides
        for guide_root in self.guide_roots():

            # -- Ensure the guide is visible
            guide_root.visibility.set(True)

            # -- Link the guide to the skeleton
            component = Component.get(guide_root)
            component.link_guide()


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

        # -- Create an attribute on the rig node to store the shape
        # -- information on
        if not self.node().hasAttr('isClean'):
            self.node().addAttr(
                'isClean',
                at='bool',
            )
        self.node().isClean.set(False)

        # -- Ensure the rig is in an editable state
        self.edit()

        for proc in self.factories.processes.plugins():
            proc(self).pre_build()

        # -- Hide all guides
        for guide_root in self.guide_roots():

            guide_root.visibility.set(False)

            # -- UnLink the guide to the skeleton
            component = Component.get(guide_root)
            component.unlink_guide()

        # -- Finally we can start cycling components and requested
        # -- a control build
        for skeleton_component_root in self.skeleton_roots():

            # -- Attempt to find the specific control parent
            rig_parent = self.control_org()
            component_parent = skeleton_component_root.getParent()

            if component_parent.hasAttr(config.BOUND):
                for potential in component_parent.attr(config.BOUND).inputs():
                    rig_parent = potential
                    break

            # -- Get a component class instance which is targeted at the
            # -- skeletal component root
            component_plugin = Component.get(skeleton_component_root)

            # -- Build the rig, generating a control component org
            component_plugin.create_rig(
                parent=component_plugin.create_control_root(
                    rig_parent,
                    component_plugin.meta(),
                )
            )

        # -- Now we need to apply any behaviours
        for behaviour_block in self.assigned_behaviours():
            # -- Instance the behaviour
            behaviour_plugin = self.factories.behaviours.request(
                behaviour_block['type'])(self)

            # -- Update the options for the behaviour plugin
            behaviour_plugin.options.update(behaviour_block['options'])

            # -- Finally apply the behaviour
            behaviour_plugin.apply()

        # -- Mark the rig build as clean
        self.node().isClean.set(True)

        # -- Now the rig has been fully built we can run any post build
        # -- processes
        for proc in self.factories.processes.plugins():
            proc(self).post_build()

        return True

    # --------------------------------------------------------------------------
    # noinspection PyTypeChecker
    def add_behaviour(self, behaviour_type, index=None, **options):
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
        if behaviour_type not in self.factories.behaviours.identifiers():
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
        if index is None:
            current_data.append(behaviour_data)

        else:
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
        self.meta().attr(config.BEHAVIOUR_DATA).set(
            json.dumps(behaviour_data),
        )

    # --------------------------------------------------------------------------
    def guide_roots(self):
        """
        Returns all the active guide roots within the rig.

        :return: list of all the guide roots
        """
        results = list()

        for child in reversed(
                self.guide_org().getChildren(allDescendents=True)):
            if Component.is_component_root(child):
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

        for child in reversed(
                self.control_org().getChildren(allDescendents=True)):
            if Component.is_component_root(child):
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

        for child in reversed(
                self.skeleton_org().getChildren(allDescendents=True)):
            if Component.is_component_root(child):
                results.append(child)

        return results

    # --------------------------------------------------------------------------
    def assigned_behaviours(self):
        """
        Returns the list of behaviours assigned to the rig. Each behaviour
        is represented by a dictionary.

        :return: list(behaviour_dictionary, ...)
        """
        return json.loads(self.meta().attr(config.BEHAVIOUR_DATA).get())

    # --------------------------------------------------------------------------
    def components(self):
        components = list()

        for skeleton_component_root in self.skeleton_roots():
            print(skeleton_component_root, Component.get(skeleton_component_root))
            components.append(Component.get(skeleton_component_root))

        return components

    # --------------------------------------------------------------------------
    @classmethod
    def all(cls):
        """
        Returns all the crab rigs within the scene

        :return: list(crab.Rig, crab.Rig, ...)
        """
        return [
            Rig(attr.node().attr(config.RIG_ROOT_LINK_ATTR).inputs()[0])
            for attr in pm.ls('*.%s' % config.RIG_ROOT_LINK_ATTR, r=True)
        ]


# ------------------------------------------------------------------------------
# noinspection PyMethodMayBeStatic
class Component(object):
    """
    A component is a hierarchical rig element which is represented by a
    skeleton structure and is capable of building a control rig over the top.

    A component is broken up into three main functions:

        * create_skeleton
            This takes in a parent joint and builds a skeletal hierarchy

        * create_guide
            This is optional, and can be used to create a guide rig over
            the skeleton if required. This is useful if you're building a
            complex component.

        * create rig
            This is where you can build your control structure.

    You may declare component specific options within the __init__ which
    you can then read from any of the above functions.
    """

    # -- This is a unique identifier for your component
    identifier = ''

    # -- This can be bumped if you want multiple versions of your
    # -- component in a production simultaneously.
    version = 0

    # -- This can be ignored
    _NON_ALPHA_NUMERICS = re.compile('[^0-9a-zA-Z]+')

    # --------------------------------------------------------------------------
    def create_skeleton(self, parent):
        """
        This is where you should build your skeleton. `parent` is the node
        your build skeleton should reside under and it will never be None.

        :param parent: Node to parent your skeleton under
        :type parent: pm.nt.DagNode

        :return: True if successful
        """
        return True

    # --------------------------------------------------------------------------
    def create_guide(self, parent):
        """
        This function allows you to build a guide element.

        :param parent: Parent node to build the rig under

        :return:
        """
        return True

    # --------------------------------------------------------------------------
    def link_guide(self):
        """
        This should perform the required steps to have the skeletal
        structure driven by the guide (if the guide is implemented). This
        will then be triggered by Rig.edit process.

        :return: None
        """
        return True

    # --------------------------------------------------------------------------
    def unlink_guide(self):
        """
        This should perform the operation to unlink the guide from the
        skeleton, leaving the skeleton completely free of any ties
        between it and the guide.

        This is run as part of the Rig.build process.

        :return: None
        """
        return True

    # --------------------------------------------------------------------------
    def create_rig(self, parent):
        """
        This should create your animation rig for this segment. The parent
        will be a pre-constructed crabSegment transform node and the guide
        will be an instance of this class centered on the guide.

        :param parent: Parent node to build the rig under

        :return:
        """
        return True

    # --------------------------------------------------------------------------
    # noinspection PyMethodMayBeStatic
    def skeleton_tools(self):
        """
        This may be used to return an optional QWidget to expose
        guide options to a user.

        :return:
        """
        pass

    # --------------------------------------------------------------------------
    def animation_tools(self):
        """
        This may be used to return an optional QWidget to expose
        animation tools to the user.

        :return:
        """
        pass

    # --------------------------------------------------------------------------
    # -- You do not need to re-implement anything below this line.

    # --------------------------------------------------------------------------
    def __init__(self, node=None):

        # -- All the options should be defined within this
        # -- dictionary
        self.options = utils.types.AttributeDict()
        self.options.description = 'unknown'
        self.options.side = config.MIDDLE

        # -- Store the node reference we are given, as this is what
        # -- we will use to find our meta
        self._reference = node
        self._meta = None

    # --------------------------------------------------------------------------
    def mark_as_skeletal_root(self, node):
        """
        This is used to define the root skeletal joint of a component. Whenever
        you implement a new component plugin your top level skeleton joint
        should be passed to this function.

        This method will setup the required component meta node which stores
        the relational information between the guide, rig and skeleton as well
        as acting as a tagging library.

        :param node: The root skeleton joint of your component
        :type node: pm.nt.Joint

        :return: None
        """
        # -- The skeleton is the key starting point, so we only ever
        # -- create new meta nodes here
        self._reference = node
        meta_node = self.create_meta()
        node.message.connect(meta_node.attr(config.SKELETON_ROOT_LINK_ATTR))

    # --------------------------------------------------------------------------
    def mark_as_control_root(self, control_root, meta_node):
        """
        You should not need to ever call this function as it is called
        as part of the Rig.build functionality for you.

        This will make a connection between the root control object and
        the components meta node allowing the relationship to be traced
        between them.

        :param control_root: The components control org node
        :type control_root: pm.nt.Transform

        :param meta_node: The metanode to tie the control object to
        :type meta_node: pm.nt.DependNode

        :return: None
        """
        control_root.message.connect(
            meta_node.attr(
                config.CONTROL_ROOT_LINK_ATTR,
            ),
        )

    # --------------------------------------------------------------------------
    def mark_as_guide_root(self, guide_root, meta_node):
        """
        You should not need to ever call this function as it is called
        as part of the Rig.add_component functionality for you.

        This will make a connection between the root guide object and
        the components meta node allowing the relationship to be traced
        between them.

        :param guide_root: The components guide org node
        :type guide_root: pm.nt.Transform

        :param meta_node: The meta node to tie the control object to
        :type meta_node: pm.nt.DependNode

        :return: None
        """
        guide_root.message.connect(
            meta_node.attr(
                config.GUIDE_ROOT_LINK_ATTR,
            ),
        )

    # --------------------------------------------------------------------------
    def skeletal_root(self):
        """
        This will return the transform which the skeletal structure
        sits under.

        :return: pm.nt.Transform
        """
        meta_node = self.meta()

        if not meta_node:
            return None

        try:
            return meta_node.attr(config.SKELETON_ROOT_LINK_ATTR).inputs()[0]

        except IndexError:
            return None

    # --------------------------------------------------------------------------
    # noinspection PyBroadException
    def control_root(self):
        """
        This will return the transform which the control structure
        sits under.

        :return: pm.nt.Transform
        """
        meta_node = self.meta()

        if not meta_node:
            return None

        try:
            meta_node.attr(config.CONTROL_ROOT_LINK_ATTR).inputs()[0]

        except IndexError:
            return None

    # --------------------------------------------------------------------------
    # noinspection PyBroadException
    def guide_root(self):
        """
        This will return the transform which the guide structure
        sits under.

        :return: pm.nt.Transform
        """
        meta_node = self.meta()

        if not meta_node:
            return None

        try:
            meta_node.attr(config.GUIDE_ROOT_LINK_ATTR).inputs()[0]

        except IndexError:
            return None

    # --------------------------------------------------------------------------
    def meta(self):
        """
        This will return the meta node representing this component. Once found
        the metanode is cached to prevent further look-ups from being
        required.

        :return: pm.nt.DependNode
        """

        # -- If the meta node has already been found, use it rather than
        # -- repeating the look up.
        if self._meta:
            return self._meta

        # -- We need to cycle upward, so create a tracking variable
        node = self._reference

        while True:

            # -- If we have hit the scene root then there is nothing
            # -- more for us to do
            if not node:
                return None

            # -- Cycle all the messaging attributes looking
            # -- for an attribute of the type we're expecting
            for attribute in node.message.outputs(plugs=True):

                # -- We're looking specifically for the crab identifer
                if config.CONNECTION_PREFIX not in attribute.name(
                        includeNode=False):
                    continue

                # -- Cache the node so we do not need to repeat the
                # -- search again
                self._meta = attribute.node()

                return self._meta

            # -- This node has no component markers, so lets go up
            # -- to the next parent
            node = node.getParent()

    # --------------------------------------------------------------------------
    def tag(self, target, label):
        """
        Shortcut for tagging to the meta root

        :param target: Target object to tag
        :param label: Label to tag with

        :return: None
        """
        # -- Now we need to check if we need to add a new message
        # -- attribute or use a pre-existing one
        attribute_name = 'crabLabel%s' % label
        meta_node = self.meta()

        if not meta_node.hasAttr(attribute_name):
            meta_node.addAttr(
                attribute_name,
                at="message",
                multi=True,
            )

        # -- Get the attribute
        attr = meta_node.attr(attribute_name)
        sub_attr = meta_node.attr('%s[%s]' % (attribute_name, 0))

        for idx in range(attr.numElements() + 1):

            # -- Get the sub attribute plug
            sub_attr = meta_node.attr('%s[%s]' % (attribute_name, idx))

            # -- If it is empty, we can re-use it
            if not sub_attr.inputs():
                break

        target.message.connect(sub_attr)

    # --------------------------------------------------------------------------
    def find(self, label):
        """
        Convenience function for performing a meta find against
        the component.

        :param label:
        :return:
        """
        meta_node = self.meta()

        # -- Check that the expected attribute exists
        attribute_name = 'crabLabel%s' % label
        if meta_node.hasAttr(attribute_name):
            return meta_node.attr(attribute_name).inputs()

        return []

    # --------------------------------------------------------------------------
    def find_first(self, label):
        """
        Convenience function for performing a meta find against
        the component.

        :param label:
        :return:
        """
        results = self.find(label)

        if results:
            return results[0]

        return None

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences,PyMethodMayBeStatic
    def bind(self, skeletal_joint, control, constrain=True, scale=True, **kwargs):
        """
        Creates a constraint binding between the skeletal joint and the control
        such that the skeletal joint will be driven by the control and this
        control will act as the parent for any child components below this
        skeletal joint.
        """
        if constrain:
            pm.parentConstraint(
                control,
                skeletal_joint,
                **kwargs
            )

            pm.scaleConstraint(
                control,
                skeletal_joint,
                **kwargs
            )

        # -- Add a binding link between the skeletal joint and
        # -- the control
        if not skeletal_joint.hasAttr(config.BOUND):
            skeletal_joint.addAttr(
                config.BOUND,
                at='message',
            )
        control.message.connect(skeletal_joint.attr(config.BOUND))

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def create_control_root(self, parent, meta_node):
        """
        Convenience function for creating a root for your component. You should
        call this from within your create_rig function call.

        :param parent: Parent for the base node
        :type parent: pm.nt.DagNode

        :param meta_node: The meta node which should be linked to this control
            rig to allow for tracability.
        :type meta_node: pm.nt.DependNode

        :return: newly created node (pm.nt.DagNode)
        """
        # -- Create the node
        node = create.generic(
            node_type='transform',
            prefix=config.RIG_COMPONENT,
            description=self._NON_ALPHA_NUMERICS.sub('', self.options.description or self.identifier),
            side=self.options.side,
            parent=parent,
            match_to=parent,
        )

        self.mark_as_control_root(
            node,
            meta_node,
        )

        return node

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def create_guide_root(self, parent, meta_node):
        """
        Convenience function for creating a root for your component. You should
        call this from within your create_guide function call.

        :param parent: Parent for the base node
        :type parent: pm.nt.DagNode

        :param meta_node: The meta node which this guide should be linked
            to.
        :type meta_node: pm.nt.DependNode

        :return: newly created node (pm.nt.DagNode)
        """
        # -- Create the node
        node = create.generic(
            node_type='transform',
            prefix=config.GUIDE_COMPONENT,
            description=self._NON_ALPHA_NUMERICS.sub('', self.options.description or self.identifier),
            side=self.options.side,
            parent=parent,
            match_to=parent,
        )

        self.mark_as_guide_root(
            node,
            meta_node,
        )
        return node

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def create_meta(self):
        """
        Creates a new meta node and connects it to the given dag node. The
        metanode is stamped with a type string and any keyword arguments
        which are passed down are used to set values on those attributes.

        :return: pm.nt.DependNode
        """
        # -- Create the node marker
        meta_node = pm.createNode('network')
        meta_node.rename(
            config.name(
                prefix=config.META,
                description=self._NON_ALPHA_NUMERICS.sub('', self.options.description or self.identifier),
                side=self.options.side,
            )
        )

        # -- Add the attributes required for a component marker
        meta_node.addAttr(
            config.COMPONENT_MARKER,
            dt='string'
        )

        # -- Store the type of the component
        meta_node.addAttr(
            config.META_IDENTIFIER,
            dt='string',
        )
        meta_node.attr(config.META_IDENTIFIER).set(self.identifier)

        meta_node.addAttr(
            config.META_VERSION,
            at='float',
        )
        meta_node.attr(config.META_VERSION).set(self.version)

        meta_node.addAttr(
            config.META_OPTIONS,
            dt='string',
        )
        meta_node.attr(config.META_OPTIONS).set(json.dumps(self.options))

        # -- Add this various link attributes to the different
        # -- parts which make up the component
        meta_node.addAttr(
            config.SKELETON_ROOT_LINK_ATTR,
            at='message',
        )

        meta_node.addAttr(
            config.CONTROL_ROOT_LINK_ATTR,
            at='message',
        )

        meta_node.addAttr(
            config.GUIDE_ROOT_LINK_ATTR,
            at='message',
        )

        return meta_node

    # --------------------------------------------------------------------------
    @classmethod
    def is_component_root(cls, node):
        """
        Class method used to check if a given node is a component root of
        any kind. If it is, the meta node will be returned.

        :param node: The node to check against.
        :typenode: pm.nt.DependNode

        :return: pm.nt.DependNode
        """
        for attr in node.message.outputs(plugs=True):

            # -- We're looking specifically for the crab identifer
            if config.CONNECTION_PREFIX not in attr.name(includeNode=False):
                continue

            return attr.node()
        return None

    # --------------------------------------------------------------------------
    @classmethod
    def get(cls, node):
        """
        Convenience function for intantiating a Component class which is
        representative of the given node.

        :param node: Node to generate a component instance for
        :type node: pm.nt.Transform

        :return: crab.Component instance
        """
        while True:

            meta = cls.is_component_root(node)

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

    # --------------------------------------------------------------------------
    def parent_component(self):
        return Component(self.skeletal_root().getParent())

    # --------------------------------------------------------------------------
    def child_components(self, recursive=False):
        """
        This will return all the child components of this component

        :param recursive: If true, all childrens children will also be
            returned
        :type recursive: bool

        :return: list
        """
        child_components = list()
        processed_roots = list()

        for child in self.skeletal_root().getChildren(ad=True):
            childs_component = Component(child)

            if childs_component.skeletal_root() in processed_roots:
                continue

            # -- Are we part of the same component?
            if childs_component.skeletal_root() == self.skeletal_root():
                continue

            # -- If we're not recursive, we only want to look for children
            # -- which are direct descendents of this one
            if not recursive and childs_component.parent_component().skeletal_root() != self.skeletal_root():
                continue

            child_components.append(childs_component)
            processed_roots.append(childs_component.skeletal_root())

        return child_components

    # --------------------------------------------------------------------------
    def remove(self):
        """
        This will remove this crab component
        :return:
        """
        # -- Start by re-parenting any child components to the parent of this
        # -- component
        parent = self.skeletal_root().getParent()

        for child_component in self.child_components(recursive=False):
            child_component.skeletal_root().setParent(parent)

        # -- Now we can delete the nodes relating to this component
        try:
            pm.delete(self.meta().attr(config.GUIDE_ROOT_LINK_ATTR).inputs())

        except: pass

        try:
            pm.delete(self.skeletal_root())

        except: pass

        try:
            pm.delete(self.meta())

        except: pass


# ------------------------------------------------------------------------------
class Behaviour(object):
    """
    A behaviour is a rigging behaviour which may or may not have a dag element
    to it and may be dependent on other elements of the control rig. Whilst
    components are atomic behaviours can cross the boundaries of any component.
    """

    # -- Unique identifier for the behaviur
    identifier = ''
    version = 0

    # --------------------------------------------------------------------------
    def __init__(self, rig=None):
        # -- All the options should be defined within this
        # -- dictionary
        self.options = utils.types.AttributeDict()
        self.options.description = 'unknown'
        self.options.side = config.MIDDLE

        # -- By default assume we do not have a root yet
        self.rig = rig

    # --------------------------------------------------------------------------
    def apply(self):
        """
        You should implement this function to build your behaviour. You may
        utilise the options dictionary to read information you need.

        :return: True if the apply is successful
        """
        return True


# ------------------------------------------------------------------------------
# noinspection PyMethodMayBeStatic
class Process(object):
    """
    A process is a plugin which is executed during an edit call as well as
    a build call. This plugin type has three stages:

        * snapshot
            This is done before the control rig is destroyed and its your
            oppotunity to read any information from the rig.
            Note: You must store the data you have read, as the same process
                instance will not be used during the build.

        * pre
            This is called after the control is destroyed, leaving the skeleton
            bare. This is typically a good time to do any skeleton modifications
            as nothing will be locking or driving the joints.

        * post
            This is called after all the components and behaviours are built,
            allowing  you to perform any actions against the rig as a whole.
    """
    identifier = 'unknown'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, rig):
        self.rig = rig

    # --------------------------------------------------------------------------
    def snapshot(self):
        """
        This is done before the control rig is destroyed and its your
        oppotunity to read any information from the rig.

        Note: You must store the data you have read, as the same process
            instance will not be used during the build.

        :return: None
        """
        pass

    # --------------------------------------------------------------------------
    def post_edit(self):
        """
        This is called after the control is destroyed, leaving the skeleton
        bare. This is typically a good time to do any skeleton modifications
        as nothing will be locking or driving the joints.

        :return:
        """
        pass

    # --------------------------------------------------------------------------
    def pre_build(self):
        """
        This is called after all the components and behaviours are built,
        allowing  you to perform any actions against the rig as a whole.

        :return:
        """
        pass

    # --------------------------------------------------------------------------
    def post_build(self):
        """
        This is called after all the components and behaviours are built,
        allowing  you to perform any actions against the rig as a whole.

        :return:
        """
        pass


# ------------------------------------------------------------------------------
class Factories(object):
    """
    This holds all three factories which a crab rig workflow relies upon
    """

    # --------------------------------------------------------------------------
    def __init__(self):

        # -- This is a library of all the components available
        # -- to the rig
        self.components = factories.Factory(
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
