import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
class ShapeSelectTool(crab.RigTool):

    identifier = "shape_select"
    display_name = "Select Shape"
    icon = "shapes.png"

    # ----------------------------------------------------------------------------------
    def run(self):

        shapes = list()

        for node in pm.selected():
            if isinstance(node, pm.nt.NurbsCurve):
                shapes.append(node)
                continue

            shapes.extend(node.getShapes())

        pm.select(shapes)


# --------------------------------------------------------------------------------------
class ShapeSelectTransformsTool(crab.RigTool):

    identifier = "shape_select_transforms"
    display_name = "Select Shape: Transforms"
    icon = "shapes.png"

    # ----------------------------------------------------------------------------------
    def run(self):

        transforms = list()

        for node in pm.selected():
            if isinstance(node, pm.nt.NurbsCurve):
                transforms.append(node.getParent())
                continue

            transforms.extend(node)

        pm.select(transforms)


# --------------------------------------------------------------------------------------
class ShapeSelectLeftTool(crab.RigTool):

    identifier = "shape_select_shapes_left"
    display_name = "Select Shape: All Left"
    icon = "shapes.png"

    # ----------------------------------------------------------------------------------
    def run(self):

        shapes = list()

        for node in pm.ls("%s_*_%s" % (crab.config.CONTROL, crab.config.LEFT)):
            if isinstance(node, pm.nt.NurbsCurve):
                shapes.append(node)
                continue

            shapes.extend(node.getShapes())

        pm.select(shapes)


# --------------------------------------------------------------------------------------
class ShapeSelectRightTool(crab.RigTool):

    identifier = "shape_select_shapes_right"
    display_name = "Select Shape: All Right"
    icon = "shapes.png"

    # ----------------------------------------------------------------------------------
    def run(self):

        shapes = list()

        for node in pm.ls(
                "%s_*_%s" % (crab.config.CONTROL, crab.config.RIGHT)):
            if isinstance(node, pm.nt.NurbsCurve):
                shapes.append(node)
                continue

            shapes.extend(node.getShapes())

        pm.select(shapes)


# --------------------------------------------------------------------------------------
class ScaleShapeTool(crab.RigTool):

    identifier = "shape_scale"
    display_name = "Scale Shapes"
    icon = "shapes.png"

    # ----------------------------------------------------------------------------------
    def __init__(self):
        super(ScaleShapeTool, self).__init__()

        self.options.wildcard = crab.config.CONTROL + "*"
        self.options.scale_by = 1.0
        self.options.selection_only = False

    # ----------------------------------------------------------------------------------
    def run(self):

        if self.options.selection_only:
            nodes = pm.selected()

        else:
            nodes = pm.ls(self.options.wildcard, type="transform")

        for node in nodes:

            # -- If there are no curve shapes on this node, skip it
            if not node.getShape():
                continue

            for shape in node.getShapes():

                # -- If it is not a nurbs curve, skip it
                if not isinstance(shape, pm.nt.NurbsCurve):
                    continue

                for idx in range(shape.numCVs()):
                    # -- Match the worldspace cv positions
                    shape.setCV(
                        idx,
                        shape.getCV(idx) * self.options.scale_by,
                        )

                shape.updateCurve()
