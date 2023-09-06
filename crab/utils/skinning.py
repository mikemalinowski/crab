# --------------------------------------------------------------------------------------
def is_skinned(joint):
    """
    Returns True if the given joint is being used for any skinning
    """
    return len(joint.outputs(type="skinCluster")) > 0


# --------------------------------------------------------------------------------------
def connected_skins(joint):
    """
    Returns True if the given joint is being used for any skinning
    """
    return list(set(joint.outputs(type="skinCluster")))


# --------------------------------------------------------------------------------------
def does_joint_have_nonzero_weights(skin, joint):
    """
    Checks if the given joint has influence values of more than zero on any vertices
    in the given skin

    :param skin: Skin Cluster to query
    :type skin: pm.nt.SkinCluster

    :param joint: The joint to test if its deforming the skin
    :type joint: pm.nt.Joint

    :return: True if any weights for the given joint are more than zero
    :rtype: bool
    """
    influence_objects = skin.influenceObjects()

    if joint not in influence_objects:
        return False

    joint_index = influence_objects.index(joint)

    for vertex_weights in skin.getWeights(skin.getGeometry()[0]):
        if vertex_weights[joint_index] > 0.0:
            return True

    return False


# --------------------------------------------------------------------------------------
def remove_joint_from_skin(skin, joint, force=True):
    """
    Removes the given joint from the given skin.

    :param skin: Skin Cluster to query
    :type skin: pm.nt.SkinCluster

    :param joint: The joint to test if its deforming the skin
    :type joint: pm.nt.Joint

    :param force: If true, even if the joint has a weighted influence it will be
        removed and the weights will be re-normalized
    :type force: bool

    :return: True if the joint is no longer an influence of the skin
    :rtype: bool
    """

    if joint not in skin.influenceObjects():
        return True

    # -- If we"re not forcing the operation, we should not proceed if there
    # -- are non-zero influence weights for the given joint
    if not force and does_joint_have_nonzero_weights(skin, joint):
        return False

    # -- This will remove the influence and re-normalize
    skin.removeInfluence(joint)

    # -- Dont assume its worked, lets check it has worked
    if joint in skin.influenceObjects():
        return False

    return True
