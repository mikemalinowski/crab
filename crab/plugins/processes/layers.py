import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
class LayerProcess(crab.Process):
    """
    Makes any bones which are part of the control hierarchy invisible
    by setting their draw style to None.
    """

    # -- Define the identifier for the plugin
    identifier = "Layers"
    version = 1

    # ----------------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def post_build(self):
        """
        This is called after the entire rig has been built, so we will attempt
        to re-apply the shape information.

        :return:
        """
        # -- Ensure the layers exist
        crab.utils.organise.add_to_layer(None, crab.config.CONTROL_LAYER)
        crab.utils.organise.add_to_layer(None, crab.config.GEOMETRY_LAYER)
        crab.utils.organise.add_to_layer(None, crab.config.SKELETON_LAYER)

        # -- Add all the elements into the layers
        for skeletal_joint in self.rig.skeleton_org().getChildren(ad=True, type="joint"):
            crab.utils.organise.add_to_layer(
                skeletal_joint,
                crab.config.SKELETON_LAYER,
            )

        for geometry in self.rig.find_org("Geometry").getChildren(ad=True, type="mesh"):
            crab.utils.organise.add_to_layer(
                geometry.getParent(),
                crab.config.GEOMETRY_LAYER,
            )

        for control in self.rig.control_org().getChildren(ad=True, type="transform"):
            if crab.config.CONTROL not in control.name():
                crab.utils.organise.add_to_layer(
                    control,
                    crab.config.CONTROL_LAYER,
                )

        # -- Ensure the layers are setup correctly
        pm.PyNode(crab.config.SKELETON_LAYER).visibility.set(0)
        pm.PyNode(crab.config.GEOMETRY_LAYER).displayType.set(2)

    # ----------------------------------------------------------------------------------
    def post_edit(self):
        """
        This is called after the control is destroyed, leaving the skeleton
        bare. This is typically a good time to do any skeleton modifications
        as nothing will be locking or driving the joints.

        :return:
        """
        pm.PyNode(crab.config.SKELETON_LAYER).visibility.set(1)
