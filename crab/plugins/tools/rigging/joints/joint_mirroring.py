import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class MirrorJointsAcrossTool(crab.RigTool):

    identifier = 'joints_mirror_across'
    display_name = 'Mirror Across'
    icon = 'joints.png'
    tooltips = dict(
        mirror_plane='What world axis should the mirror happen across',
        translation_only='If true then rotation mirroring will not be performed',
    )

    # --------------------------------------------------------------------------
    def __init__(self):
        super(MirrorJointsAcrossTool, self).__init__()

        self.options.mirror_plane = ['XZ', 'XY', 'YZ']
        self.options.translation_only = False

    # --------------------------------------------------------------------------
    def run(self):
        crab.utils.maths.global_mirror(
            pm.selected(),
            across=self.options.mirror_plane or None,
            remap=MirrorJointsAcrossTool.remap,
            translation_only=self.options.translation_only,
        )

    # --------------------------------------------------------------------------
    @classmethod
    def remap(cls, node):
        if '_' + crab.config.LEFT in node.name():
            return pm.PyNode(
                node.name().replace(
                    '_' + crab.config.LEFT,
                    '_' + crab.config.RIGHT,
                )
            )

        else:
            return pm.PyNode(
                node.name().replace(
                    '_' + crab.config.RIGHT,
                    '_' + crab.config.LEFT,
                )
            )


# ------------------------------------------------------------------------------
class MirrorFaceJointsAcrossTool(crab.RigTool):

    identifier = 'joints_mirror_face_joints'
    display_name = 'Mirror Face Joints'
    icon = 'joints.png'
    tooltips = dict(
        mirror_translation='If False then only rotation will be mirrored',
        mirror_rotation='If False then only translation will be mirrored',
    )

    # --------------------------------------------------------------------------
    def __init__(self):
        super(MirrorFaceJointsAcrossTool, self).__init__()

        self.options.mirror_translation = True
        self.options.mirror_rotation = True

    # --------------------------------------------------------------------------
    def run(self):

        selection_list = pm.selected()
        for current_item in selection_list:

            if current_item.nodeType() != 'joint':
                continue

            opposite_item = self.remap(current_item)
            if opposite_item:
                if self.options.mirror_translation:
                    opposite_item.translateX.set(current_item.translateX.get())
                    opposite_item.translateY.set(-1 * current_item.translateY.get())
                    opposite_item.translateZ.set(current_item.translateZ.get())
                if self.options.mirror_rotation:
                    opposite_item.rotateX.set(current_item.rotateX.get())
                    opposite_item.rotateY.set(-1 * current_item.rotateY.get())
                    opposite_item.rotateZ.set(-1 * current_item.rotateZ.get())
                    opposite_item.rotateZ.set(180 + opposite_item.rotateZ.get())

    # --------------------------------------------------------------------------
    @classmethod
    def remap(cls, node):
        if crab.config.LEFT in node.name():
            return pm.PyNode(
                node.name().replace(
                    crab.config.LEFT,
                    crab.config.RIGHT,
                )
            )
        elif crab.config.RIGHT in node.name():
            return pm.PyNode(
                node.name().replace(
                    crab.config.RIGHT,
                    crab.config.LEFT,
                )
            )
        else:
            return None


# ------------------------------------------------------------------------------
class MirrorJointsTool(crab.RigTool):

    identifier = 'joints_mirror'
    display_name = 'Mirror'
    icon = 'joints.png'

    tooltips = dict(
        mirror_plane='What world axis should the mirror happen across',
    )

    # --------------------------------------------------------------------------
    def __init__(self):
        super(MirrorJointsTool, self).__init__()

        self.options.mirror_plane = ['XZ', 'XY', 'YZ']

    # --------------------------------------------------------------------------
    def run(self):
        crab.utils.maths.global_mirror(
            pm.selected(),
            across=self.options.mirror_plane or None,
        )
