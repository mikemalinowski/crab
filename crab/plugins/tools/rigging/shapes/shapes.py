import pymel.core as pm

import os
import json
import crab
from crab.vendor import qute


# ------------------------------------------------------------------------------
class StoreShapeTool(crab.RigTool):
    """
    Exposes the functionality to store a shape into the crab shape repository
    or to a given path
    """
    identifier = 'shape_io_store'
    display_name = 'Store Shape'
    icon = 'shapes.png'
    tooltips = dict(
        name='The name to store this shape under',
    )

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
    identifier = 'shape_io_apply'
    display_name = 'Apply Shape'
    icon = 'shapes.png'
    tooltips = dict(
        shapes='List of preset shapes that can be applied. You can alteratively make your own!',
    )

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
    identifier = 'shape_match_cvs'
    display_name = 'Mimic Shape CVs'
    icon = 'shapes.png'

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
    identifier = 'shape_rig_store'
    display_name = 'Store Rig Shapes To File'
    icon = 'shapes.png'

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
    identifier = 'shape_rig_load'
    display_name = 'Load Rig Shapes From File'
    icon = 'shapes.png'

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
