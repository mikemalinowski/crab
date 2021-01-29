import pymel.core as pm

from ..utils import shapes
from .. import config


# ------------------------------------------------------------------------------
def generic(node_type,
            prefix,
            description,
            side,
            parent=None,
            xform=None,
            match_to=None,
            shape=None,
            find_transform=False,
            counter=1):
    """
    Convenience function for creating a node, generating the name using
    the unique name method and giving the ability to assign the parent and
    transform.

    :param node_type: Type of node to create, such as 'transform'
    :type node_type: str

    :param prefix: Prefix to assign to the node name
    :type prefix: str

    :param description: Descriptive section of the name
    :type description: str

    :param side: Tag for the location to be used during the name generation
    :type side: str

    :param parent: Optional parent to assign to the node
    :type parent: pm.nt.DagNode

    :param xform: Optional worldSpace matrix to apply to the object
    :type xform: pm.dt.Matrix

    :param match_to: Optional node to match in worldspace
    :type match_to: pm.nt.DagNode

    :param shape: Optional shape to apply to the node
    :type shape: name of shape or path

    :param find_transform: If True, then the nodes transform will
        be found if the created node is not a transform
    :type find_transform: bool

    :return: pm.nt.DependNode
    """
    # -- Create the node
    node = pm.createNode(node_type)

    if not isinstance(node, pm.nt.Transform) and find_transform:
        node = node.getParent()

    # -- Name it based on our naming convention
    node.rename(
        config.name(
            prefix=prefix,
            description=description,
            side=side,
            counter=counter,
        ),
    )

    # -- If we're given a matrix utilise that
    if xform:
        node.setMatrix(
            xform,
            worldSpace=True,
        )

    # -- Match the object to the target object if one
    # -- is given.
    if match_to:
        node.setMatrix(
            match_to.getMatrix(worldSpace=True),
            worldSpace=True,
        )

    # -- Parent the node if we're given a parent
    if parent:
        node.setParent(parent)

    if shape:
        shapes.apply(node, shape)

    return node


# ------------------------------------------------------------------------------
def org(description, side, parent=None):
    """
    Creates a simple org node

    :param description: Descriptive section of the name
    :type description: str

    :param side: Tag for the location to be used during the name generation
    :type side: str

    :param parent: Optional parent to assign to the node
    :type parent: pm.nt.DagNode

    """
    return generic(
        prefix=config.ORG,
        node_type='transform',
        description=description,
        side=side,
        parent=parent,
        match_to=parent,
    )
