import crab
from crab.vendor import qute
import pymel.core as pm


# ------------------------------------------------------------------------------
class DefineAPoseTool(crab.RigTool):

    identifier = 'poses_define_a_pose'
    display_name = 'Define A Pose'
    icon = 'poses.png'
    tooltips = dict(
        selection_only='If true, only the selected objects will be affected',
    )
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
            nodes = pm.ls('%s_*' % crab.config.SKELETON, type='joint', r=True)
            nodes.extend(pm.ls('%s_*' % crab.config.GUIDE, type='transform', r=True))

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

    identifier = 'poses_apply_a_pose'
    display_name = 'Apply A Pose'
    icon = 'poses.png'
    tooltips = dict(
        selection_only='If true, only the selected objects will be affected',
        rotate_only='If True only the rotation will be applied',
    )

    POSE_NAME = 'APose'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(ApplyAPoseTool, self).__init__()
        self.options.selection_only = False
        self.options.rotate_only = False
        self.options.translate_only = False

    # --------------------------------------------------------------------------
    def run(self):

        # -- Ensure all rigs are editable
        for rig in crab.Rig.all():
            if not rig.is_editable():

                confirmation = qute.utilities.request.confirmation(
                    title='%s is not editable' % rig.node().name(),
                    label='To assign a pose, the rig needs to be editable. Would you like to put the rig into an editable state?',
                )

                if confirmation:
                    rig.edit()

                else:

                    # -- If any rig is not intended to be editable, exit
                    return

        selection_state_text = 'all joints'
        rotation_only_text = ''
        if self.options.selection_only:
            nodes = pm.selected()
            selection_state_text = 'selected joints'

        else:
            nodes = pm.ls('%s_*' % crab.config.SKELETON, type='joint', r=True)
            nodes.extend(pm.ls('%s_*' % crab.config.GUIDE, type='transform', r=True))

        with crab.utils.contexts.UndoChunk():
            for joint in nodes:
                if joint.hasAttr(self.POSE_NAME):

                    pos = None
                    if self.options.rotate_only:
                        pos = joint.getTranslation()
                        rotation_only_text = 'rotation only'

                    rot = None
                    if self.options.translate_only:
                        rot = joint.getRotation()
                        rotation_only_text = 'translation only'

                    joint.setMatrix(joint.attr(self.POSE_NAME).get())

                    if pos:
                        joint.setTranslation(pos)

                    if rot:
                        joint.setRotation(rot)

        print ('Loaded: {} to {} {}'.format(
            self.POSE_NAME,
            selection_state_text,
            rotation_only_text
        )),


# ------------------------------------------------------------------------------
class DefineTPoseTool(DefineAPoseTool):
    identifier = 'poses_define_t_pose'
    display_name = 'Define T Pose'
    category = 'Poses'
    POSE_NAME = 'TPose'


# ------------------------------------------------------------------------------
class ApplyTPoseTool(ApplyAPoseTool):
    identifier = 'poses_apply_t_pose'
    display_name = 'Apply T Pose'
    POSE_NAME = 'TPose'
