import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class ShapeSelectTool(crab.RigTool):

    identifier = 'shape_select'
    display_name = 'Select Shape'
    icon = 'shapes.png'

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

    identifier = 'shape_select_transforms'
    display_name = 'Select Shape Transforms'
    icon = 'shapes.png'

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

    identifier = 'shape_select_shapes_left'
    display_name = 'Select Shape: All Left'
    icon = 'shapes.png'

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

    identifier = 'shape_select_shapes_right'
    display_name = 'Select Shape: All Right'
    icon = 'shapes.png'

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