import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class ToggleJointStyleTool(crab.RigTool):

    identifier = 'joints_toggle_draw'
    display_name = 'Toggle Draw'
    icon = 'joints.png'

    # --------------------------------------------------------------------------
    def run(self):
        selected = pm.selected()

        if not selected:
            return

        if not isinstance(selected[0], pm.nt.Joint):
            return

        current_value = selected[0].drawStyle.get()

        value = 2 if not current_value else 0

        for joint in pm.selected():
            if isinstance(joint, pm.nt.Joint):
                joint.drawStyle.set(value)
