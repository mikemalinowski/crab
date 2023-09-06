import pymel.core as pm

from .basics import generic
from .. import config


# --------------------------------------------------------------------------------------
def guide(
    description,
    side,
    parent=None,
    xform=None,
    translation_offset=None,
    rotation_offset=None,
    match_to=None,
    link_to=None,
    shape=None,
):
    """
    Creates a control structure - which is a structure which conforms to the
    following hierarchy:

        ORG -> ZRO -> OFF -> CTL

    :param description: Descriptive section of the name
    :type description: str

    :param side: Tag for the location to be used during the name generation
    :type side: str

    :param parent: Optional parent to assign to the node
    :type parent: pm.nt.DagNode

    :param xform: Optional worldSpace matrix to apply to the object
    :type xform: pm.dt.Matrix

    :param translation_offset: Optional local space translation offset to be
        applied to the guide
    :type translation_offset: pm.nt.Vector

    :param rotation_offset: Optional local space rotation offset to be
        applied to the guide
    :type rotation_offset: pm.nt.Vector

    :param match_to: Optional node to match in worldspace
    :type match_to: pm.nt.DagNode

    :param shape: Optional shape to apply to the node
    :type shape: name of shape or path

    :param link_to: If given, an unselectable line is drawn between this
        guide control and the given transform.
    :type link_to: pm.nt.DagNode

    :return: pm.nt.DependNode
    """
    guide_node = generic(
        "transform",
        config.GUIDE,
        description,
        side,
        shape=shape or "cube",
        parent=parent,
        xform=xform,
        match_to=match_to or parent,
    )

    if link_to:
        curve = pm.curve(
            d=1,
            p=[
                [0, 0, 0],
                [0, 0, 0],
            ],
        )

        # -- Make the curve unselectable
        curve.getShape().template.set(True)

        # -- Create the first cluster
        pm.select("%s.cv[0]" % curve.name())
        cls_root_handle, cls_root_xfo = pm.cluster()

        # -- Create the second cluster
        pm.select("%s.cv[1]" % curve.name())
        cls_target_handle, cls_target_xfo = pm.cluster()

        # -- Hide the clusters, as we do not want them
        # -- to be interactable
        cls_root_xfo.visibility.set(False)
        cls_target_xfo.visibility.set(False)

        # -- Ensure they"re both children of the guide
        cls_root_xfo.setParent(guide_node)
        cls_target_xfo.setParent(guide_node)

        # -- Ensure the target is zero"d
        cls_target_xfo.setMatrix(pm.dt.Matrix())

        # -- Constrain the root to the linked object
        pm.parentConstraint(
            link_to,
            cls_root_xfo,
            maintainOffset=False,
        )

    # -- Set the guide specific colouring
    guide_node.useOutlinerColor.set(True)
    guide_node.outlinerColorR.set(config.GUIDE_COLOR[0] * (1.0 / 255))
    guide_node.outlinerColorG.set(config.GUIDE_COLOR[1] * (1.0 / 255))
    guide_node.outlinerColorB.set(config.GUIDE_COLOR[2] * (1.0 / 255))

    for guide_shape in guide_node.getShapes():
        # -- Set the display colour
        guide_shape.overrideEnabled.set(True)
        guide_shape.overrideRGBColors.set(True)

        guide_shape.overrideColorR.set(config.GUIDE_COLOR[0] * (1.0 / 255))
        guide_shape.overrideColorG.set(config.GUIDE_COLOR[1] * (1.0 / 255))
        guide_shape.overrideColorB.set(config.GUIDE_COLOR[2] * (1.0 / 255))

    if translation_offset:
        guide_node.setTranslation(
            translation_offset,
            worldSpace=False,
        )

    if rotation_offset:
        guide_node.setRotation(
            rotation_offset,
            worldSpace=False,
        )

    return guide_node
