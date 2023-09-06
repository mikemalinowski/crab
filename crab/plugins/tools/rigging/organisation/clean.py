import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
class CleanMeta(crab.RigTool):
    """
    This will clean/remove any redundant crab meta nodes along with any orphan
    guide roots
    """

    identifier = "clean_meta"
    display_name = "Clean Rig Meta"
    icon = "clean.png"

    # ----------------------------------------------------------------------------------
    def run(self):

        meta_nodes = [
            node for node in pm.ls("META_*")
            if node.hasAttr(crab.config.COMPONENT_MARKER)
        ]

        for meta_node in meta_nodes:

            # -- Check if it has a skeletal root connection, if it does, then its
            # -- perfectly valid
            if meta_node.attr(crab.config.SKELETON_ROOT_LINK_ATTR).inputs():
                continue

            # -- If this is an orphan, then check for a guide connection, if there
            # -- is one, then we remove the guide
            guide_connection = meta_node.attr(crab.config.GUIDE_ROOT_LINK_ATTR).inputs()

            if guide_connection:
                pm.delete(guide_connection)

            # -- Finally delete the meta node
            if pm.objExists(meta_node):
                pm.delete(meta_node)

