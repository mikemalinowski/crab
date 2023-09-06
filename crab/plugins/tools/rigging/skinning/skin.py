import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
class SkinDisconnect(crab.RigTool):

    identifier = "skinning_disconnect"
    display_name = "Skinning : Disconnect All Skins"
    icon = "skinning.png"

    # ----------------------------------------------------------------------------------
    def run(self):

        for skin in pm.ls(type="skinCluster"):
            skin.moveJointsMode(True)


# --------------------------------------------------------------------------------------
class SkinReconnect(crab.RigTool):

    identifier = "skinning_connect"
    display_name = "Skinning : Reconnect All Skins"
    icon = "skinning.png"

    # ----------------------------------------------------------------------------------
    def run(self):
        for skin in pm.ls(type="skinCluster"):
            skin.moveJointsMode(False)


# --------------------------------------------------------------------------------------
class CopyToUnboundMesh(crab.RigTool):

    identifier = "skinning_copy_to_unbound_mesh"
    display_name = "Skinning : Copy Skin To Unbound Mesh"
    icon = "skinning.png"

    # ----------------------------------------------------------------------------------
    def run(self, current_skin_host=None, target=None):

        # -- Get our mesh candidates
        current_skin_host = current_skin_host or pm.selected()[0]
        targets = target or pm.selected()[1:]

        if not isinstance(targets, list):
            targets = [targets]

        # -- Look for the mesh
        skin = pm.PyNode(pm.mel.findRelatedSkinCluster(current_skin_host))

        # -- Get a list of the influence objects being used
        # -- by the skin currently
        influences = skin.influenceObjects()

        for target in targets:
            # -- Apply a new skin cluster
            new_skin = pm.skinCluster(
                influences,
                target,
                toSelectedBones=True,
                maximumInfluences=skin.getMaximumInfluences()
            )

            # -- Copy the skin weights between them
            pm.copySkinWeights(
                sourceSkin=skin,
                destinationSkin=new_skin,
                noMirror=True,
                surfaceAssociation="closestPoint",
                influenceAssociation=["name", "closestJoint", "label"],
            )

        # -- Keep the source mesh selected
        pm.select(current_skin_host)
