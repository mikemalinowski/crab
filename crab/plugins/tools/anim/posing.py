import os
import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
def get_icon(name):
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "icons",
        "%s.png" % name,
    )


# --------------------------------------------------------------------------------------
def get_namespace(node):
    if ":" in node:
        return ":".join(pm.selected()[0].name().split(":")[:-1])

    return None


# --------------------------------------------------------------------------------------
class CopyPoseTool(crab.tools.AnimTool):
    """
    This will store the current local space transform of the selected
    controls and store them.
    """

    identifier = "poses_copy"
    display_name = "Pose : Copy"
    icon = get_icon("pose_store")

    Pose = dict()

    def run(self, nodes=None):
        nodes = nodes or pm.selected()

        for ctl in nodes:
            CopyPoseTool.Pose[ctl.name().split(":")[-1]] = ctl.getMatrix()


# --------------------------------------------------------------------------------------
class PastePoseTool(crab.tools.AnimTool):
    """
    This will apply the previously stored local space transforms back to the objects.

    If "Selection Only" is turned on, then the pose will only be applied to matching
    objects which are also selected.
    """

    identifier = "poses_copy_paste"
    display_name = "Pose : Paste"
    icon = get_icon("pose_apply")

    tooltips = dict(
        selection_only=(
            "If True the pose will only be applied to matched "
            "controls in the current selection"
        ),
    )

    def __init__(self):
        super(PastePoseTool, self).__init__()

        self.options.selection_only = False

    def run(self, nodes=None):
        nodes = nodes or pm.selected()

        selected_names = [
            node.name()
            for node in nodes
        ]

        if not selected_names:
            return

        ns = get_namespace(selected_names[0])

        for ctl, pose in CopyPoseTool.Pose.items():

            # -- Add the namespace onto the ctl
            resolved_name = ctl
            if ns:
                resolved_name = ns + ":" + ctl

            if not pm.objExists(resolved_name):
                continue

            if self.options.selection_only and ctl not in selected_names:
                continue

            pm.PyNode(resolved_name).setMatrix(pose)


# --------------------------------------------------------------------------------------
class CopyWorldSpaceTool(crab.tools.AnimTool):
    """
    This will store the current world space transform of the selected
    controls and store them.
    """

    identifier = "poses_copyworldspace"
    display_name = "Pose : Copy : World Space"
    icon = get_icon("pose_store")

    TRANSFORM_DATA = dict()

    def run(self):
        # -- Clear out any dictionary data
        CopyWorldSpaceTool.TRANSFORM_DATA = dict()

        for node in pm.selected():
            CopyWorldSpaceTool.TRANSFORM_DATA[node.name()] = node.getMatrix(
                worldSpace=True)


# --------------------------------------------------------------------------------------
class PasteWorldSpaceTool(crab.tools.AnimTool):
    """
    This will apply the previously stored world space transforms back to the objects.

    If "Selection Only" is turned on, then the pose will only be applied to matching
    objects which are also selected.
    """

    identifier = "poses_copyworldspace_paste"
    display_name = "Pose : Paste : World Space"
    icon = get_icon("pose_apply")

    def run(self):

        for name, matrix in CopyWorldSpaceTool.TRANSFORM_DATA.items():
            if pm.objExists(name):
                pm.PyNode(name).setMatrix(
                    CopyWorldSpaceTool.TRANSFORM_DATA[name],
                    worldSpace=True,
                )
