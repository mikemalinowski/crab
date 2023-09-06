import crab


# --------------------------------------------------------------------------------------
class BoneFilterProcess(crab.Process):
    """
    Makes any bones which are part of the control hierarchy invisible
    by setting their draw style to None.
    """

    # -- Define the identifier for the plugin
    identifier = "BoneFilter"
    version = 1

    # ----------------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def post_build(self):
        """
        This is called after the entire rig has been built, so we will attempt
        to re-apply the shape information.

        :return: 
        """
        for joint in self.rig.control_org().getChildren(ad=True, type="joint"):
            joint.drawStyle.set(2)  # -- Hide
