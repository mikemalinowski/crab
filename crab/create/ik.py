# import itertools
import pymel.core as pm
#

# from . import basics
# from . import controls
# from .. import utils
from .. import config
#

def _generate_ik(start, end, description, side, parent=None, visible=False, solver='ikRPsolver', polevector=None, **kwargs):
    """
    Private function to generate the ik, returning the result from the ik handle call

    :param start:
    :param end:
    :param description:
    :param side:
    :param parent:
    :param visible:
    :param solver:
    :param polevector:
    :param kwargs:
    :return:
    """
    # -- Hook up the Ik Handle
    result = pm.ikHandle(
        startJoint=start,
        endEffector=end,
        solver=solver,
        priority=1,
        autoPriority=False,
        enableHandles=True,
        snapHandleToEffector=True,
        sticky=False,
        weight=1,
        positionWeight=1,
        **kwargs
    )

    ikh = result[0]

    ikh.visibility.set(visible)

    ikh.rename(
        config.name(
            prefix='IKH',
            description=description,
            side=side,
        ),
    )

    if parent:
        ikh.setParent(parent)

    if polevector:
        pm.poleVectorConstraint(
            polevector,
            ikh,
        )

    return result

# ------------------------------------------------------------------------------
def simple_ik(start, end, description, side, parent=None, visible=False, solver='ikRPsolver', polevector=None, **kwargs):
    """
    This is a convenience function for generating an IK handle
    and having it named.

    :param start:
    :param end:
    :param description:
    :param side:
    :param parent:
    :param visible:
    :param solver:
    :param polevector:
    :param kwargs:

    :return: ikHandle
    """
    # -- Hook up the Ik Handle
    result = _generate_ik(
        start=start,
        end=end,
        description=description,
        side=side,
        parent=parent,
        visible=visible,
        solver=solver,
        polevector=polevector,
        **kwargs
    )

    # -- Return the IK Handle
    return result[0]


# ------------------------------------------------------------------------------
def spline_ik(start, end, description, side, parent=None, visible=False, polevector=None, **kwargs):
    """
    This is a convenience function for generating an IK handle
    and having it named.

    :param start:
    :param end:
    :param description:
    :param side:
    :param parent:
    :param visible:
    :param polevector:
    :param kwargs:

    :return: [ikHandle, curve]
    """
    # -- Hook up the Ik Handle
    result = _generate_ik(
        start=start,
        end=end,
        description=description,
        side=side,
        parent=None,
        visible=False,
        solver='ikSplineSolver',
        polevector=None,
        **kwargs
    )

    # -- Return the IK Handle
    return result[0], result[-1]
