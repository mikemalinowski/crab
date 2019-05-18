import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class SkinDisconnect(crab.RigTool):

    identifier = 'Skin : Disconnect'

    # --------------------------------------------------------------------------
    def run(self):

        for skin in pm.ls(type='skinCluster'):
            skin.moveJointsMode(True)


# ------------------------------------------------------------------------------
class SkinReconnect(crab.RigTool):

    identifier = 'Skin : Reconnect'

    # --------------------------------------------------------------------------
    def run(self):
        for skin in pm.ls(type='skinCluster'):
            skin.moveJointsMode(False)
