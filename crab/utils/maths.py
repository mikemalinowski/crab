import pymel.core as pm


# ------------------------------------------------------------------------------
def caclulcate_upvector_position(point_a, point_b, point_c, length=0.5):
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
