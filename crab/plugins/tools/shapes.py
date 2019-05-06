import crab
import pymel.core as pm


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

    # --------------------------------------------------------------------------
    def run(self):

        shapes = list()

        for node in pm.selected():
            if isinstance(node, pm.nt.NurbsCurve):
                shapes.append(node)
                continue

            shapes.extend(node.getShapes())

        pm.select(shapes)


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
