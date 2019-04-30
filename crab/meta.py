"""
This module contains all the methods relating to the creating and 
utilisation of meta nodes.

In crab a metanode is simply a network node which is tagged to the
root of components or rigs. The meta nodes store information about the
plugins the component represents. 

The metanodes also serve as a tagging feature, allowing objects in the 
scene to be tagged with a label and therefore found again by that label.
"""
from . import utils
from . import config

import json
import pymel.core as pm


# ------------------------------------------------------------------------------
# noinspection PyTypeChecker
def create(meta_type, connect_to, **kwargs):
    """
    Creates a new metanode and connects it to the given dag node. The 
    metanode is stamped with a type string and any keyword arguments
    which are passed down are used to set values on those attributes.
    
    :param meta_type: This should be a metatype as defined in crab.config
        This allows crab to distinguish between rigs, components, skeletons
        and guides etc.
    :type meta_type: str
    
    :param connect_to: This is the node you want the metanode to be 
        connected to.
    :type connect_to: pm.nt.DagNode
    
    :param kwargs: Any keyword arguments where the keyword must be a
        name of an attribute on the metanode and the value is the value
        you want to set the attribute to.
    
    :return: pm.nt.DependNode
    """
    # -- Create the node marker
    meta_node = pm.createNode('network')
    meta_node.rename(
        utils.name(
            prefix=config.META,
            description=utils.get_description(connect_to.name()),
            side=utils.get_side(connect_to.name()),
        )
    )

    # -- Add the attribute to allow us to hook this to a node
    meta_node.addAttr(
        config.LINK,
        at='message',
    )

    # -- Now connect the marker to the node
    connect_to.message.connect(meta_node.attr(config.LINK))

    # -- Add the attributes required for a component marker
    meta_node.addAttr(
        config.META_TYPE,
        dt='string'
    )
    meta_node.attr(config.META_TYPE).set(meta_type)

    # -- Store the version of the component
    meta_node.addAttr(
        config.META_IDENTIFIER,
        dt='string',
    )

    meta_node.addAttr(
        config.META_VERSION,
        at='float',
    )

    meta_node.addAttr(
        config.META_OPTIONS,
        dt='string',
    )
    
    for option, value in kwargs.items():
        if meta_node.hasAttr(option):
            meta_node.attr(option).set(value)
    
    return meta_node


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def has_meta(node, specific_type=None):
    """
    Checks whether the given node has a meta node. You can also check 
    whether it has a meta node of a designated type.
    
    :param node: The node to check for
    :type node: pm.nt.DagNode
    
    :param specific_type: Optional string to check whether the meta node
        is of a type you're specifically looking for.
    :type specific_type: str
    
    :return: True if a meta node was found 
    """

    # -- All meta nodes are connected via the message links, so start
    # -- by checking that attribute
    for attribute in node.message.outputs(plugs=True):

        # -- Ignore any attributes which are not meta link attributes
        if attribute.name(includeNode=False) != config.LINK:
            continue

        # -- Give ourselves easy access to the node hosting
        # -- the attribute
        potential_node = attribute.node()

        # -- Check whether this node meets all our requirements
        if isinstance(potential_node, pm.nt.Network):
            if potential_node.hasAttr(config.META_TYPE):
                type_attr = potential_node.attr(config.META_TYPE)

                if specific_type and type_attr.get() != specific_type:
                    continue

                return True

    return False


# ------------------------------------------------------------------------------
def get_meta_root(node, specific_type=None):
    """
    Given a dag node this will cycle up the nodes hierarchy looking for the 
    first node defined by a meta node, optionally with a specific type defined.
    
    :param node: The node from which a search should start from
    :type node: pm.nt.DagNode 
    
    :param specific_type: Optional string to test when looking for a meta
        node
    :type specific_type: str
    
    :return: The meta root node if one is found 
    """
    while True:

        if not node:
            return None

        if has_meta(node, specific_type=specific_type):
            return node

        # -- This node has no component markers, so lets go up
        # -- to the next parent
        node = node.getParent()

        # -- If the next parent is None - meaning we have hit the
        # -- world level, we have nothing to find
        if not node:
            return None


# ------------------------------------------------------------------------------
def get_meta_node(node, specific_type=None):
    """
    From a given node, a search for a meta root is performed. Once found the
    actual metanode is then returned from the root.
    
    :param node: Node to start searching from
    :type node: pm.nt.DagNode
     
    :param specific_type: Optional meta type to check for
     
    :return: pm.nt.DependNode 
    """
    meta_root = get_meta_root(node, specific_type=specific_type)

    if not meta_root:
        return None

    for candidate in node.message.outputs():
        if candidate.hasAttr(config.META_TYPE):
            return candidate


# ------------------------------------------------------------------------------
def tag(target, label, meta_root=None):
    """
    Tagging is a mechanism which allows for objects to be accessible
    by string labels instead of using their names. When tagging you 
    define the label nad the object. Multiple tags can be made with 
    the same label.
    
    :param target: Object to store against the tag
    :type target: pm.nt.DependNode
    
    :param label: Label to be used to store the node with
    :type label: str
    
    :param meta_root: Optional declaration of the meta root to store
        the tag information on. If not given then a search for the 
        first metaroot above the target is utilised.
    :type meta_root: pm.nt.DagNode
    
    :return: None 
    """
    if not meta_root:
        meta_root = get_meta_root(target)

    if not meta_root:
        raise Exception('No meta root could be found')

    meta_node = get_meta_node(meta_root)

    # -- Now we need to check if we need to add a new message
    # -- attribute or use a pre-existing one
    attribute_name = 'crabLabel%s' % label

    if not meta_node.hasAttr(attribute_name):
        meta_node.addAttr(
            attribute_name,
            at="message",
            multi=True,
        )

    # -- Now make the message connection
    plug = meta_node.attr(attribute_name).elementByLogicalIndex(
        meta_node.attr(attribute_name).numElements(),
    )
    target.message.connect(plug)


# ------------------------------------------------------------------------------
def find(label, meta_root):
    """
    Looks for a label definition on the given meta root and returns a list
    of all the objects tagged with that label.
    
    :param label: Label to search for
    :type label: str
    
    :param meta_root: Meta Root node to look at when finding the results
    :type meta_root: pm.nt.DagNode
    :return: 
    """
    meta_node = get_meta_node(meta_root)

    # -- Check that the expected attribute exists
    attribute_name = 'crabLabel%s' % label
    if meta_node.hasAttr(attribute_name):
        return meta_node.attr(attribute_name).inputs()

    return []


# ------------------------------------------------------------------------------
def get_identifier(node):
    """
    Convenience function for returning the value of the identifier 
    attribute of the given meta node (or the meta node representing
    the given node).
    
    :param node: The node to search from
    :type node: pm.nt.DagNode
    
    :return: str 
    """
    return get_meta_node(node).attr(config.META_IDENTIFIER).get()


# ------------------------------------------------------------------------------
def get_type(node):
    """
    Convenience function for returning the value of the meta type 
    attribute of the given meta node (or the meta node representing
    the given node).
    
    :param node: The node to search from
    :type node: pm.nt.DagNode
    
    :return: str 
    """
    return get_meta_node(node).attr(config.META_TYPE).get()


# ------------------------------------------------------------------------------
def get_version(node):
    """
    Convenience function for returning the value of the version 
    attribute of the given meta node (or the meta node representing
    the given node).
    
    :param node: The node to search from
    :type node: pm.nt.DagNode
    
    :return: int 
    """
    return get_meta_node(node).attr(config.META_VERSION).get()


# ------------------------------------------------------------------------------
def get_options(node):
    """
    Convenience function for returning the value of the options 
    attribute of the given meta node (or the meta node representing
    the given node).
    
    :param node: The node to search from
    :type node: pm.nt.DagNode
    
    :return: dict 
    """
    return json.loads(get_meta_node(node).attr(config.META_OPTIONS).get())
