import pymel.core as pm

# from .. import config
from .. import create


# ------------------------------------------------------------------------------
def new(node, target, label='', resets=None):
    """
    Creates a snap mapping from the given node to the target. The current
    offset between the two are stored during this process, allowing for that
    offset to be retained when a snap is requested.
    
    :param node: The node which can be snapped
    :type node: pm.nt.Transform

    :param target: The node which acts as a snapping target
    :type target: pm.nt.Transform

    :param label: An identifier for the snap offset
    :type label: str

    :return: Snap node containing the offset
    :rtype: pm.nt.DependNode
    """
    # -- Create a new snap node
    snap_node = _new_node()

    # -- Now we can start hooking up the relevant
    # -- attributes
    snap_node.label.set(label)
    snap_node.isCrabSnap.set(True)

    # -- Connect the relationship attributes
    target.message.connect(
        snap_node.snapTarget,
        force=True,
    )

    node.message.connect(
        snap_node.snapSource,
        force=True,
    )

    # -- Finally we need to get the relative matrix
    # -- between the two objects in their current
    # -- state.
    node_to_modify_mat4 = pm.dt.Matrix(
        node.getMatrix(worldSpace=True),
    )

    node_of_interest_mat4 = pm.dt.Matrix(
        target.getMatrix(worldSpace=True),
    )

    # -- Determine the offset between the two
    offset_mat4 = node_to_modify_mat4 * node_of_interest_mat4.inverse()

    # -- Store that matrix into the matrix
    # -- attribute
    snap_node.offsetMatrix.set(
        offset_mat4,
    )

    # -- If we're given any resets, hook them up now
    if resets:
        for node_to_zero in resets:
            plug = snap_node.attr('nodesToZero').elementByLogicalIndex(
                snap_node.attr('nodesToZero').numElements(),
            )
            node_to_zero.message.connect(plug)

    return snap_node


# ------------------------------------------------------------------------------
def remove(node, label=None):
    """
    Removes any snap relationships on the given node. If a label
    is given then only relationships with that label will be 
    removed.

    :param node: The node in which the snap relationships should
        be removed.
    :type node: pm.nt.Transform

    :param label: An optional argument to specify which snap relationship
        should be removed during this call.
    :type label: str

    :return: The number of snap relationships removed.
    """
    snap_nodes = get(node)

    if not snap_nodes:
        return 0

    # -- Assume we need to delete everything
    to_delete = snap_nodes

    # -- Check if we need to filter by a specified lable
    if label:
        to_delete = [
            snap_node
            for snap_node in snap_nodes
            if snap_node.label.get() == label
        ]

    # -- Remove the relationships
    delete_count = len(to_delete)
    pm.delete(to_delete)

    return delete_count


# ------------------------------------------------------------------------------
def labels(node):
    """
    Gives access to all the labels assigned to the given node.

    :param node: Node to query
    :type node: pm.nt.Transform

    :return: list(str, str, str, ...)
    """
    found_labels = [
        snap_node.label.get()
        for snap_node in get(node)
    ]

    return list(set(found_labels))


# ------------------------------------------------------------------------------
def members(label, namespace=None, from_nodes=None):
    """
    This function allows you to query all the nodes which contain
    relationships with a specified label. 
    
    :param label: The label to query for
    :type label: str

    :param namespace: Optional argument to filter only nodes within a given
        namespace
    :type namespace: str

    :param from_nodes: An optional argument to filter only nodes within
        a specific node list
    :type from_nodes: list(pm.nt.Transform, ..)

    :return: list(pm.nt.Transform, pm.nt.Transform, ...)
    """
    # -- Get all the snap nodes
    snap_nodes = pm.ls('*.isCrabSnap', r=True, o=True)

    # -- Define our output
    matched = list()

    for snap_node in snap_nodes:

        # -- Skip nodes which do not have matching labels
        if snap_node.label.get() != label:
            continue

        # -- Filter any namespace differences if required
        if namespace and namespace not in snap_node.name():
            continue

        # -- Filter by the node list if given
        if from_nodes:

            source_node = snap_node.snapSource.inputs()

            if not source_node:
                continue

            if source_node[0] not in from_nodes:
                continue

        matched.append(snap_node)

    return sorted(matched, key=lambda x: x.snapSource.inputs()[0].longName().count('|'))


# ------------------------------------------------------------------------------
def get(node, target=None, label=None):
    """
    Returns teh snap nodes assigned to the given node

    :param node: Node to query
    :type node: pm.nt.Transform

    :param target: If given, only snap nodes which bind the node and the 
        target together are returned.
    :type target: pm.nt.Transform

    :param label: If given only relationships with the given label
        will be returned
    :type label: str

    :return: list(pm.nt.Network, ...)
    """

    # -- Cycle over all the network nodes connected
    # -- to our snapSource
    possibilities = [
        attr.node()
        for attr in node.message.outputs(type='network', plugs=True)
        if attr.name(includeNode=False) == 'snapSource'
    ]

    # -- Ensure we're only dealing with snap nodes
    possibilities = [
        possibility
        for possibility in possibilities
        if possibility.hasAttr('isCrabSnap')
    ]

    # -- If we're asked to get by label lets restrict
    # -- to that now
    if label:
        possibilities = [
            possibility
            for possibility in possibilities
            if possibility.label.get() == label
        ]

    # -- If we're given a specific target lets filter
    # -- out anything else
    if target:
        possibilities = [
            possibility
            for possibility in possibilities
            if target in possibility.snapTarget.inputs()
        ]

    return possibilities


# ------------------------------------------------------------------------------
def snappable(node):
    """
    Returns True if the given node has any snap nodes linked to it

    :param node: The node to check
    :type node: pm.nt.Transform

    :return: bool
    """
    return len(get(node)) > 0


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def snap(node, target, start_time=None, end_time=None, key=True):
    """
    This will match one node to the other providing there is a snap
    relationship between then. If a time range is given then the match
    will occur over time.

    If no snap relationship exists between the two nodes then a straight
    forward matrix matching will occur.

    :param node: The node to move
    :type node: pm.nt.Transform

    :param target: The node to match to
    :type target: pm.nt.Transform

    :param start_time: The time to start from. If this is not given then
        the match will only occur on the current frame
    :type start_time: int

    :param end_time: The time to stop at. If this is not given then the
        match will only occur on the current frame
    :type end_time: int

    :param key: If true the matching will be keyed. Note, if a start and
        end time are given then this is ignored and the motion will always
        be keyed.
    :type key: bool

    :return:
    """
    # -- Get the snaps between the two nodes
    snap_nodes = get(node, target=target)

    # -- If we have a snap, take the first and use that offset matrix
    # -- otherwise we use
    if snap_nodes:
        offset_matrix = snap_nodes[0].offsetMatrix.get()

    else:
        offset_matrix = pm.dt.Matrix()

    # -- Get the list of nodes to reset
    zero_these = list()
    if snap_nodes[0].hasAttr('nodesToZero'):
        zero_these = snap_nodes[0].nodesToZero.inputs()

    # -- Use the current time if we're not given specific
    # -- frame ranges
    start_time = start_time if start_time is not None else int(pm.currentTime())
    end_time = end_time if end_time is not None else int(pm.currentTime())

    # -- Cycle the frame range ensuring we dont accidentally
    # -- drop off the last frame
    for frame in range(start_time, end_time+1):
        pm.setCurrentTime(frame)

        _set_worldspace_matrix(
            node,
            target,
            offset_matrix,
        )

        # -- Zero any nodes which require it
        for node_to_zero in zero_these:
            _zero_node(node_to_zero)

            if key or start_time != end_time:
                pm.setKeyframe(node_to_zero)

        # -- Check if we need to key
        if key or start_time != end_time:
            pm.setKeyframe(node)


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def snap_label(label=None, restrict_to=None, start_time=None, end_time=None, key=True):
    """
    This will match all the members of the snap group.

    :param label: The name of the snap group to get the members from
    :type label: str

    :param restrict_to: If given, only group members which are also present
        within this list will be matched.
    :type restrict_to: pm.nt.Transform

    :param start_time: The time to start from. If this is not given then
        the match will only occur on the current frame
    :type start_time: int

    :param end_time: The time to stop at. If this is not given then the
        match will only occur on the current frame
    :type end_time: int

    :param key: If true the matching will be keyed. Note, if a start and
        end time are given then this is ignored and the motion will always
        be keyed.
    :type key: bool

    :return:
    """
    # -- Get a list of all the snap nodes with this label
    snap_nodes = members(
        label,
        from_nodes=restrict_to
    )

    # -- Use the current time if we're not given specific
    # -- frame ranges
    start_time = start_time if start_time is not None else int(pm.currentTime())
    end_time = end_time if end_time is not None else int(pm.currentTime())

    # -- Cycle the frame range ensuring we dont accidentally
    # -- drop off the last frame
    for frame in range(start_time, end_time+1):
        pm.setCurrentTime(frame)

        for snap_node in snap_nodes:

            # -- NOTE: We *could* group the target/node together
            # -- outside the frame iteration as an optimisation. For
            # -- the sake of code simplicity on the first pass its
            # -- done during iteration.
            pass

            # -- Get the target node - if there is no target
            # -- we do nothing
            targets = snap_node.snapTarget.inputs()

            if not targets:
                continue

            # -- Pull out the target as a named variable for
            # -- code clarity
            target = targets[0]

            # -- Pull out the node to modify
            nodes = snap_node.snapSource.inputs()

            if not nodes:
                continue


            # -- Pull out the node as a named variable for
            # -- code clarity
            node = nodes[0]

            # -- Match the two objects with the offset matrix
            _set_worldspace_matrix(
                node,
                target,
                snap_node.offsetMatrix.get(),
            )

            # -- Get the list of nodes to reset
            if snap_node.hasAttr('nodesToZero'):
                zero_these = snap_node.nodesToZero.inputs()

                # -- Zero any nodes which require it
                for node_to_zero in zero_these:
                    _zero_node(node_to_zero)

                    if key or start_time != end_time:
                        pm.setKeyframe(node_to_zero)
            
            # -- Key the match if we need to
            if key or start_time != end_time:
                pm.setKeyframe(node)


# ------------------------------------------------------------------------------
def _new_node():
    """
    Snap relationships are stored on network nodes with a very specific
    attribute setup. This function creates that setup for us.
    
    :return: pm.nt.Network
    """
    snap_node = create.generic(
        node_type='network',
        prefix=config.SNAP,
        description='Meta',
        side=config.SIDELESS,
    )

    # -- Add an attribute to ensure we can always identify 
    # -- this node
    snap_node.addAttr(
        'isCrabSnap',
        at='bool',
        dv=True,
    )

    snap_node.addAttr(
        'label',
        dt='string',
    )

    # -- Next add the relationship attributes
    snap_node.addAttr(
        'snapTarget',
        at='message',
    )

    snap_node.addAttr(
        'snapSource',
        at='message',
    )

    # -- We add our attributes for offset data
    snap_node.addAttr(
        'offsetMatrix',
        dt='matrix',
    )

    # -- Define a list of items which should be reset whenever
    # -- this snap is acted upon
    snap_node.addAttr(
        'nodesToZero',
        at='message',
        multi=True,
    )

    return snap_node


# ------------------------------------------------------------------------------
def _set_worldspace_matrix(node, target, offset_matrix):
    """
    Sets the worldspace matrix of the given node to that of the target
    matrix with the offset matrix applied.

    :param node: Node to set the transform on
    :type node: pm.nt.Transform

    :param offset_matrix: The matrix to offset during the apply
    :type offset_matrix: pm.dt.Matrix

    :return: None
    """
    # -- Apply the offset
    target_matrix = pm.dt.Matrix(target.getMatrix(worldSpace=True))
    resolved_mat4 = offset_matrix * target_matrix

    # -- Now we need to apply the matrix
    node.setMatrix(
        resolved_mat4,
        worldSpace=True,
    )


# ------------------------------------------------------------------------------
def _zero_node(node):
    """
    Zero's the nodes

    :param node:
    :return:
    """
    for attr in node.listAttr(k=True):

        attr_name = attr.name(includeNode=False)

        if 'scale' in attr_name:
            value = 1.0

        elif 'translate' in attr_name or 'rotate' in attr_name:
            value = 0.0

        else:
            continue

        try:
            attr.set(value)
        except:
            pass

    for attr in node.listAttr(k=True, ud=True):
        value = pm.attributeQuery(
            attr.name(includeNode=False),
            node=node,
            listDefault=True,
        )

        try:
            attr.set(value)

        except:
            continue
