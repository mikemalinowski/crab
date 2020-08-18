import pymel.core as pm

import os
import json
import crab
from crab.vendor import qute


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
class ShapeMirrorXTool(crab.RigTool):

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

    identifier = 'Shape : Mirror : Y'

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

    identifier = 'Shape : Mirror : Z'

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
    convenience tool to mirror all the left sided shapes over to the right
    side.
    """
    identifier = 'Shape : Mirror Left to Right'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(ShapeMirrorLeftToRightTool, self).__init__()
        self.options.axis = 'Y'

    # --------------------------------------------------------------------------
    def run(self):

        # -- Get the Shape mirroring tool that matches
        # -- our axis as defined in the options
        tool = crab.tools.rigging().request('Shape : Mirror : %s' % self.options.axis.upper())

        # -- Select the left controls using crabs naming conventions
        pm.select(
            [
                control
                for control in pm.ls('%s_*_%s' % (crab.config.CONTROL, crab.config.LEFT), type='transform')
                if control.getShapes()
            ]
        )
        tool().run()


# ------------------------------------------------------------------------------
class StoreShapeTool(crab.RigTool):
    """
    Exposes the functionality to store a shape into the crab shape repository
    or to a given path
    """
    identifier = 'Shape IO : Store'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(StoreShapeTool, self).__init__()
        self.options.name = ''

    # --------------------------------------------------------------------------
    def run(self, node=None):

        save_path = os.path.join(
            os.path.dirname(crab.__file__),
            'shapes',
            '%s.json' % self.options.name,
        )

        crab.utils.shapes.write(
            node or pm.selected()[0],
            save_path,
        )


# ------------------------------------------------------------------------------
class ApplyShapeTool(crab.RigTool):
    """
    Exposes the functionality to store a shape into the crab shape repository
    or to a given path
    """
    identifier = 'Shape IO : Apply'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(ApplyShapeTool, self).__init__()
        self.options.shapes = [
            os.path.basename(path).replace('.json', '')
            for path in crab.utils.shapes.shapes()
        ]

    # --------------------------------------------------------------------------
    def run(self, node=None, shape_name=None):

        if not node:
            node = pm.selected()

        if not isinstance(node, list):
            node = [node]

        for single_node in node:
            crab.utils.shapes.apply(
                single_node,
                shape_name or self.options.shapes
            )


# ------------------------------------------------------------------------------
class MatchCVsTool(crab.RigTool):
    """
    Matches the cvs (in worldspace) between two curves, providing they have
    the same cv count
    """
    identifier = 'Shape : Match CVs'

    # --------------------------------------------------------------------------
    def run(self, source=None, target=None):

        source = source or pm.selected()[0]
        target = target or pm.selected()[1]

        if isinstance(source, pm.nt.Transform):
            source = source.getShape()

        if isinstance(target, pm.nt.Transform):
            target = target.getShape()

        # -- We now need to match the cv positions of our curves
        # -- against the guide cv's
        if source.numCVs() != target.numCVs():
            raise Exception(
                'Source curve has {} cvs but the target curve has {}.'.format(
                    source.numCVs(),
                    target.numCVs(),
                ),
            )

        # -- Cycle the cvs and match their position
        for idx in range(source.numCVs()):

            # -- Match the worldspace cv positions
            target.setCV(
                idx,
                source.getCV(idx, space='world'),
                space='world',
            )

        target.updateCurve()

# ------------------------------------------------------------------------------
class StoreRigShapeData(crab.RigTool):
    """
    This tool allows for all the shape data in a rig to be written out
    to a json file to allow it to be transferred to other rigs/scenes
    """
    identifier = 'Shape : Data : Store'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(StoreRigShapeData, self).__init__()

    # --------------------------------------------------------------------------
    def run(self, filepath=None, rig_node=None, silent=False):

        # -- If we're not given a file path we need to ask for one
        if not filepath:
            filepath = qute.quick.getFilepath(
                save=True,
                title='Save Rig Shape Data',
            )

        # -- If no filepath was given (either through code or through
        # -- qute) we have nothing more to do
        if not filepath:
            return

        # -- Get the shape info attribute
        if rig_node:
            attr = rig_node.attr('shapeInfo')

        else:
            # -- In this scenario we need to find the shape info attribute
            # -- but as crab has a one-editable-rig-per-scene rule we can
            # -- make an assumption about it
            possibilities = pm.ls(
                '*.shapeInfo',
                r=True,
            )

            # -- If no rigs were found prompt the user - unless we're
            # -- running silently
            if not possibilities:
                if not silent:
                    qute.quick.confirm(
                        'Shape Save Error',
                        'No shape info attribute could be found'
                    )
                return False

            attr = possibilities[0]

        # -- Write the file out to disk
        with open(filepath, 'w') as f:
            json.dump(
                json.loads(attr.get()),
                f,
                sort_keys=True,
                indent=4,
            )


# ------------------------------------------------------------------------------
class LoadRigShapeData(crab.RigTool):
    """
    This tool allows for shape data to be loaded from a json file and
    applied to the rig.
    """
    identifier = 'Shape : Data : Load'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(LoadRigShapeData, self).__init__()

    # --------------------------------------------------------------------------
    def run(self, filepath=None, rig_node=None, silent=False):

        # -- If we're not given a file path we need to ask for one
        if not filepath:
            filepath = qute.quick.getFilepath(
                save=False,
                title='Save Rig Shape Data',
                filter_='*.json'
            )

        # -- If no filepath was given (either through code or through
        # -- qute) we have nothing more to do
        if not filepath:
            return

        # -- Get the shape info attribute
        if rig_node:
            attr = rig_node.attr('shapeInfo')

        else:
            # -- In this scenario we need to find the shape info attribute
            # -- but as crab has a one-editable-rig-per-scene rule we can
            # -- make an assumption about it
            possibilities = pm.ls(
                '*.shapeInfo',
                r=True,
            )

            # -- If no rigs were found prompt the user - unless we're
            # -- running silently
            if not possibilities:
                if not silent:
                    qute.quick.confirm(
                        'Shape Save Error',
                        'No shape info attribute could be found'
                    )
                return False

            attr = possibilities[0]

        # -- Put the rig into edit mode - this means we will
        # -- overwrite the currently existing shape store information
        rig = crab.Rig(attr.node())
        rig.edit()

        # -- Now write the new shape data into the rig
        with open(filepath, 'r') as f:

            # -- Convert the json to a flat structure
            attr.set(json.dumps(json.load(f)))

        # -- Trigger a rig build
        rig.build()

        return True


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
