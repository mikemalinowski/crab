import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class DefineAPoseTool(crab.RigTool):

    identifier = 'Poses : Define A Pose'
    POSE_NAME = 'APose'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(DefineAPoseTool, self).__init__()
        self.options.selection_only = False

    # --------------------------------------------------------------------------
    def run(self):

        if self.options.selection_only:
            nodes = pm.selected()

        else:
            nodes = pm.ls('%s_*' % crab.config.SKELETON, type='joint')
            nodes.extend(pm.ls('%s_*' % crab.config.GUIDE, type='transform'))

        with crab.utils.contexts.UndoChunk():
            for joint in nodes:
                if not joint.hasAttr(self.POSE_NAME):
                    joint.addAttr(self.POSE_NAME, at='matrix')
                joint.attr(self.POSE_NAME).set(joint.getMatrix())


# ------------------------------------------------------------------------------
class ApplyAPoseTool(crab.RigTool):
    identifier = 'Poses : Apply A Pose'
    POSE_NAME = 'APose'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(ApplyAPoseTool, self).__init__()
        self.options.selection_only = False
        self.options.rotate_only = False

    # --------------------------------------------------------------------------
    def run(self):
        if self.options.selection_only:
            nodes = pm.selected()

        else:
            nodes = pm.ls('%s_*' % crab.config.SKELETON, type='joint')
            nodes.extend(pm.ls('%s_*' % crab.config.GUIDE, type='transform'))

        with crab.utils.contexts.UndoChunk():
            for joint in nodes:
                if joint.hasAttr(self.POSE_NAME):

                    pos = None
                    if self.options.rotate_only:
                        pos = joint.getTranslation()

                    joint.setMatrix(joint.attr(self.POSE_NAME).get())

                    if pos:
                        joint.setTranslation(pos)


# ------------------------------------------------------------------------------
class DefineTPoseTool(DefineAPoseTool):
    identifier = 'Poses : Define T Pose'
    POSE_NAME = 'TPose'


# ------------------------------------------------------------------------------
class ApplyTPoseTool(ApplyAPoseTool):
    identifier = 'Poses : Apply T Pose'
    POSE_NAME = 'TPose'
