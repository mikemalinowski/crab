import json
import itertools
import pymel.core as pm

from .. import config
from .. import create
from . import hierarchy


# ------------------------------------------------------------------------------
def zero(joint):
    for axis in ['X', 'Y', 'Z']:
        joint.attr('rotate%s' % axis).set(0)
        joint.attr('translate%s' % axis).set(0)
        joint.attr('scale%s' % axis).set(1)
        joint.attr('jointOrient%s' % axis).set(0)


# ------------------------------------------------------------------------------
def replicate_chain(from_this, to_this, parent, world=True, replacements=None):
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

        if replacements:
            for replace_this, with_this in replacements.items():
                new_joint.rename(
                    new_joint.name().replace(
                        replace_this,
                        with_this,
                    ),
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
        is_deformer=False,
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
def reverse_chain(joints):
    """
    Reverses the hierarchy of the joint chain.

    :param joints: List of joints in the chain to reverse

    :return: the same list of joints in reverse order
    """
    # -- Store the base parent so we can reparent the chain
    # -- back under it
    base_parent = joints[0].getParent()

    # -- Start by clearing all the hierarchy of the chain
    for joint in joints:
        joint.setParent(None)

    # -- Now build up the hierarchy in the reverse order
    for idx in range(len(joints)):
        try:
            joints[idx].setParent(joints[idx + 1])
        except IndexError:
            pass

    # -- Finally we need to set the base parent once
    # -- again
    joints[-1].setParent(base_parent)

    joints.reverse()

    return joints


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


# ------------------------------------------------------------------------------
def write_joint_file(joints, filepath):
    """
    Writes out joint information to a json file to allow the joint
    structure to be rebuilt easily.

    :param joints: List of joints to write out
    :type joints: list(pm.nt.Joint, ...)

    :param filepath: Filepath to write to
    :type filepath: str

    :return: None
    """
    all_joint_data = dict()

    for joint in joints:

        parent = joint.getParent()

        if parent not in joints:
            parent = None

        joint_data = dict(
            name=joint.name(),
            parent=parent.name() if parent else None,
            radius=joint.radius.get(),
            attributes=dict(),
            is_deformer=True,
        )

        for type_ in ['translate', 'rotate', 'scale', 'jointOrient']:
            for axis in ['X', 'Y', 'Z']:
                joint_data['attributes'][type_ + axis] = joint.attr(
                    type_ + axis).get()

        # -- If there is A or T pose attributes, record this as well
        for pose_attr in ['APose', 'TPose']:
            if joint.hasAttr(pose_attr):
                joint_data['attributes'][pose_attr] = list(
                    itertools.chain(*joint.attr(pose_attr).get())
                )

        all_joint_data[joint.name()] = joint_data

    with open(filepath, 'w') as f:
        json.dump(all_joint_data, f, sort_keys=True, indent=4)

    return None


# ------------------------------------------------------------------------------
def load_joint_file(root_parent, all_joint_data, side_override=None):
    """
    Creates a joint hierarchy based on the given data. If the data
    is a dictionary it is parsed as is otherwise it is assumed to be
    a json file and will be read accordingly.

    :param root_parent: The joint in which to parent the generated
        structure under.
    :type root_parent: pm.nt.Joint

    :param all_joint_data: Either a dictionary conforming to the structure
        generated by the write_joint_file method or a filepath to a json file
        containing the equivalent structure.
    :type all_joint_data: dict or str

    :param side_override: If given, this can be used to override the side
        segment of the names of the generated joints.
    :type side_override: str

    :return: dictionary where the key is the name entry in the file
        and the value is the generated joint
    """
    if not isinstance(all_joint_data, dict):
        with open(all_joint_data, 'r') as f:
            all_joint_data = json.load(f)

    generated_joint_map = dict()

    for joint_data in all_joint_data.values():

        # -- Create the joint
        pm.select(clear=True)

        joint = create.joint(
                description=config.get_description(joint_data['name']),
                side=side_override or config.get_side(joint_data['name']),
                counter=config.get_counter(joint_data['name']),
                is_deformer=joint_data.get('is_deformer', True),
                radius=joint_data['attributes'].get('radius', 1),
                parent=None,
        )

        # -- Set the joint attributes
        generated_joint_map[joint_data['name']] = joint

    # -- Now set up the parenting
    for identifier, joint in generated_joint_map.items():
        parent_name = all_joint_data[identifier]['parent']

        if parent_name:
            joint.setParent(generated_joint_map[parent_name])

        else:
            joint.setParent(root_parent)

        for pose_attr in ['APose', 'TPose']:
            if pose_attr in all_joint_data[identifier]['attributes']:
                joint.addAttr(pose_attr, at='matrix')

        for name, value in all_joint_data[identifier]['attributes'].items():
            if joint.hasAttr(name):
                joint.attr(name).set(value)

    return generated_joint_map
