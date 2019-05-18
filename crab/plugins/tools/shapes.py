import pymel.core as pm

import crab


# ------------------------------------------------------------------------------
class ShapeInvertXTool(crab.RigTool):

    identifier = 'Shape : Invert : X'

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

    identifier = 'Shape : Invert : Y'

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

    identifier = 'Shape : Invert : Z'

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
class ShapeSelectTool(crab.RigTool):

    identifier = 'Shape : Select'

    # ------------------------------------------------------------- -------------
    def run(self):

        shapes = list()

        for node in pm.selected():
            if isinstance(node, pm.nt.NurbsCurve):
                shapes.append(node)
                continue

            shapes.extend(node.getShapes())

        pm.select(shapes)


# ------------------------------------------------------------------------------
class ShapeSelectTransformsTool(crab.RigTool):

    identifier = 'Shape : Select : Transforms'

    # --------------------------------------------------------------------------
    def run(self):

        transforms = list()

        for node in pm.selected():
            if isinstance(node, pm.nt.NurbsCurve):
                transforms.append(node.getParent())
                continue

            transforms.extend(node)

        pm.select(transforms)


# ------------------------------------------------------------------------------
class ShapeSelectLeftTool(crab.RigTool):

    identifier = 'Shape : Select : All Left'

    # --------------------------------------------------------------------------
    def run(self):

        shapes = list()

        for node in pm.ls('%s_*_%s' % (crab.config.CONTROL, crab.config.LEFT)):
            if isinstance(node, pm.nt.NurbsCurve):
                shapes.append(node)
                continue

            shapes.extend(node.getShapes())

        pm.select(shapes)


# ------------------------------------------------------------------------------
class ShapeSelectRightTool(crab.RigTool):

    identifier = 'Shape : Select : All Right'

    # --------------------------------------------------------------------------
    def run(self):

        shapes = list()

        for node in pm.ls(
                '%s_*_%s' % (crab.config.CONTROL, crab.config.RIGHT)):
            if isinstance(node, pm.nt.NurbsCurve):
                shapes.append(node)
                continue

            shapes.extend(node.getShapes())

        pm.select(shapes)


# ------------------------------------------------------------------------------
class ShapeMirrorTool(crab.RigTool):

    identifier = 'Shape : Mirror : X'

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
            shape_data = crab.utils.shapeio.read(source_node)

            # -- Clear the shapes on the other side
            if target_node.getShapes():
                pm.delete(target_node.getShapes())

            # -- Apply the shapes to that side
            crab.utils.shapeio.apply(target_node, shape_data)

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
