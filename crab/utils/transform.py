"""
This module contains functionality to help manipulate transformation data
"""
import pymel.core as pm


# --------------------------------------------------------------------------------------------------
def up_axis():
    return pm.upAxis(q=True, axis=True)


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


# --------------------------------------------------------------------------------------------------
def apply(node, tx=None, ty=None, tz=None, rx=None, ry=None, rz=None, sx=None, sy=None, sz=None, jx=None, jy=None, jz=None):
    """
    Convenience function for setting different transform attributes of a transform
    in one function call

    :param node: The node to assign the trasnform to
    :type node: pm.nt.Transform

    :param tx: Value to assign to translateX if given.
    :type tx: float

    :param ty: Value to assign to translateY if given.
    :type ty: float

    :param tz: Value to assign to translateZ if given.
    :type tz: float

    :param rx: Value to assign to rotateX if given.
    :type rx: float

    :param ry: Value to assign to rotateY if given.
    :type ry: float

    :param rz: Value to assign to rotateZ if given.
    :type rz: float

    :param sx: Value to assign to scaleX if given.
    :type sx: float

    :param sy: Value to assign to scaleY if given.
    :type sy: float

    :param sz: Value to assign to scaleZ if given.
    :type sz: float

    :param jx: Value to assign to jointOrientX if given.
    :type jx: float

    :param jy: Value to assign to jointOrientY if given.
    :type jy: float

    :param jy: Value to assign to jointOrientY if given.
    :type jy: float

    :return: None
    """

    if tx and node.hasAttr('tx'):
        node.attr('tx').set(tx)

    if ty and node.hasAttr('ty'):
        node.attr('ty').set(ty)

    if tz and node.hasAttr('tz'):
        node.attr('tz').set(tz)

    if rx and node.hasAttr('rx'):
        node.attr('rx').set(rx)

    if ry and node.hasAttr('ry'):
        node.attr('ry').set(ry)

    if rz and node.hasAttr('rz'):
        node.attr('rz').set(rz)

    if sx and node.hasAttr('sx'):
        node.attr('sx').set(sx)

    if sy and node.hasAttr('sy'):
        node.attr('sy').set(sy)

    if sz and node.hasAttr('sz'):
        node.attr('sz').set(sz)

    if jx and node.hasAttr('jx'):
        node.attr('jointOrientX').set(jx)

    if jy and node.hasAttr('jy'):
        node.attr('jointOrientY').set(jy)

    if jz and node.hasAttr('jz'):
        node.attr('jointOrientZ').set(jz)
