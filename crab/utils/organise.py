import pymel.core as pm


# ------------------------------------------------------------------------------
def add_separator_attr(node):
    """
    Adds an underscored attribute as an attribute separator

    :param node: Node to add the separator to
    :tpye node: pm.nt.DependNode

    :return: None
    """
    character = '_'
    name_to_use = character * 8

    while node.hasAttr(name_to_use):
        name_to_use += character

    node.addAttr(
        name_to_use,
        niceName='-' * 12,
        k=True,
    )

    node.attr(name_to_use).lock()


# ------------------------------------------------------------------------------
def add_to_layer(nodes, layer_name):
    """
    Adds a node to the layer with the given name. If that layer does not
    exist it will be created with default options.

    :param nodes: List of nodes (or a single node)
    :type nodes: pm.nt.Transform or list(pm.nt.Transform, ..)

    :param layer_name: Name of layer to add to
    :type layer_name: str

    :return: None
    """

    # -- If the layer does not exist, we need to create it
    if not pm.ls(layer_name, type='displayLayer'):
        pm.createDisplayLayer(
            name=layer_name,
            empty=True,
        )

    # -- If the nodes is a list a single node we should convert
    # -- that to a list
    nodes = [nodes]

    # -- Get the layer
    layer = pm.PyNode(layer_name)
    layer.addMembers(nodes)
