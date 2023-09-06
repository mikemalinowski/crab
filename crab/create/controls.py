from .. import config
from .basics import generic


# --------------------------------------------------------------------------------------
def control(
    description,
    side,
    parent=None,
    xform=None,
    match_to=None,
    shape=None,
    lock_list=None,
    hide_list=None,
    rotation_order=None,
    counter=1,
):
    """
    Creates a control structure - which is a structure which conforms to the
    following hierarchy:

        ORG -> ZRO -> OFF -> CTL

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

    :param lock_list: This is a list of attribute names you want to lock. This
        is only applied to the control.
    :type lock_list: A list of strings, or a string deliminated by ;

    :param hide_list: This is a list of attribute names you want to hide. This
        is only applied to the control.
    :type hide_list: A list of strings, or a string deliminated by ;

    :param rotation_order: The rotation order that should be assigned to this
        control by default
    :type rotation_order: int

    :param counter: [Optional] What counter should be tested for generating
        the name of the rig element
    :type counter: int

    :return: pm.nt.DependNode
    """
    prefixes = [
        config.ORG,
        config.ZERO,
        config.OFFSET,
        config.CONTROL,
    ]

    for prefix in prefixes:
        # -- Declare any specific options for this iteration
        options = dict()

        # -- Controls are the only items which have shapes
        if prefix == config.CONTROL:
            options["shape"] = shape

        parent = generic(
            "transform",
            prefix,
            description,
            side,
            parent=parent,
            xform=xform,
            match_to=match_to,
            counter=counter,
            **options
        )

    # -- Check if we need to convert lock or hide data
    if hide_list and not isinstance(hide_list, list):
        hide_list = hide_list.split(";")

    if lock_list and not isinstance(lock_list, list):
        lock_list = lock_list.split(";")

    if hide_list:
        for attr_to_hide in hide_list:
            if attr_to_hide:
                parent.attr(attr_to_hide).set(k=False)

    if lock_list:
        for attr_to_lock in lock_list:
            if attr_to_lock:
                parent.attr(attr_to_lock).lock()

    # -- Now expose the rotation order
    parent.rotateOrder.set(k=True)

    parent.rotateOrder.set(rotation_order or config.DEFAULT_CONTROL_ROTATION_ORDER)

    return parent
