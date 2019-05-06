"""
This module contains the Component class. This class should be inherited from
whenever you want to write new component for crab.
"""
import json
import pymel.core as pm


from . import meta
from . import utils
from . import create
from . import config


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

    # --------------------------------------------------------------------------
    def create_skeleton(self, parent):
        """
        This is where you should build your skeleton. `parent` is the node
        your build skeleton should reside under and it will never be None.
        
        :param parent: Node to parent your skeleton under
        :type parent: pm.nt.DagNode
        
        :return: True if successful
        """
        pass

    # --------------------------------------------------------------------------
    def create_guide(self, parent, skeleton_component):
        """
        This function allows you to build a guide element. 
        
        :param parent: Parent node to build the rig under
        
        :param skeleton_component: A Component instance representing the 
            skeleton.
             
        :return: 
        """
        pass

    # --------------------------------------------------------------------------
    def create_rig(self, parent, skeleton_component, guide_component):
        """
        This should create your animation rig for this segment. The parent
        will be a pre-constructed crabSegment transform node and the guide
        will be an instance of this class centered on the guide.

        :param parent: Parent node to build the rig under
        
        :param skeleton_component: A Component instance representing the 
            skeleton.
            
        :return: 
        """

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

        # -- By default assume we do not have a root yet
        self.root = None

        # -- If we are given a node, we should look for the root
        # -- of the component from the node we're given.
        if node:
            self.define_root(node)

    # --------------------------------------------------------------------------
    def define_root(self, node, *args, **kwargs):
        """
        Finds the root node and updates the options of the class to those
        off the root

        :param node: Node to search from
        :type node: pm.nt.Transform

        :return: None
        """
        # -- Define the root
        self.root = meta.get_meta_root(node)

        # -- Now update the class options based on the options stored
        # -- within the meta node
        self.options.update(
            json.loads(
                meta.get_meta_node(self.root).attr(config.META_OPTIONS).get(),
            ),
        )

    # --------------------------------------------------------------------------
    def tag(self, target, label):
        """
        Shortcut for tagging to the meta root
        
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
    # noinspection PyUnresolvedReferences,PyMethodMayBeStatic
    def bind(self, skeletal_joint, control, constrain=True, **kwargs):
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

        # -- Add a binding link between the skeletal joint and
        # -- the control
        if not skeletal_joint.hasAttr(config.BOUND):
            skeletal_joint.addAttr(
                config.BOUND,
                at='message',
            )
        control.message.connect(skeletal_joint.attr(config.BOUND))

    # --------------------------------------------------------------------------
    def define_skeleton_root(self, node):
        """
        This will add a meta node to the given node to mark that node as being
        the root of the components skeleton hierarchy.

        :param node: Node to mark as the skeletal root

        :return: None 
        """
        # -- Create the meta node, passing through all our options
        meta.create(
            config.COMPONENT_SKELETON_TYPE,
            node,
            **{
                config.META_IDENTIFIER: self.identifier,
                config.META_VERSION: self.version,
                config.META_OPTIONS: json.dumps(self.options),
            }
        )

        # -- Add the guide options attribute
        node.addAttr(
            config.GUIDE_OPTIONS,
            dt='string',
        )

        # -- Update the root property of the class, to ensure its
        # -- always accessible
        self.root = node

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def create_control_base(self, parent):
        """
        Convenience function for creating a root for your component. You should
        call this from within your create_rig function call.
        
        :param parent: Parent for the base node
        :type parent: pm.nt.DagNode
        
        :return: newly created node (pm.nt.DagNode) 
        """
        # -- Create the node
        node = create.generic(
            node_type='transform',
            prefix=config.RIG_COMPONENT,
            description=self.options.description or self.identifier,
            side=self.options.side,
            parent=parent,
            match_to=parent,
        )

        # -- Create the meta node, passing through all our options
        meta.create(
            config.COMPONENT_RIG_TYPE,
            node,
            **{
                config.META_IDENTIFIER: self.identifier,
                config.META_VERSION: self.version,
                config.META_OPTIONS: json.dumps(self.options),
            }
        )

        return node

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def create_guide_base(self, parent, skeleton_root):
        """
        Convenience function for creating a root for your component. You should
        call this from within your create_guide function call.

        :param parent: Parent for the base node
        :type parent: pm.nt.DagNode

        :return: newly created node (pm.nt.DagNode) 
        """
        # -- Create the node
        node = create.generic(
            node_type='transform',
            prefix=config.GUIDE_COMPONENT,
            description=self.options.description or self.identifier,
            side=self.options.side,
            parent=parent,
            match_to=parent,
        )

        # -- Create the meta node, passing through all our options
        meta_node = meta.create(
            config.COMPONENT_GUIDE_TYPE,
            node,
            **{
                config.META_IDENTIFIER: self.identifier,
                config.META_VERSION: self.version,
                config.META_OPTIONS: json.dumps(self.options),
            }
        )

        # -- Add a guide link
        meta_node.addAttr(
            config.GUIDE_LINK,
            at='message',
        )

        skeleton_root.message.connect(meta_node.attr(config.GUIDE_LINK))

        return node

    # --------------------------------------------------------------------------
    def guide(self):

        # -- Check if the root has a guide link
        for attr in self.root.message.outputs(plugs=True):
            if attr.name(includeNode=False) == config.GUIDE_LINK:
                connections = attr.node().attr(config.LINK).inputs()
                if connections:
                    return self.__class__(attr.node().attr(config.LINK).inputs()[0])

        return None
