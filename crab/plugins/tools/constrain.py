import crab

import pymel.core as pm


# ------------------------------------------------------------------------------
class ZeroWSRotationsTool(crab.RigTool):

    identifier = 'Transforms : Zero WS Transforms'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(ZeroWSRotationsTool, self).__init__()

    # --------------------------------------------------------------------------
    def run(self, these_nodes=None):

        # -- Take the given variables as a priority. If they are
        # -- not given we use the options, and if they are also
        # -- not given then we take the current selection
        these_nodes = these_nodes or pm.selected()

        for node in these_nodes:
            node.setRotation(
                pm.dt.Quaternion(),
                worldSpace=True,
            )


# ------------------------------------------------------------------------------
class ObjectAimTool(crab.RigTool):

    identifier = 'Transforms : Aim At'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(ObjectAimTool, self).__init__()

        self.options.aim_this = ''
        self.options.at_this = ''

    # --------------------------------------------------------------------------
    def run(self, aim_this=None, at_this=None):

        # -- Take the given variables as a priority. If they are
        # -- not given we use the options, and if they are also
        # -- not given then we take the current selection
        aim_this = aim_this or self.options.aim_this or pm.selected()[0]
        at_this = at_this or self.options.at_this or pm.selected()[1]

        cns = pm.aimConstraint(
            at_this,
            aim_this,
            offset=[0, 0, 0],
            weight=1,
            aimVector=[1, 0, 0],
            upVector=[0, 0, 1],
            worldUpType="vector",
            worldUpVector=[0, 1, 0],
        )
        mat4 = aim_this.getMatrix()
        pm.delete(cns)
        aim_this.setMatrix(mat4)


# ------------------------------------------------------------------------------
class FollicleTool(crab.RigTool):

    identifier = 'Transforms : Create Follicle'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(FollicleTool, self).__init__()

        self.options.parent = ''
        self.options.surface = ''
        self.options.drive = ''
        self.options.description = ''
        self.options.side = ['MD', 'RT', 'LF']

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def run(self, parent=None, surface=None, drive=None):

        if not parent and pm.objExists(self.options.parent):
            parent = pm.PyNode(self.options.parent)

        if not surface and pm.objExists(self.options.surface):
            surface = pm.PyNode(self.options.surface)

        if not surface and pm.selected():
            surface = pm.selected()[0]

        if not drive and pm.objExists(self.options.drive):
            drive = pm.PyNode(self.options.drive)

        # -- Drive is optional
        if self.options.drive:
            drive = pm.PyNode(self.options.drive)

        # -- If we have the transform then we need to get the
        # -- shape
        if isinstance(surface, pm.nt.Transform):
            surface = surface.getShape()

        # -- We need to test whether the surface is a mesh or not
        is_mesh = False

        if isinstance(surface, pm.nt.Mesh):
            is_mesh = True

        follicle = crab.create.generic(
            node_type='follicle',
            prefix=crab.config.MECHANICAL,
            description=self.options.description,
            side=self.options.side,
            parent=parent,
            find_transform=True,
        )
        follicle = follicle.getShape()

        if is_mesh:
            surface.attr('outMesh').connect(follicle.inputMesh)

        else:
            surface.attr('local').connect(follicle.inputSurface)

        surface.attr('worldMatrix[0]').connect(follicle.inputWorldMatrix)

        follicle.outTranslate.connect(follicle.getParent().translate)
        follicle.outRotate.connect(follicle.getParent().rotate)

        if drive:

            # -- Set the UV positions
            if is_mesh:
                u, v = surface.getUVAtPoint(
                    drive.getTranslation(space='world'),
                    space='world',
                )

            else:
                _, u, v = surface.closestPoint(
                    drive.getTranslation(space='world'),
                    space='world',
                )

            follicle.attr('parameterU').set(u)
            follicle.attr('parameterV').set(v)

            pm.parentConstraint(
                follicle.getParent(),
                drive,
                maintainOffset=True,
            )


# ------------------------------------------------------------------------------
class CopyTransformValue(crab.RigTool):

    identifier = 'Transforms : Copy Values'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(CopyTransformValue, self).__init__()

        self.options.copy_from_this = ''
        self.options.copy_to_this = ''
        self.options.mirror_plane = ['None', 'XZ', 'XY', 'YZ']

    # --------------------------------------------------------------------------
    def run(self):

        copy_from_this = self.options.copy_from_this or pm.selected()[0]
        copy_to_this = self.options.copy_to_this or pm.selected()[1]
        transform_attributes = [
            'translateX',
            'translateY',
            'translateZ',
            'rotateX',
            'rotateY',
            'rotateZ',
            'scaleX',
            'scaleY',
            'scaleZ',
        ]
        mirror_values_look_up = {
            'None': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'XZ': [1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0],
            'XY': [1.0, 1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0],
            'YZ': [-1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
        }
        mirror_values_list = mirror_values_look_up[self.options.mirror_plane]

        with crab.utils.contexts.UndoChunk():
            for attribute, multiplier in zip(transform_attributes, mirror_values_list):
                copy_to_this.attr(attribute).unlock()
                copy_to_this.attr(attribute).set(
                    copy_from_this.attr(attribute).get() * multiplier
                )


