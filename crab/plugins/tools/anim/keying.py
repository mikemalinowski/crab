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
class KeyAllTool(crab.tools.AnimTool):
    """
    This will place a keyframe on all controls within the entire scene at their
    current values and at the current time.
    """

    identifier = "keyframe_all"
    display_name = "Key : All"
    icon = get_icon("key_all")

    def run(self):
        pm.setKeyframe(crab.utils.access.get_controls())


# --------------------------------------------------------------------------------------
class KeyAllOnCharacterTool(crab.tools.AnimTool):
    """
    This will keyframe all the controls within the currently selected rig at their
    current values on the current frame.
    """

    identifier = "keyframe_all_character"
    display_name = "Key : All : Character"
    icon = get_icon("key_character")

    def run(self):
        pm.setKeyframe(crab.utils.access.get_controls(current_only=True))
