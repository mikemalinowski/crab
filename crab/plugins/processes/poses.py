import crab


# ------------------------------------------------------------------------------
class LayerProcess(crab.Process):
    """
    Makes any bones which are part of the control hierarchy invisible
    by setting their draw style to None.
    """

    # -- Define the identifier for the plugin
    identifier = "Layer"
    version = 1

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def post_edit(self):
        """
        This is called after the entire rig has been built, so we will attempt
        to re-apply the shape information.

        :return:
        """
        crab.tools.rigging().request("poses_apply_a_pose")().run()

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def pre_build(self):
        """
        This is called after the entire rig has been built, so we will attempt
        to re-apply the shape information.

        :return:
        """
        crab.tools.rigging().request("poses_apply_t_pose")().run()
