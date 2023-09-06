import json
import uuid
import time
import operator
import traceback
import maya.cmds as mc
import pymel.core as pm

from . import _factories

from .. import utils
from .. import config
from .. import create
from ..constants import log


# --------------------------------------------------------------------------------------
class Signal(object):
    """
    A simple signal emmisison mechanism to allow for events within functions
    to trigger mid-call callbacks.
    """

    # ----------------------------------------------------------------------------------
    def __init__(self):
        self._callables = list()

    # ----------------------------------------------------------------------------------
    def connect(self, item):
        self._callables.append(item)

    # ----------------------------------------------------------------------------------
    def emit(self, *args, **kwargs):
        for item in self._callables:
            item(*args, **kwargs)


# --------------------------------------------------------------------------------------
class Rig(object):
    """
    The rig class represents the main interfacing class for a crab rig. From
    here you can apply new components or behaviours as well as gain access
    to applied components.

    This example shows how to build a new rig

    ..code-block:: python

        >>> import crab
        >>>
        >>> new_rig = crab.Rig.create(name="MyRig")

    You can then use this variable to add new components

    ..code-block:: python

        >>> import crab
        >>>
        >>> # -- Build a new rig
        >>> new_rig = crab.Rig.create(name="MyRig")
        >>>
        >>> # -- Add a component to the rig
        >>> new_rig.add_component("Location")
        >>>
        >>> # -- Build the rig
        >>> new_rig.build()
        >>>
        >>> # -- Return the rig to an editable state
        >>> new_rig.edit()
    """

    # ----------------------------------------------------------------------------------
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

    # ----------------------------------------------------------------------------------
    def built_successfully(self):
        """
        Checks if the rig was successfully built last time the build
        was attempted
        """
        if self.node().hasAttr("built_successfully"):
            return self.node().built_successfully.get()

        return True

    # ----------------------------------------------------------------------------------
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
            node_type="transform",
            prefix=config.RIG_ROOT,
            description=name or "CrabRig",
            side=config.MIDDLE,
        )

        # -- Store an attribute to state whether the rig has been successfully built.
        # -- this allow mechanisms to check whether they should run or whether there
        # -- may be issues
        rig_root.addAttr(
            "built_successfully",
            at="bool",
            dv=True,
        )

        control_root = create.generic(
            node_type="transform",
            prefix=config.ORG,
            description="ControlRig",
            side=config.MIDDLE,
            parent=rig_root,
        )

        skeleton_root = create.generic(
            node_type="transform",
            prefix=config.ORG,
            description="Skeleton",
            side=config.MIDDLE,
            parent=rig_root,
        )

        guide_root = create.generic(
            node_type="transform",
            prefix=config.ORG,
            description="Guide",
            side=config.MIDDLE,
            parent=rig_root,
        )

        cls.create_meta(
            rig_root=rig_root,
            skeleton_root=skeleton_root,
            control_root=control_root,
            guide_root=guide_root,
        )

        create.generic(
            node_type="transform",
            prefix=config.ORG,
            description="Geometry",
            side=config.MIDDLE,
            parent=rig_root,
        )

        # -- Select the rig root
        pm.select(skeleton_root)

        # -- Debug build information
        log.debug("Created new Crab Rig")

        return Rig(rig_root)

    # ----------------------------------------------------------------------------------
    @classmethod
    def create_meta(
        cls,
        rig_root,
        skeleton_root=None,
        control_root=None,
        guide_root=None,
    ):
        if not skeleton_root:
            skeleton_root = utils.hierarchy.find_below(rig_root, "Skeleton")

        if not control_root:
            control_root = utils.hierarchy.find_below(rig_root, "ControlRig")

        if not guide_root:
            guide_root = utils.hierarchy.find_below(rig_root, "Guide")

        # -- Create the node marker
        rig_meta = pm.createNode("network")
        rig_meta.rename(
            config.name(
                prefix=config.META,
                description=config.get_description(rig_root),
                side=config.MIDDLE,
            )
        )

        # -- Add the attributes required for a component marker
        rig_meta.addAttr(config.RIG_ROOT_LINK_ATTR, at="message")
        rig_root.message.connect(rig_meta.attr(config.RIG_ROOT_LINK_ATTR))

        # -- Add this various link attributes to the different
        # -- parts which make up the component
        rig_meta.addAttr(
            config.SKELETON_ROOT_LINK_ATTR,
            at="message",
        )

        rig_meta.addAttr(
            config.CONTROL_ROOT_LINK_ATTR,
            at="message",
        )

        rig_meta.addAttr(
            config.GUIDE_ROOT_LINK_ATTR,
            at="message",
        )
        rig_meta.addAttr(
            config.BEHAVIOUR_DATA,
            dt="string",
        )
        rig_meta.attr(config.BEHAVIOUR_DATA).set("[]")

        # -- Create our sub-category nodes. These allow us to create
        # -- clear distinctions between our control rig, skeleton and
        # -- guides.
        control_root.message.connect(
            rig_meta.attr(config.CONTROL_ROOT_LINK_ATTR),
        )

        skeleton_root.message.connect(
            rig_meta.attr(config.SKELETON_ROOT_LINK_ATTR),
        )

        guide_root.message.connect(
            rig_meta.attr(config.GUIDE_ROOT_LINK_ATTR),
        )

        return rig_meta

    # ----------------------------------------------------------------------------------
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

        # -- We"ll need to cycle up from the given reference node
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
                # -- We"re looking specifically for the crab identifer
                if attr.name(includeNode=False) != config.RIG_ROOT_LINK_ATTR:
                    continue

                # -- Store the meta node so we do not have to search
                # -- against
                self._meta = attr.node()

                return self._meta

            # -- This node has no component markers, so lets go up
            # -- to the next parent
            node = node.getParent()

    # ----------------------------------------------------------------------------------
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

    # ----------------------------------------------------------------------------------
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

    # ----------------------------------------------------------------------------------
    def control_org(self):
        """
        Returns the transform which the control rig resides under.

        :return: pm.nt.Transform
        """
        try:
            return self.meta().attr(config.CONTROL_ROOT_LINK_ATTR).inputs()[0]

        except AttributeError:
            return None

    # ----------------------------------------------------------------------------------
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

    # ----------------------------------------------------------------------------------
    def find_org(self, label):
        """
        This is a generic convenience function for finding org nodes which
        are directly under the rig but not managed.

        :param label: Descriptive element to search for
        :type label: str

        :return: pm.nt.Transform
        """
        for child in self.node().getChildren(type="transform"):
            if "_%s_" % label in child.name():
                return child

        return None

    # ----------------------------------------------------------------------------------
    def available_components(self):
        """
        This will return a list of component classes (not instanced)

        :return: List(crab.Component, crab.Component)
        """
        return self.factories.components.plugins()

    # ----------------------------------------------------------------------------------
    def available_behaviours(self):
        """
        This will return a list of component classes (not instanced)

        :return: List(crab.Component, crab.Component)
        """
        return self.factories.behaviours.plugins()

    # ----------------------------------------------------------------------------------
    def behaviours(self, unique_id=None):
        """
        This will return a list of component classes (not instanced)

        :return: List(crab.Component, crab.Component)
        """
        all_behaviour_data = json.loads(self.meta().attr(config.BEHAVIOUR_DATA).get())

        behaviours = list()

        for behaviour_data in all_behaviour_data:
            # -- If we do not recognise the behaviour, log it and continu
            if (
                behaviour_data.get("type", "")
                not in self.factories.behaviours.identifiers()
            ):
                print("{} is not a recognised behaviour".format(behaviour_data["type"]))
                continue

            # -- Instance the behaviour
            behaviour_class = self.factories.behaviours.request(behaviour_data["type"])
            behaviour = behaviour_class(
                rig=self, instance_id=behaviour_data.get("id", None)
            )

            # -- Update the behaviour with all its option information
            behaviour.options.update(behaviour_data.get("options", {}))

            # -- If we"re given a specific behaviour id to look for, and it matches
            # -- then lets return it
            if unique_id and behaviour_data.get("id") == unique_id:
                return behaviour

            # -- Add the behaviour to the list
            behaviours.append(behaviour)

        return behaviours

    # ----------------------------------------------------------------------------------
    def serialise_behaviour(self, behaviour):
        """
        This will serialise any information from a behaviour that is assigned
        to a rig
        """
        pass

    # ----------------------------------------------------------------------------------
    def validate_behaviours(self, remove_invalid=False):
        """
        This will run behaviour validation - checking for any behaviours
        that are not valid or cannot be built

        :param remove_invalid: If True then any that return an invalid result
            will be removed from the build recipie
        :type remove_invalid: bool

        :return: False if ANY behaviours are invalid
        """
        overall_result = True
        # -- We need to get a list of all the contents we expect to have
        # -- whenever the rig is built
        contents = list()

        for component in self.components():
            meta_node = component.meta()

            # -- If this node has no contents skip it
            if not meta_node.hasAttr(config.META_CONTENTS):
                continue

            # -- Scoop up the list
            contents.extend(
                eval(
                    meta_node.attr(config.META_CONTENTS).get(),
                ),
            )

        # -- Now cycle teh list of behaviours and check each one is capable
        # -- of building correctly
        for behaviour in self.behaviours():
            # -- We take the result only if our running result is True. This
            # -- is because having any ONE false result means the end result
            # -- needs to be false.
            # -- We do want to run all the behaviour validators though - so that
            # -- the user is aware of all issues
            result = behaviour.can_build(contents)

            if not result:
                overall_result = False

                if remove_invalid:
                    behaviour.remove()

        return overall_result

    # ----------------------------------------------------------------------------------
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
            will then be passed directly to the component"s option dictionary.

        :return: component plugin instance
        """
        # -- Get the skeleton root
        parent = parent or self.skeleton_org()

        # -- Attempt to get the segment class
        if component_type not in self.factories.components.identifiers():
            log.error(
                (
                    "%s is not a recognised component_type type. Check your "
                    "plugin paths."
                )
                % component_type
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
                    "The %s segment failed to create its guide successfully"
                    % (component_type,),
                )
                return None

            # -- Link the two
            plugin.link_guide()

            # -- Add a debug message to denote the success of the
            # -- component addition
            log.debug("Successfully created component of type: %s" % component_type)

            return plugin

    # ----------------------------------------------------------------------------------
    def recreate_component(self, component):
        # -- Store all the transforms of the joints
        transforms = dict()
        a_poses = dict()
        t_poses = dict()
        leaf_components = dict()

        component_parent = component.skeletal_root().getParent()
        component_joints = component.skeletal_joints()

        for joint in component_joints:
            transforms[joint.name()] = joint.getMatrix()

            if joint.hasAttr("APose"):
                a_poses[joint.name()] = joint.APose.get()

            if joint.hasAttr("TPose"):
                t_poses[joint.name()] = joint.TPose.get()

        # -- We now need to store the skeletal hierarchy
        for joint in component.skeletal_root().getChildren(ad=True, type="joint"):
            # -- If this joint is a component joint we ignore it
            if joint in component_joints:
                continue

            # -- If this joint is not a component joint, but its not a direct child
            # -- of a component joint we also ignore it
            if joint.getParent() not in component_joints:
                continue

            # -- To reach here we have a joint which is not part of this component but
            # -- is an immediate child. Therefore we need to store it and unparent it
            leaf_components[joint] = joint.getParent().name()
            joint.setParent(None)

        # -- Remove the component
        component.remove()

        # -- Add the component
        new_component = self.add_component(
            component.identifier, parent=component_parent, **component.options
        )

        # -- We now need to try and restore as much information as possible
        for joint in new_component.skeletal_joints():
            name = joint.name()

            if name in transforms:
                joint.setMatrix(transforms[name])

            if name in a_poses:
                if not joint.hasAttr("APose"):
                    joint.addAttr("APose", at="matrix")
                joint.APose.set(a_poses[name])

            if name in t_poses:
                if not joint.hasAttr("TPose"):
                    joint.addAttr("TPose", at="matrix")
                joint.TPose.set(t_poses[name])

        # -- Now we need to set any parenting
        for leaf_component, parent_name in leaf_components.items():
            if pm.objExists(parent_name):
                leaf_component.setParent(pm.PyNode(parent_name))

    # ----------------------------------------------------------------------------------
    def edit(self):
        """
        Puts the rig into an editable state - removing the control rig
        and exposing the skeleton as well as triggering any guides.

        During this process all the stored process plugins will have their
        snapshot and pre functions called.

        :return: True if the rig enters edit mode successfully
        """
        # -- If we"re already in an editable state we do not need
        # -- to do anything more
        if self.is_editable():
            log.info("Rig is already editable.")
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
            self.performing_action.emit(
                "Performing Snapshot : {}".format(proc.identifier)
            )
            proc(self).snapshot()

        # -- Now we must remove the control rig
        self.performing_action.emit("Deleting control rig")
        pm.delete(self.control_roots())

        for proc in self.factories.processes.plugins():
            self.performing_action.emit(
                "Running post-edit processes : {}".format(proc.identifier)
            )
            proc(self).post_edit()

        # -- Show all guides
        for skeleton_component_root in self.skeleton_roots():
            print(skeleton_component_root)
            component_plugin = self.factories.components.find_from_node(
                skeleton_component_root
            )
            guide_root = component_plugin.guide_root()

            if not guide_root:
                continue

            self.performing_action.emit("Linking Guides: {}".format(guide_root))

            # -- Ensure the guide is visible
            guide_root.visibility.set(True)

            # -- Link the guide to the skeleton
            component = self.factories.components.find_from_node(guide_root)
            component.link_guide()

        self.edit_complete.emit(True)
        return True

    # ----------------------------------------------------------------------------------
    def build(self):
        """
        This builds the rig. It first places the rig into an editable
        state and removes any guide infrastructure. It will then proceed
        to build the control rig before executing the post functions of
        all the stored processes.

        :return: True if the build was successful
        """
        # -- Log the action of starting a rig build
        log.info("Commencing rig build.")

        # -- Track the start time
        start_time = time.time()

        # -- Create an attribute on the rig node to store the shape
        # -- information on
        if not self.node().hasAttr("isClean"):
            self.node().addAttr(
                "isClean",
                at="bool",
            )
        self.node().isClean.set(False)

        # -- Ensure the rig is in an editable state
        self.edit()

        # -- Check if our rig node has the built successfully attribute. This is crucual
        # -- for processes to know what state the rig is in
        if not self.node().hasAttr("built_successfully"):
            self.node().addAttr(
                "built_successfully",
                at="bool",
                dv=True,
            )

        # -- Determine how many actions we will be processing so we can

        # -- emit the correct value
        action_count = len(self.factories.processes.plugins())
        action_count += len(self.guide_roots())
        action_count += len(self.behaviours())
        action_count += len(self.skeleton_roots())
        action_count += len(self.factories.processes.plugins())

        # -- From this point onward we may start making edits to the rig
        # -- so we set teh built_successfully flag to false until we"re
        # -- complete
        self.node().built_successfully.set(False)

        # -- Emit the edit starting action
        self.edit_started.emit(action_count)

        # -- Run any validation before we start. If any validation fails then
        # -- we do not continue
        for proc in self.factories.processes.plugins():
            self.performing_action.emit("Running Process : {}".format(proc.identifier))
            result = proc(self).validate()

            if not result:
                print(
                    "%s failed during validation. Please see script editor for details"
                    % proc.identifier
                )
                return False

        for proc in self.factories.processes.plugins():
            self.performing_action.emit("Running Process : {}".format(proc.identifier))
            proc(self).pre_build()

        # -- Hide all guides
        for guide_root in self.guide_roots():
            self.performing_action.emit("Unlinking Guide : {}".format(guide_root))

            guide_root.visibility.set(False)

            # -- UnLink the guide to the skeleton
            component = self.factories.components.find_from_node(guide_root)
            component.unlink_guide()

        # -- Finally we can start cycling components and requested
        # -- a control build
        for skeleton_component_root in self.skeleton_roots():
            self.performing_action.emit(
                "Building Component : {}".format(skeleton_component_root)
            )

            # -- Attempt to find the specific control parent
            rig_parent = self.control_org()
            component_parent = skeleton_component_root.getParent()

            if component_parent.hasAttr(config.BOUND):
                for potential in component_parent.attr(config.BOUND).inputs():
                    rig_parent = potential
                    break

            # -- Get a component class instance which is targeted at the
            # -- skeletal component root
            component_plugin = self.factories.components.find_from_node(
                skeleton_component_root
            )

            print(
                "Starting build of : %s (%s)"
                % (component_plugin.identifier, skeleton_component_root)
            )

            try:
                meta_node = component_plugin.meta()

                # -- Ensure we have a contents node
                if not meta_node.hasAttr(config.META_CONTENTS):
                    meta_node.addAttr(
                        config.META_CONTENTS,
                        dt="string",
                    )
                    meta_node.attr(config.META_CONTENTS).set("[]")

                # -- Snapshot the scene list
                scene_list = set(mc.ls(dag=True))

                # -- Build the rig, generating a control component org
                result = component_plugin.create_rig(
                    parent=component_plugin.create_control_root(
                        rig_parent,
                        component_plugin.meta(),
                    )
                )

                # -- Capture the delta
                new_scene_list = set(mc.ls(dag=True))
                meta_node.attr(config.META_CONTENTS).set(
                    str(list(new_scene_list - scene_list))
                )

                if not result:
                    print(
                        "%s returned False during build." % component_plugin.identifier
                    )
                    return False

            except:
                traceback.print_exc()
                return False

            print("\tBuild complete")

        # -- Now we need to apply any behaviours
        for behaviour in self.behaviours():
            self.performing_action.emit(
                "Building Behaviour : {}".format(behaviour.identifier)
            )

            print("Starting application of : %s" % behaviour.identifier)

            try:
                # -- Finally apply the behaviour
                behaviour.apply()

            except:
                traceback.print_exc()
                return False

            print("\tApplication complete")

        # -- Mark the rig build as clean
        self.node().isClean.set(True)

        # -- Now the rig has been fully built we can run any post build
        # -- processes
        for proc in sorted(
            self.factories.processes.plugins(), key=operator.attrgetter("order")
        ):
            self.performing_action.emit("Running Process : {}".format(proc.identifier))

            print("Starting Process : %s" % proc.identifier)
            try:
                proc(self).post_build()

            except:
                traceback.print_exc()
                return False

            print("\tProcess complete")

        # -- To reach this point our rig build has been succesful, so we should
        # -- mark it as such
        self.node().built_successfully.set(True)

        # -- Calculate the time it took
        print(
            "Rig took {} to build".format(
                round(time.time() - start_time, 4),
            )
        )

        return True

    # ----------------------------------------------------------------------------------
    def is_editable(self):
        """
        Checks if the rig is considered to be in an editable or animatable
        state.

        :return: True if the rig is editable
        """
        if self.control_roots():
            return False

        return True

    # ----------------------------------------------------------------------------------
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
        # -- Ensure the behaviour is accessible
        if behaviour_type not in self.factories.behaviours.identifiers():
            log.error("%s could not be found." % behaviour_type)
            return False

        # -- Get the current behaviour data
        current_data = json.loads(self.meta().attr(config.BEHAVIOUR_DATA).get())

        # -- Create a data block to add it to
        unique_id = str(uuid.uuid4())
        behaviour_data = dict(
            type=behaviour_type,
            options=options,
            id=unique_id,
        )

        # -- Assign our data into the current data
        if index is None:
            current_data.append(behaviour_data)

        else:
            current_data.insert(index, behaviour_data)

        # -- Now write the data into the attribute
        self.meta().attr(config.BEHAVIOUR_DATA).set(
            json.dumps(current_data),
        )

        return self.behaviours(unique_id=unique_id)

    # ----------------------------------------------------------------------------------
    def guide_roots(self):
        """
        Returns all the active guide roots within the rig.

        :return: list of all the guide roots
        """
        results = list()

        for child in reversed(self.guide_org().getChildren(allDescendents=True)):
            if self.factories.component_abstract.is_component_root(child):
                results.append(child)

        return results

    # ----------------------------------------------------------------------------------
    def control_roots(self):
        """
        Returns all the component roots within the control hierarchy
        of the rig

        :return: list (pm.nt.DagNode, ...)
        """
        results = list()

        for child in reversed(self.control_org().getChildren(allDescendents=True)):
            if self.factories.component_abstract.is_component_root(child):
                results.append(child)

        return results

    # ----------------------------------------------------------------------------------
    def skeleton_roots(self):
        """
        Returns all the component roots within the skeletal hierarchy
        of the rig

        :return: list(pm.nt.DagNode, ...)
        """
        results = list()

        for child in reversed(self.skeleton_org().getChildren(allDescendents=True)):
            if self.factories.component_abstract.is_component_root(child):
                results.append(child)

        return results

    # ----------------------------------------------------------------------------------
    def components(self):
        components = list()

        for skeleton_component_root in self.skeleton_roots():
            components.append(
                self.factories.components.find_from_node(skeleton_component_root)
            )

        return components

    # ----------------------------------------------------------------------------------
    @classmethod
    def all(cls):
        """
        Returns all the crab rigs within the scene

        :return: list(crab.Rig, crab.Rig, ...)
        """
        return [
            Rig(attr.node().attr(config.RIG_ROOT_LINK_ATTR).inputs()[0])
            for attr in pm.ls("*.%s" % config.RIG_ROOT_LINK_ATTR, r=True)
        ]


# --------------------------------------------------------------------------------------
def get():
    """
    Convenience function for getting the first crab rig in the scene
    """
    rigs = Rig.all()

    if rigs:
        return rigs[0]

    return None
