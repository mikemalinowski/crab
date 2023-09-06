# --------------------------------------------------------------------------------------
# noinspection PyMethodMayBeStatic
class Process(object):
    """
    A process is a plugin which is executed during an edit call as well as
    a build call. This plugin type has three stages:

        * snapshot
            This is done before the control rig is destroyed and its your
            oppotunity to read any information from the rig.
            Note: You must store the data you have read, as the same process
                instance will not be used during the build.

        * pre
            This is called after the control is destroyed, leaving the skeleton
            bare. This is typically a good time to do any skeleton modifications
            as nothing will be locking or driving the joints.

        * post
            This is called after all the components and behaviours are built,
            allowing  you to perform any actions against the rig as a whole.
    """

    identifier = "unknown"
    version = 1
    order = 0

    # ----------------------------------------------------------------------------------
    def __init__(self, rig):
        self.rig = rig

    # ----------------------------------------------------------------------------------
    def snapshot(self):
        """
        This is done before the control rig is destroyed and its your
        oppotunity to read any information from the rig.

        Note: You must store the data you have read, as the same process
            instance will not be used during the build.

        :return: None
        """
        pass

    # ----------------------------------------------------------------------------------
    def post_edit(self):
        """
        This is called after the control is destroyed, leaving the skeleton
        bare. This is typically a good time to do any skeleton modifications
        as nothing will be locking or driving the joints.

        :return:
        """
        pass

    # ----------------------------------------------------------------------------------
    def pre_build(self):
        """
        This is called after validation but before the components are started
        to be built.

        :return:
        """
        pass

    # ----------------------------------------------------------------------------------
    def post_build(self):
        """
        This is called after all the components and behaviours are built,
        allowing  you to perform any actions against the rig as a whole.

        :return:
        """
        pass

    # ----------------------------------------------------------------------------------
    def validate(self):
        """
        This occurs before the pre_build and should NOT modify the rig in any form. It
        should only be used to validate that the build process can begin.
        """
        return True
