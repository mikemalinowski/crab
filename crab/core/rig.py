import json
import uuid
import traceback
import pymel.core as pm

from . import _factories

from .. import utils
from .. import config
from .. import create
from ..constants import log


# ------------------------------------------------------------------------------
class Signal(object):
    """
    A simple signal emmisison mechanism to allow for events within functions
    to trigger mid-call callbacks.
    """

    # --------------------------------------------------------------------------
    def __init__(self):
        self._callables = list()

    # --------------------------------------------------------------------------
    def connect(self, item):
        self._callables.append(item)

    # --------------------------------------------------------------------------
    def emit(self, *args, **kwargs):
        for item in self._callables:
            item(*args, **kwargs)


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

        # -- Delcare our signals to allow mechanisms to tie into the rig
        # -- processes. Lets start with the edit signals
        self.edit_started = Signal()  # -- Will pass the number of actions
        self.edit_complete = Signal()  # -- Will pass the name of the action

        # -- Now setup the rig build signals
        self.build_started = Signal()  # -- Will pass the number of actions
        self.build_complete = Signal()  # -- Will pass the result of the rig build

        # -- This is a more generic signal used by both the edit and the build
        # -- for when an action is being performed
        self.performing_action = Signal()  # -- Will pass the name of the action

        # -- Instance our factory
        self.factories = _factories.factory_manager()

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
        try:
            return self.meta().attr(config.RIG_ROOT_LINK_ATTR).inputs()[0]

        except AttributeError:
            return None

    # --------------------------------------------------------------------------
    def guide_org(self):
        """
        Returns the transform node which is used to store all the guide
        elements under.

        :return: pm.nt.Transform
        """
        try:
            return self.meta().attr(config.GUIDE_ROOT_LINK_ATTR).inputs()[0]

        except AttributeError:
            return None

    # --------------------------------------------------------------------------
    def control_org(self):
        """
        Returns the transform which the control rig resides under.

        :return: pm.nt.Transform
        """
        try:
            return self.meta().attr(config.CONTROL_ROOT_LINK_ATTR).inputs()[0]

        except AttributeError:
            return None

    # --------------------------------------------------------------------------
    def skeleton_org(self):
        """
        Returns the transform node which the skeletal hierarchy
        sits under.

        :return: pm.nt.Transform
        """
        try:
            return self.meta().attr(config.SKELETON_ROOT_LINK_ATTR).inputs()[0]

        except AttributeError:
            return None

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

        # -- If we got a failed plugin, or our plugin is a macro, we dont
        # -- need to do anything else
        if not result or not plugin.meta():
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
        self.factories.components.find_from_node(skeleton_node).remove()

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

        # -- Determine how many actions we will be processing so we can
        # -- emit the correct value
        action_count = len(self.factories.processes.plugins()) * 2
        action_count += 1  # Deletion of the rig itself
        action_count += len(self.guide_roots())

        # -- Emit the edit starting action
        self.edit_started.emit(action_count)

        # -- Before removing the control rig we need to give all our
        # -- processes to the oppotunity to snapshop the rig and
        # -- perform any pre-processes
        for proc in self.factories.processes.plugins():
            self.performing_action.emit('Performing Snapshot : {}'.format(proc.identifier))
            proc(self).snapshot()

        # -- Now we must remove the control rig
        self.performing_action.emit('Deleting control rig')
        pm.delete(self.control_roots())

        for proc in self.factories.processes.plugins():
            self.performing_action.emit('Running post-edit processes : {}'.format(proc.identifier))
            proc(self).post_edit()

        # -- Show all guides
        for guide_root in self.guide_roots():

            self.performing_action.emit('Linking Guides: {}'.format(guide_root))

            # -- Ensure the guide is visible
            guide_root.visibility.set(True)

            # -- Link the guide to the skeleton
            component = self.factories.components.find_from_node(guide_root)
            component.link_guide()

        self.edit_complete.emit(True)
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

        # -- Determine how many actions we will be processing so we can
        # -- emit the correct value
        action_count = len(self.factories.processes.plugins())
        action_count += len(self.guide_roots())
        action_count += len(self.assigned_behaviours())
        action_count += len(self.skeleton_roots())
        action_count += len(self.factories.processes.plugins())

        # -- Emit the edit starting action
        self.edit_started.emit(action_count)

        for proc in self.factories.processes.plugins():
            self.performing_action.emit('Running Process : {}'.format(proc.identifier))
            proc(self).pre_build()

        # -- Hide all guides
        for guide_root in self.guide_roots():
            self.performing_action.emit('Unlinking Guide : {}'.format(guide_root))

            guide_root.visibility.set(False)

            # -- UnLink the guide to the skeleton
            component = self.factories.components.find_from_node(guide_root)
            component.unlink_guide()

        # -- Finally we can start cycling components and requested
        # -- a control build
        for skeleton_component_root in self.skeleton_roots():
            self.performing_action.emit('Building Component : {}'.format(skeleton_component_root))

            # -- Attempt to find the specific control parent
            rig_parent = self.control_org()
            component_parent = skeleton_component_root.getParent()

            if component_parent.hasAttr(config.BOUND):
                for potential in component_parent.attr(config.BOUND).inputs():
                    rig_parent = potential
                    break

            # -- Get a component class instance which is targeted at the
            # -- skeletal component root
            component_plugin = self.factories.components.find_from_node(skeleton_component_root)

            print('Starting build of : %s' % component_plugin.identifier)

            try:
                # -- Build the rig, generating a control component org
                result = component_plugin.create_rig(
                    parent=component_plugin.create_control_root(
                        rig_parent,
                        component_plugin.meta(),
                    )
                )

                if not result:
                    print('%s returned False during build.' % component_plugin.identifier)
                    return False

            except:
                traceback.print_exc()
                return False

            print('\tBuild complete')

        # -- Now we need to apply any behaviours
        for behaviour_block in self.assigned_behaviours():
            self.performing_action.emit('Building Behaviour : {}'.format(behaviour_block['type']))

            if behaviour_block['type'] not in self.factories.behaviours.identifiers():
                print('Request for behaviour : {} could not be found'.format(behaviour_block['type']))
                continue

            # -- Instance the behaviour
            behaviour_plugin = self.factories.behaviours.request(
                behaviour_block['type']
            )(self)

            # -- Update the options for the behaviour plugin
            behaviour_plugin.options.update(behaviour_block['options'])

            print('Starting application of : %s' % behaviour_plugin.identifier)

            try:
                # -- Finally apply the behaviour
                behaviour_plugin.apply()

            except:
                traceback.print_exc()
                return False

            print('\tApplication complete')

        # -- Mark the rig build as clean
        self.node().isClean.set(True)

        # -- Now the rig has been fully built we can run any post build
        # -- processes
        for proc in self.factories.processes.plugins():
            self.performing_action.emit('Running Process : {}'.format(proc.identifier))

            print('Starting Process : %s' % proc.identifier)
            try:
                proc(self).post_build()

            except:
                traceback.print_exc()
                return False

            print('\tProcess complete')
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
            if self.factories.component_abstract.is_component_root(child):
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
            if self.factories.component_abstract.is_component_root(child):
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
            if self.factories.component_abstract.is_component_root(child):
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
            components.append(self.factories.components.find_from_node(skeleton_component_root))

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
