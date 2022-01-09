
import re
import json
import pymel.core as pm

from .. import utils
from .. import config
from .. import create


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

    # -- This allows an icon to be defined
    icon = utils.resources.get('component.png')

    # -- This allows for tooltips to be specified for the options of this component
    tooltips = dict()

    # -- The preview allows you to specify the location of a gif to show the user
    # -- what this behaviour will result in. If not specified then no rich help
    # -- will be presented for this item
    preview = None

    # -- Legacy identifiers are only used to retain backward compatibility
    # -- when changing an identifier.
    legacy_identifiers = list()

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

        # -- We use this mechanism to expose locations as dropdowns
        self.options._side = config.LOCATIONS

        # -- Store the node reference we are given, as this is what
        # -- we will use to find our meta
        self._reference = node
        self._meta = None

    # --------------------------------------------------------------------------
    def save(self):
        """
        Saves any options information from this node back onto the scene
        """

        meta_node = self.meta()

        # -- Write the data back out
        meta_node.Options.set(
            json.dumps(self.options),
        )

# --------------------------------------------------------------------------
    @classmethod
    def rich_help(cls):
        return dict(
            title=cls.identifier.title(),
            gif=cls.preview,
            description=cls.__doc__.strip() if cls.__doc__ else '',
        )

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

        # -- Set an outliner colour for skeletal roots
        node.useOutlinerColor.set(True)
        node.outlinerColorR.set(0)
        node.outlinerColorG.set(0.7)
        node.outlinerColorB.set(1)

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
            return meta_node.attr(config.GUIDE_ROOT_LINK_ATTR).inputs()[0]

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
    def find(self, label=''):
        """
        Convenience function for performing a meta find against
        the component.

        :param label:
        :return:
        """
        meta_node = self.meta()

        # -- Check that the expected attribute exists
        if label:
            attribute_name = 'crabLabel%s' % label
            if meta_node.hasAttr(attribute_name):
                return meta_node.attr(attribute_name).inputs()

        else:
            results = list()
            for attr in meta_node.listAttr(ud=True):
                if 'crabLabel' in attr.name():
                    results.extend(attr.inputs())

            return results

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

        meta_node.addAttr(
            config.META_CONTENTS,
            dt='string',
        )
        meta_node.attr(config.META_CONTENTS).set('[]')

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
    def apply_options(self):
        """
        This will push any changes to the options dictionarly of this class
        instance into the meta node representing this component.

        ```python

            import crab
            import pymel.core as pm

            # -- Get the first rig in the scene
            rig = crab.Rig.all()[0]

            # -- Cycle all the components in the rig
            for component in rig.components():

                # -- Alter some of the options
                if 'lock' in component.options:
                    component.options.lock = ''

                # -- Push our changes back onto the meta node in the scene
                component.apply_options()

        ```
        :return:
        """
        self.meta().Options.set(
            json.dumps(self.options),
        )

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
        This will remove this crab component if possible

        :return: True if the component was removed
        """
        # -- Get a list of all the skeletal joints and check if they are connected
        # -- to any skin clusters. If they are then we do not remove the component
        skinned_joints = list()
        for joint in self.find():
            if joint.name().startswith(config.SKELETON) and utils.skinning.is_skinned(joint):
                skinned_joints.append(joint.name())

        if skinned_joints:
            print('%s could not be removed, as some of the joints are connected to skin clusters' % self.options.description)
            print('\n' + '\n\t'.join(skinned_joints))

            return False

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

        return True