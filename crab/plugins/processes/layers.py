import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class LayerProcess(crab.Process):
    """
    Makes any bones which are part of the control hierarchy invisible
    by setting their draw style to None.
    """

    # -- Define the identifier for the plugin
    identifier = 'Layer'
    version = 1

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def post_build(self):
        """
        This is called after the entire rig has been built, so we will attempt
        to re-apply the shape information.

        :return:
        """
        control_root = self.rig.find('ControlRoot')[0]
        skeleton_root = self.rig.find('SkeletonRoot')[0]
        geometry_root = self.rig.find('GeometryRoot')[0]

        # -- Ensure the layers exist
        crab.utils.organise.add_to_layer(None, crab.config.CONTROL_LAYER)
        crab.utils.organise.add_to_layer(None, crab.config.GEOMETRY_LAYER)
        crab.utils.organise.add_to_layer(None, crab.config.SKELETON_LAYER)

        # -- Add all the elements into the layers
        for skeletal_joint in skeleton_root.getChildren(ad=True, type='joint'):
            crab.utils.organise.add_to_layer(
                skeletal_joint,
                crab.config.SKELETON_LAYER,
            )

        for geometry in geometry_root.getChildren(ad=True, type='mesh'):
            crab.utils.organise.add_to_layer(
                geometry.getParent(),
                crab.config.GEOMETRY_LAYER,
            )

        for control in control_root.getChildren(ad=True, type='transform'):
            if crab.config.CONTROL not in control.name():
                crab.utils.organise.add_to_layer(
                    control,
                    crab.config.CONTROL_LAYER,
                )

        # -- Ensure the layers are setup correctly
        pm.PyNode(crab.config.SKELETON_LAYER).visibility.set(0)
        pm.PyNode(crab.config.GEOMETRY_LAYER).displayType.set(2)
