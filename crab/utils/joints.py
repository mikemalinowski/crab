import pymel.core as pm

from .. import config
from .. import create
from . import hierarchy


# ------------------------------------------------------------------------------
def replicate_chain(from_this, to_this, parent, world=True):
    """
    Replicates the joint chain exactly
    """
    # -- Define our output joints
    new_joints = list()

    joints_to_trace = hierarchy.get_between(from_this, to_this)

    # -- We can now cycle through our trace joints and replicate them
    next_parent = parent

    for joint_to_trace in joints_to_trace:
        new_joint = replicate(
            joint_to_trace,
            parent=next_parent,
        )

        # -- The first joint we always have to simply match
        # -- in worldspace if required
        if world and joint_to_trace == joints_to_trace[0]:
            new_joint.setMatrix(
                joint_to_trace.getMatrix(worldSpace=True),
                worldSpace=True,
            )

        # -- Store the new joint
        new_joints.append(new_joint)

        # -- Mark the new joint as being the parent for
        # -- the next
        next_parent = new_joint

    return new_joints


# ------------------------------------------------------------------------------
def replicate(joint, parent, description=None):
    """
    Replicates an individual joint and makes it a child of the parent

    :param joint: Joint to replicate
    :type joint: pm.nt.Joint

    :param parent: Node to parent the new node under
    :type parent: pm.nt.DagNode

    :param description: Description to replace with. If none the description
        from the joint being replicated is used.
    :type description: str

    :return: pm.nt.Joint
    """

    # -- Create the joint
    new_joint = create.joint(
        description=description or config.get_description(joint),
        side=config.get_side(joint),
        parent=parent,
        match_to=joint,
    )

    # -- Attributes to copy
    vector_attrs = [
        'translate',
        'rotate',
        'scale',
        'jointOrient'
    ]

    # -- Set the specific attributes
    for vector_attr in vector_attrs:
        for axis in ['X', 'Y', 'Z']:
            new_joint.attr(vector_attr + axis).set(
                joint.attr(vector_attr + axis).get(),
            )

    return new_joint


# ------------------------------------------------------------------------------
def move_rotations_to_joint_orients(joint):
    """
    Moves the rotations on the skeleton to the joint orients

    :param joint: The joint to alter
    :type joint: pm.nt.Joint

    :return: None
    """
    # -- Store the world space matrix
    ws_mat4 = joint.getMatrix(worldSpace=True)

    # -- Zero the joint orients
    for attr in ['jointOrientX', 'jointOrientY', 'jointOrientZ']:
        joint.attr(attr).set(0)

    # -- Now we can restore the matrix
    joint.setMatrix(ws_mat4, worldSpace=True)

    # -- Now we can shift the values from the rotation to the orient
    # -- knowing that the world transform will be retained
    for axis in ['X', 'Y', 'Z']:

        # -- Set the orient value
        joint.attr('jointOrient%s' % axis).set(
            joint.attr('rotate%s' % axis).get(),
        )

        # -- Zero the rotation value
        joint.attr('rotate%s' % axis).set(0)

    return None


# ------------------------------------------------------------------------------
def move_joint_orients_to_rotations(joint):
    """
    Moves the values from the joint orient of the node to the rotation
    whilst retaining the transform of the node.

    :param joint: The joint to alter
    :type joint: pm.nt.Joint

    :return: None
    """
    # -- Store the world space matrix
    ws_mat4 = joint.getMatrix(worldSpace=True)

    # -- Zero the joint orients
    for attr in ['jointOrientX', 'jointOrientY', 'jointOrientZ']:
        joint.attr(attr).set(0)

    # -- Now we can restore the matrix
    joint.setMatrix(ws_mat4, worldSpace=True)
