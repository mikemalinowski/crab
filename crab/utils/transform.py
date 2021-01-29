"""
This module contains functionality to help manipulate transformation data
"""
import pymel.core as pm


# --------------------------------------------------------------------------------------------------
def resolve_translation(vector):
    """
    This assumes a list of length 3 in the order of X, Y, Z where Y is considered the
    'up axis'. If the up axis of the application is indeed Y, then the vector is returned
    untouched. However, if the up-axis is Z then the vector is mutated.

    :param vector: Translation vector
    :type vector: list(x, y, z)

    :return: list(float, float, float)
    """

    if pm.upAxis(q=True, axis=True) == 'y':
        return vector

    return [
        vector[2],
        vector[0],
        vector[1],

    ]
