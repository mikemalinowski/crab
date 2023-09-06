import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
class MoveRotationsToOrientsTool(crab.RigTool):

    identifier = "joints_oriswitch_rotations_to_orients"
    display_name = "Move Rotations to Orients"
    icon = "joints.png"

    tooltips = dict(
        mirror_plane=(
            "Moves any rotations on the normal X,Y,Z channels to the "
            "joint orient channels"
        ),
    )

    # ----------------------------------------------------------------------------------
    def run(self):
        for node in pm.selected():
            crab.utils.joints.move_rotations_to_joint_orients(node)


# --------------------------------------------------------------------------------------
class MoveOrientsToRotationsTool(crab.RigTool):

    identifier = "joints_oriswitch_orients_to_rotations"
    display_name = "Move Orients to Rotations"
    icon = "joints.png"

    tooltips = dict(
        mirror_plane=(
            "Moves any rotations on the joint orient channels to "
            "the normal X,Y,Z channels"
        ),
    )

    # ----------------------------------------------------------------------------------
    def run(self):
        for node in pm.selected():
            crab.utils.joints.move_joint_orients_to_rotations(node)

