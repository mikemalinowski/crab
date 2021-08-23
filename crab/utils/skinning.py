

# --------------------------------------------------------------------------------------------------
def is_skinned(joint):
    """
    Returns True if the given joint is being used for any skinning
    """
    return len(joint.outputs(type='skinCluster')) > 0


# --------------------------------------------------------------------------------------------------
def connected_skins(joint):
    """
    Returns True if the given joint is being used for any skinning
    """
    return joint.outputs(type='skinCluster')
