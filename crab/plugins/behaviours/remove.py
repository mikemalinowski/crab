import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class ReparentBehaviour(crab.Behaviour):
    identifier = "Delete Nodes"
    version = 1

    tooltip = dict(
        node="The name of the node to be reparented to",
        new_parent="The name of the node which should be the targets new parent",
    )

    REQUIRED_NODE_OPTIONS = ["node", "new_parent"]

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(ReparentBehaviour, self).__init__(*args, **kwargs)

        self.options.nodes = ""

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        for node in self.options.nodes.split(";"):

            if node and pm.objExists(node):
                pm.delete(node)
                
        return True
