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

        selection_state_text = 'all joints'

        confirm_result = 'Yes'
        if self.options.selection_only:
            nodes = pm.selected()
            selection_state_text = 'selected joints'

        else:
            confirm_result = pm.confirmDialog(
                title='Confirm',
                message='This will replace the entire {}, Are you sure?'.format(self.POSE_NAME),
                button=['Yes', 'No'],
                defaultButton='Yes',
                cancelButton='No',
                dismissString='No'
            )
            nodes = pm.ls('%s_*' % crab.config.SKELETON, type='joint')
            nodes.extend(pm.ls('%s_*' % crab.config.GUIDE, type='transform'))

        if confirm_result == 'Yes':
            with crab.utils.contexts.UndoChunk():
                for joint in nodes:
                    if not joint.hasAttr(self.POSE_NAME):
                        joint.addAttr(self.POSE_NAME, at='matrix')
                    joint.attr(self.POSE_NAME).set(joint.getMatrix())
            print ('Updated: {} on {}'.format(self.POSE_NAME, selection_state_text)),
        else:
            print ('Action Cancelled: {}'.format(self.POSE_NAME)),


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
        selection_state_text = 'all joints'
        rotation_only_text = ''
        if self.options.selection_only:
            nodes = pm.selected()
            selection_state_text = 'selected joints'

        else:
            nodes = pm.ls('%s_*' % crab.config.SKELETON, type='joint')
            nodes.extend(pm.ls('%s_*' % crab.config.GUIDE, type='transform'))

        with crab.utils.contexts.UndoChunk():
            for joint in nodes:
                if joint.hasAttr(self.POSE_NAME):

                    pos = None
                    if self.options.rotate_only:
                        pos = joint.getTranslation()
                        rotation_only_text = 'rotation only'

                    joint.setMatrix(joint.attr(self.POSE_NAME).get())

                    if pos:
                        joint.setTranslation(pos)
        print ('Loaded: {} to {} {}'.format(
            self.POSE_NAME,
            selection_state_text,
            rotation_only_text
        )),


# ------------------------------------------------------------------------------
class DefineTPoseTool(DefineAPoseTool):
    identifier = 'Poses : Define T Pose'
    POSE_NAME = 'TPose'


# ------------------------------------------------------------------------------
class ApplyTPoseTool(ApplyAPoseTool):
    identifier = 'Poses : Apply T Pose'
    POSE_NAME = 'TPose'
