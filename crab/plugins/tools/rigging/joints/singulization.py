import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class SingulizeSelected(crab.RigTool):

    identifier = 'joints_singulize_selected'
    display_name = 'Singulize Selected'
    icon = 'joints.png'

    # --------------------------------------------------------------------------
    def run(self):
        rig = crab.Rig(node=pm.selected()[0])

        for node in pm.selected():
            rig.add_component('Singular', pre_existing_joint=node.name())


# ------------------------------------------------------------------------------
class SingulizeAll(crab.RigTool):

    identifier = 'joints_singulize_all'
    display_name = 'Singulize All'
    icon = 'joints.png'

    # --------------------------------------------------------------------------
    def run(self):

        # -- Get the currently active rig
        rig = crab.Rig.all()[0]

        # -- Find all teh joints in the rig so we can check which
        # -- require singulizing
        all_joints = rig.skeleton_org().getChildren(
            allDescendents=True,
            type='joint',
        )

        for joint in all_joints:

            # -- Assume the joint will need singulizing unless
            # -- we find otherwise.
            requires_singulizing = True

            # -- If the joint has crab meta attached, then we do not
            # -- want to singulize it
            for possible_meta in joint.outputs(type='network'):
                if possible_meta.hasAttr('crabComponent'):
                    requires_singulizing = False
                    break

            # -- Singulize if required
            if requires_singulizing:
                rig.add_component('Singular', pre_existing_joint=joint.name())
