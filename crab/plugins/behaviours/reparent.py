import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class ReparentBehaviour(crab.Behaviour):
    identifier = 'Re-Parent'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(ReparentBehaviour, self).__init__(*args, **kwargs)

        self.options.node = ''
        self.options.new_parent = ''

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):
        node = pm.PyNode(self.options.node)
        new_parent = pm.PyNode(self.options.new_parent)

        node.setParent(new_parent)

        return True
