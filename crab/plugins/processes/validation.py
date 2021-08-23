import crab
import pymel.core as pm

from crab.vendor import qute


# --------------------------------------------------------------------------------------------------
class CheckPose(crab.Process):

    identifier = 'APose Validation'

    def validate(self):
        """
        We want to check that the pose the rig is in is the same as the stored
        pose - this prevents the user losing A-Pose changes when hitting the rig build
        """
        print('running APose Validation')

        failures = list()

        for joint in pm.ls(crab.config.SKELETON + '*'):
            if joint.hasAttr('APose'):
                expected_matrix = joint.APose.get()
                current_matrix = joint.getMatrix()

                if not current_matrix.isEquivalent(expected_matrix):
                    failures.append(joint)

        # -- If we have failures, lets call them out
        if failures:

            # -- Print each failure
            for failure in failures:
                print('%s is not in its APose, your current pose might be lost' % failure.name())

            # -- If we are in batch mode then we return, we ignore this issue
            if pm.about(batch=True):
                return True

            # -- Because we're in UI mode, we should ask the user whether they want to
            # -- continue
            confirmation = qute.utilities.request.confirmation(
                title='Pose Difference',
                label='There are differences between your current pose and the A-Pose. Do you want to continue?',
            )

            if not confirmation:
                return False

        else:
            print('\tNo failures found.')

        return True
