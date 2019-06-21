import pymel.core as pm

from .. import config


# ------------------------------------------------------------------------------
def get_controls(current_only=False):
    """
    Returns all the controls in a rig

    :param current_only: If True only the controls of the currently
        selected rig will be returned.

    :return: List(pm.nt.Transform, ..)
    """
    ns = '*'

    if current_only:
        if pm.selected() and ':' in pm.selected()[0]:
            ns = ':'.join(pm.selected()[0].name().split(':')[:-1])

    return [
        ctl
        for ctl in pm.ls('%s:%s_*' % (ns, config.CONTROL), r=True,type='transform')
        if not isinstance(ctl, pm.nt.Constraint)
    ]


# ------------------------------------------------------------------------------
def component_nodes(node, match_string=None, node_type='transform'):
    """
    Returns all the nodes which belong to the same component as the
    given node. You may optionally provide a match string to do
    name testing against as well as a type filter.

    :param node: Node to search from
    :type node: pm.nt.DagNode

    :param match_string: Optional string to name test against which
        is case sensitive
    :type match_string: str

    :param node_type: Optional node type to test for
    :type node_type: str

    :return: generator(pm.nt.DagNode, ...)
    """
    return
    # return _filtered_children(
    #     node=get_component(node).control_root(),
    #     match_string=match_string,
    #     node_type=node_type,
    # )


# ------------------------------------------------------------------------------
def _filtered_children(node, match_string=None, node_type='transform'):
    """
    Private recursive function which finds all the children within the
    same component

    :param node: Node to search from
    :type node: pm.nt.DagNode

    :param match_string: Optional string to name test against which
        is case sensitive
    :type match_string: str

    :param node_type: Optional node type to test for
    :type node_type: str

    :return: generator(pm.nt.DagNode, ...)
    """
    for child in node.getChildren():
        if config.RIG_COMPONENT in child.name():
            continue

        if match_string:
            if match_string in child.name():
                yield child

        else:
            yield child

        for sub_child in _filtered_children(child, match_string, node_type):
            yield sub_child
