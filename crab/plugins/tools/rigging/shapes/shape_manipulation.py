import pymel.core as pm
import crab


# ------------------------------------------------------------------------------
class ShapeInvertXTool(crab.RigTool):

    identifier = 'shape_invert_shape_x'
    display_name = 'Invert Shape : X'
    icon = 'shapes.png'

    # --------------------------------------------------------------------------
    def run(self):
        invert_shapes(
            pm.selected(),
            [
                -1.0,
                1.0,
                1.0,
            ]
        )


# ------------------------------------------------------------------------------
class ShapeInvertYTool(crab.RigTool):

    identifier = 'shape_invert_shape_y'
    display_name = 'Invert Shape : Y'
    icon = 'shapes.png'

    # --------------------------------------------------------------------------
    def run(self):
        invert_shapes(
            pm.selected(),
            [
                1.0,
                -1.0,
                1.0,
            ]
        )


# ------------------------------------------------------------------------------
class ShapeInvertZTool(crab.RigTool):

    identifier = 'shape_invert_shape_z'
    display_name = 'Invert Shape : Z'
    icon = 'shapes.png'

    # --------------------------------------------------------------------------
    def run(self):
        invert_shapes(
            pm.selected(),
            [
                1.0,
                1.0,
                -1.0,
            ]
        )


# ------------------------------------------------------------------------------
class ShapeMirrorXTool(crab.RigTool):

    identifier = 'shape_mirror_x'
    display_name = 'Mirror Shape: X'
    icon = 'shapes.png'

    # --------------------------------------------------------------------------
    def run(self):
        if not pm.selected():
            return

        for source_node in pm.selected()[:]:

            target_node = None

            # -- Look for the object in the alternate side
            try:
                if crab.config.LEFT in source_node.name():
                    target_node = pm.PyNode(
                        source_node.name().replace(
                            crab.config.LEFT,
                            crab.config.RIGHT,
                        )
                    )

                else:
                    target_node = pm.PyNode(
                        source_node.name().replace(
                            crab.config.RIGHT,
                            crab.config.LEFT,
                        )
                    )

            except:
                print('%s does not have an alternate side' % source_node)

            # -- Read the shape data from the current side
            shape_data = crab.utils.shapes.read(source_node)

            # -- Clear the shapes on the other side
            if target_node.getShapes():
                pm.delete(target_node.getShapes())

            # -- Apply the shapes to that side
            crab.utils.shapes.apply(target_node, shape_data)

            # -- Invert the shape globally
            for source_shape, target_shape in zip(source_node.getShapes(), target_node.getShapes()):

                for idx in range(source_shape.numCVs()):

                    # -- Get the worldspace position of the current cv
                    source_pos = source_shape.getCV(
                        idx,
                        space='world',
                    )

                    # -- Set the position of the cv with the X axis
                    # -- inverted
                    target_shape.setCV(
                        idx,
                        [
                            source_pos[0] * -1,
                            source_pos[1],
                            source_pos[2],
                        ],
                        space='world',
                    )

                # -- Update teh curve to propagate the change
                target_shape.updateCurve()


# ------------------------------------------------------------------------------
class ShapeMirrorYTool(crab.RigTool):

    identifier = 'shape_mirror_y'
    display_name = 'Mirror Shape: Y'
    icon = 'shapes.png'

    # --------------------------------------------------------------------------
    def run(self):
        if not pm.selected():
            return

        for source_node in pm.selected()[:]:

            target_node = None

            # -- Look for the object in the alternate side
            try:
                if crab.config.LEFT in source_node.name():
                    target_node = pm.PyNode(
                        source_node.name().replace(
                            crab.config.LEFT,
                            crab.config.RIGHT,
                        )
                    )

                else:
                    target_node = pm.PyNode(
                        source_node.name().replace(
                            crab.config.RIGHT,
                            crab.config.LEFT,
                        )
                    )

            except:
                pass

            if not target_node:
                print('%s does not have an alternate side' % source_node)
                continue

            # -- Read the shape data from the current side
            shape_data = crab.utils.shapes.read(source_node)

            # -- Clear the shapes on the other side
            if target_node.getShapes():
                pm.delete(target_node.getShapes())

            # -- Apply the shapes to that side
            crab.utils.shapes.apply(target_node, shape_data)

            # -- Invert the shape globally
            for source_shape, target_shape in zip(source_node.getShapes(), target_node.getShapes()):

                for idx in range(source_shape.numCVs()):

                    # -- Get the worldspace position of the current cv
                    source_pos = source_shape.getCV(
                        idx,
                        space='world',
                    )

                    # -- Set the position of the cv with the X axis
                    # -- inverted
                    target_shape.setCV(
                        idx,
                        [
                            source_pos[0],
                            source_pos[1] * -1,
                            source_pos[2],
                        ],
                        space='world',
                    )

                # -- Update teh curve to propagate the change
                target_shape.updateCurve()


# ------------------------------------------------------------------------------
class ShapeMirrorZTool(crab.RigTool):

    identifier = 'shape_mirror_z'
    display_name = 'Mirror Shape: Z'
    icon = 'shapes.png'

    # --------------------------------------------------------------------------
    def run(self):
        if not pm.selected():
            return

        for source_node in pm.selected()[:]:

            target_node = None

            # -- Look for the object in the alternate side
            try:
                if crab.config.LEFT in source_node.name():
                    target_node = pm.PyNode(
                        source_node.name().replace(
                            crab.config.LEFT,
                            crab.config.RIGHT,
                        )
                    )

                else:
                    target_node = pm.PyNode(
                        source_node.name().replace(
                            crab.config.RIGHT,
                            crab.config.LEFT,
                        )
                    )

            except:
                print('%s does not have an alternate side' % source_node)

            # -- Read the shape data from the current side
            shape_data = crab.utils.shapes.read(source_node)

            # -- Clear the shapes on the other side
            if target_node.getShapes():
                pm.delete(target_node.getShapes())

            # -- Apply the shapes to that side
            crab.utils.shapes.apply(target_node, shape_data)

            # -- Invert the shape globally
            for source_shape, target_shape in zip(source_node.getShapes(), target_node.getShapes()):

                for idx in range(source_shape.numCVs()):

                    # -- Get the worldspace position of the current cv
                    source_pos = source_shape.getCV(
                        idx,
                        space='world',
                    )

                    # -- Set the position of the cv with the X axis
                    # -- inverted
                    target_shape.setCV(
                        idx,
                        [
                            source_pos[0],
                            source_pos[1],
                            source_pos[2] * -1,
                        ],
                        space='world',
                    )

                # -- Update teh curve to propagate the change
                target_shape.updateCurve()


# ------------------------------------------------------------------------------
class ShapeMirrorLeftToRightTool(crab.RigTool):
    """
    Most crab components are always built from left to right. This is a
    convenience tool to mirror all the left sided shapes over to the rightss
    side.
    """

    identifier = 'shape_mirror_left_to_right'
    display_name = 'Mirror Shape Left to Right'
    icon = 'shapes.png'
    tooltips = dict(
        axis='Which axis should we mirror across (from positive to negative)',
    )

    # --------------------------------------------------------------------------
    def __init__(self):
        super(ShapeMirrorLeftToRightTool, self).__init__()
        self.options.axis = 'X' if pm.upAxis(q=True, axis=True).upper() == 'Y' else 'Y'
        self.options.selection_only = False

    # --------------------------------------------------------------------------
    def run(self):

        # -- Get the Shape mirroring tool that matches
        # -- our axis as defined in the options
        tool = crab.tools.rigging().request('shape_mirror_%s' % self.options.axis.lower())

        # -- Select the left controls using crabs naming conventions
        if self.options.selection_only:

            # -- If we're running on selection only, then we dont need to manage
            # -- the selection
            pass

        else:
            pm.select(
                [
                    control
                    for control in pm.ls('%s_*_%s' % (crab.config.CONTROL, crab.config.LEFT), type='transform')
                    if control.getShapes()
                ]
            )

        # -- Run the tool
        tool().run()


# ------------------------------------------------------------------------------
def invert_shapes(nodes, inversion_axis):

    for node in nodes:

        if isinstance(node, pm.nt.NurbsCurve):
            invert_shape(node, inversion_axis)
            continue

        for shape in node.getShapes():
            invert_shape(shape, inversion_axis)


# ------------------------------------------------------------------------------
def invert_shape(shape, inversion_axis):
    for idx, pos in enumerate(shape.getCVs()):

        shape.setCV(
            idx,
            [
                pos[0] * inversion_axis[0],
                pos[1] * inversion_axis[1],
                pos[2] * inversion_axis[2],
            ],
        )
        shape.updateCurve()
