import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class ReparentBehaviour(crab.Behaviour):
    identifier = "Re-Parent"
    version = 1

    tooltip = dict(
        node="The name of the node to be reparented to",
        new_parent="The name of the node which should be the targets new parent",
    )

    REQUIRED_NODE_OPTIONS = ["node", "new_parent"]

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(ReparentBehaviour, self).__init__(*args, **kwargs)

        self.options.node = ""
        self.options.new_parent = ""

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        # -- Check that we can actually get the parent
        if not pm.objExists(self.options.new_parent):
            raise Exception("%s does not exist" % self.options.new_parent)

        # -- Get hte parent as a pymel node
        new_parent = pm.PyNode(self.options.new_parent)

        for node_name in self.options.node.split(";"):

            node_name = node_name.strip()

            if not pm.objExists(node_name):
                raise Exception("%s does not exist" % node_name)

            node = pm.PyNode(node_name)
            node.setParent(new_parent)

        return True
