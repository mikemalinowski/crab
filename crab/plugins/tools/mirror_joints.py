import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class MirrorJointsTool(crab.RigTool):

    identifier = 'Mirror Joints'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(MirrorJointsTool, self).__init__()

        self.options.mirror_plane = ''

    # --------------------------------------------------------------------------
    def run(self):
        crab.utils.maths.global_mirror(
            pm.selected(),
            across=self.options.mirror_plane or None,
        )
