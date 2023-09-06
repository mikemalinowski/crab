import pymel.core as pm

from . import basics
from .. import config


# --------------------------------------------------------------------------------------
def joint(
    description,
    side,
    parent=None,
    xform=None,
    match_to=None,
    radius=3,
    counter=1,
    is_deformer=True,
):
    """
    Creates a joint, ensuring the right parenting and radius

    :param description: Descriptive section of the name
    :type description: str

    :param side: Tag for the location to be used during the name generation
    :type side: str

    :param parent: Optional parent to assign to the node
    :type parent: pm.nt.DagNode or None

    :param xform: Optional worldSpace matrix to apply to the object
    :type xform: pm.dt.Matrix

    :param match_to: Optional node to match in worldspace
    :type match_to: pm.nt.DagNode

    :param radius: Radius to assign to the joint
    :type radius: int

    :param counter: The counter number to start at. By default this is 1 and will
        count up until a unique number is found.
    :type counter: int

    :param is_deformer: If true, this will be placed in a deformers set
    :type is_deformer: bool

    :return: pm.nt.DependNode
    """
    # -- Joints always parent under whatever is selected, so
    # -- clear the selection
    pm.select(clear=True)

    # -- Create the joint
    new_joint = basics.generic(
        "joint",
        config.SKELETON,
        description,
        side,
        parent=parent,
        xform=xform,
        counter=counter,
        match_to=match_to,
    )

    new_joint.jointOrientX.set(0)
    new_joint.jointOrientY.set(0)
    new_joint.jointOrientZ.set(0)

    if parent:
        new_joint.setMatrix(
            parent.getMatrix(worldSpace=True),
            worldSpace=True,
        )

    # -- If we"re given a matrix utilise that
    if xform:
        new_joint.setMatrix(
            xform,
            worldSpace=True,
        )

    # -- Match the object to the target object if one
    # -- is given.
    if match_to:
        new_joint.setMatrix(
            match_to.getMatrix(worldSpace=True),
            worldSpace=True,
        )

    # -- Set the joint radius
    new_joint.radius.set(radius)

    if is_deformer:
        if not pm.objExists("deformers"):
            pm.sets(n="deformers", empty=True)

        deformer_set = pm.PyNode("deformers")

        if isinstance(deformer_set, pm.nt.ObjectSet):
            deformer_set.addMembers([new_joint])

    # -- Clear the selection
    pm.select(clear=True)

    return new_joint
