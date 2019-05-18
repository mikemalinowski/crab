import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class DefineAPoseTool(crab.RigTool):

    identifier = 'Poses : Define A Pose'
    POSE_NAME = 'APose'

    # --------------------------------------------------------------------------
    def run(self):
        for joint in pm.ls('%s_*' % crab.config.SKELETON):
            if not joint.hasAttr(self.POSE_NAME):
                joint.addAttr(self.POSE_NAME, at='matrix')
            joint.attr(self.POSE_NAME).set(joint.getMatrix())


# ------------------------------------------------------------------------------
class ApplyAPoseTool(crab.RigTool):
    identifier = 'Poses : Apply A Pose'
    POSE_NAME = 'APose'

    # --------------------------------------------------------------------------
    def run(self):
        for joint in pm.ls('%s_*' % crab.config.SKELETON):
            if joint.hasAttr(self.POSE_NAME):
                joint.setMatrix(joint.attr(self.POSE_NAME).get())


# ------------------------------------------------------------------------------
class DefineTPoseTool(DefineAPoseTool):
    identifier = 'Poses : Define T Pose'
    POSE_NAME = 'TPose'


# ------------------------------------------------------------------------------
class ApplyTPoseTool(ApplyAPoseTool):
    identifier = 'Poses : Apply T Pose'
    POSE_NAME = 'TPose'
