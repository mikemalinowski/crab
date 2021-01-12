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
    """
    This will aim the first object at the second object. You can also provide
    an upvector along with whether the aim and upvector should be flipped.

    This is the equivalent of using an aimConstraint + delete operation.
    """
    identifier = 'Transforms : Aim At'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(ObjectAimTool, self).__init__()

        self.options.aim_this = ''
        self.options.at_this = ''
        self.options.up_target = ''
        self.options.flip_aim = False
        self.options.flip_up = False

    # --------------------------------------------------------------------------
    def run(self, aim_this=None, at_this=None, up_target=None, flip_aim=False, flip_up=False):

        aim_this = aim_this or self.options.aim_this
        at_this = at_this or self.options.at_this
        up_target = up_target or self.options.up_target

        selection_list = pm.ls(sl=True)
        if len(selection_list) == 2:
            aim_this = selection_list[0]
            at_this = selection_list[1]
        elif len(selection_list) == 3:
            aim_this = selection_list[0]
            at_this = selection_list[1]
            up_target = selection_list[2]

        flip_aim = flip_aim or self.options.flip_aim
        flip_up = flip_up or self.options.flip_up

        if flip_aim:
            aim_vector = (-1, 0, 0)
        else:
            aim_vector = (1, 0, 0)

        if flip_up:
            up_vector = (0, 0, -1)
        else:
            up_vector = (0, 0, 1)

        scene_up = "scene"
        object_up = "object"

        if up_target:
            # aim with up target as upvector
            temp_constraint = pm.aimConstraint(
                at_this,
                aim_this,
                aimVector=aim_vector,
                upVector=up_vector,
                worldUpType=object_up,
                worldUpObject=up_target,
            )
        else:
            # aim with assumed scene as upvector
            temp_constraint = pm.aimConstraint(
                at_this,
                aim_this,
                aimVector=aim_vector,
                upVector=up_vector,
                worldUpType=scene_up,
            )
        pm.delete(temp_constraint)


# ------------------------------------------------------------------------------
class MoveChildBoneTool(crab.RigTool):

    identifier = 'Transforms : Move Child Bone'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(MoveChildBoneTool, self).__init__()

        self.options.child_bone = ''
        self.options.target = ''

    # --------------------------------------------------------------------------
    def run(self, child_bone=None, target=None):

        # -- Take the given variables as a priority. If they are
        # -- not given we use the options, and if they are also
        # -- not given then we take the current selection
        child_bone = child_bone or self.options.child_bone or pm.selected()[0]
        parent_bone = child_bone.getParent()
        target = target or self.options.target or pm.selected()[1]

        if parent_bone:
            cns = pm.aimConstraint(
                target,
                parent_bone,
                offset=[0, 0, 0],
                weight=1,
                aimVector=[1, 0, 0],
                upVector=[0, 0, 1],
                worldUpType="vector",
                worldUpVector=[0, 1, 0],
            )
            mat4 = parent_bone.getMatrix()
            pm.delete(cns)
            parent_bone.setMatrix(mat4)

        child_bone.setTranslation(
            target.getTranslation(worldspace=True),
            worldSpace=True,
        )


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


