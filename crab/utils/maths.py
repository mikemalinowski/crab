import collections
import pymel.core as pm


# ------------------------------------------------------------------------------
def calculate_upvector_position(point_a, point_b, point_c, length=0.5):
    """
    Based on three points, this will calculate the position for an
    up-vector for the plane.

    :param point_a: Start point
    :type point_a: pm.dt.Vector or pm.nt.Transform

    :param point_b: Mid Point
    :type point_b: pm.dt.Vector or pm.nt.Transform

    :param point_c: End Point
    :type point_c: pm.dt.Vector or pm.nt.Transform

    :param length: Optional multiplier for the length of the vector. By
        default this is 0.5 of the sum of the points ab and bc.
    :type length: float

    :return: pm.nt.Vector
    """

    # -- If we're given transforms we need to convert them to
    # -- vectors
    if isinstance(point_a, pm.nt.Transform):
        point_a = point_a.getTranslation(worldSpace=True)

    if isinstance(point_b, pm.nt.Transform):
        point_b = point_b.getTranslation(worldSpace=True)

    if isinstance(point_c, pm.nt.Transform):
        point_c = point_c.getTranslation(worldSpace=True)

    # -- Create the vectors between the points
    ab = point_b - point_a
    ac = point_c - point_a
    cb = point_c - point_b

    # -- Get the center point between the end points
    center = point_a + ((ab.dot(ac) / ac.dot(ac))) * ac

    # -- Create a normal vector pointing at the mid point
    normal = (point_b - center).normal()

    # -- Define the length for the upvector
    vector_length = (ab.length() + cb.length()) * length

    # -- Calculate the final vector position
    result = point_b + (vector_length * normal)

    return result


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def global_mirror(transforms=None, across=None, behaviour=True, remap=None, translation_only=False):
    """ 
    This function is taken from github with a minor modification. The
    author and credit goes to Andreas Ranman.
    
    Github Url:
        https://gist.github.com/rondreas/1c6d4e5fc6535649780d5b65fc5a9283
    
    Mirrors transform across hyperplane. 

    transforms -- list of Transform or string.
    across -- plane which to mirror across.
    behaviour -- bool 

    """
    # No specified transforms, so will get selection
    if not transforms:
        transforms = pm.selected(type='transform')

    # Check to see all provided objects is an instance of pymel transform node,
    elif not all(map(lambda x: isinstance(x, pm.nt.Transform), transforms)):
        raise ValueError("Passed node which wasn't of type: Transform")

    # -- Ensure we have a mirror plane
    across = across or get_likely_mirror_plane(transforms[0])

    # Validate plane which to mirror across,
    if not across in ('XY', 'YZ', 'XZ'):
        raise ValueError(
            "Keyword Argument: 'across' not of accepted value ('XY', 'YZ', 'XZ').")

    stored_matrices = collections.OrderedDict()

    for transform in transforms:

        # Get the worldspace matrix, as a list of 16 float values
        mtx = pm.xform(transform, q=True, ws=True, m=True)

        # Invert rotation columns,
        rx = [n * -1 for n in mtx[0:9:4]]
        ry = [n * -1 for n in mtx[1:10:4]]
        rz = [n * -1 for n in mtx[2:11:4]]

        # Invert translation row,
        t = [n * -1 for n in mtx[12:15]]

        # Set matrix based on given plane, and whether to include behaviour or not.
        if across is 'XY':
            mtx[14] = t[2]  # set inverse of the Z translation

            # Set inverse of all rotation columns but for the one we've set translate to.
            if behaviour:
                mtx[0:9:4] = rx
                mtx[1:10:4] = ry

        elif across is 'YZ':
            mtx[12] = t[0]  # set inverse of the X translation

            if behaviour:
                mtx[1:10:4] = ry
                mtx[2:11:4] = rz
        else:
            mtx[13] = t[1]  # set inverse of the Y translation

            if behaviour:
                mtx[0:9:4] = rx
                mtx[2:11:4] = rz

        stored_matrices[transform] = mtx

    for transform in stored_matrices:
        target = transform
        if remap:
            try:
                target = remap(transform)
            except:
                continue

        if translation_only:
            target.setTranslation(
                stored_matrices[transform][12:15],
                space='world',
            )

        else:
            pm.xform(target, ws=True, m=stored_matrices[transform])


# ------------------------------------------------------------------------------
def get_likely_mirror_plane(node):
    """
    Looks at the worldspace transform of a node and returns a mirror
    plane string of either XY, YZ or XZ
    
    The worldspace translation of the node is used to determine this.
    
    :param node: Node to test
    :type node: pm.nt.Transform
    
    :return: str
    """
    position = [abs(n) for n in node.getTranslation(node, worldSpace=True)]

    # -- We're only interested in a two dimensional plane, so pop
    # -- out the Y axis
    if pm.upAxis(q=True, axis=True) == 'y':
        position.pop(1)

    else:
        position.pop(2)

    # -- Of the X and Z plane, get the prominent one
    prominent_axis = position.index(max(position))

    if prominent_axis == 0:
        return 'YZ'

    else:
        return 'XZ'
