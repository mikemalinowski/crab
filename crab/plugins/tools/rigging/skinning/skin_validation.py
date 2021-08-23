import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class PrintSelectedInfluencesWithWeight(crab.RigTool):

    identifier = 'weighting_print_selected_influences_with_weight'
    display_name = 'Weighting : Print Selected Influences With Weight'

    # --------------------------------------------------------------------------
    def run(self, joints=None):
        """
        This is the main execution function for your tool. You may inspect
        the options dictionary of the tool to tailor the behaviour of your
        tool.

        :return: True of successful.
        """
        joints = joints or pm.selected()

        for joint in joints:
            if crab.utils.skinning.is_skinned(joint):

                print('%s is being used in the following skin clusters:' % joint.name())

                for skin in crab.utils.skinning.connected_skins(joint):
                    print('\t%s' % skin)

        return True
