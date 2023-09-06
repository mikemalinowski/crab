import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class LockAndHideBehaviour(crab.Behaviour):
    identifier = "Lock And Hide Attributes"
    version = 1

    tooltip = dict(
        node="The name of the node to have attributes locked and hidden",
        attributes="List of attributes to lock (seperated by ;)",
    )

    REQUIRED_NODE_OPTIONS = ["node", "attributes"]

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(LockAndHideBehaviour, self).__init__(*args, **kwargs)

        self.options.node = ""
        self.options.attributes = ""

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        if not pm.objExists(self.options.node):
            pm.error("Could not find : " + self.options.node)
            return False

        node = pm.PyNode(self.options.node)

        for attr in self.options.attributes.split(";"):
            if attr:
                node.attr(attr).lock()
                node.attr(attr).set(k=False, cb=False)

        return True


# ------------------------------------------------------------------------------
class UnLockAndShowBehaviour(crab.Behaviour):
    identifier = "UnLock And Show Attributes"
    version = 1

    tooltip = dict(
        node="The name of the node to have attributes unlocked and shown",
        attributes="List of attributes to unlock (seperated by ;)",
    )

    REQUIRED_NODE_OPTIONS = ["node", "attributes"]

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(UnLockAndShowBehaviour, self).__init__(*args, **kwargs)

        self.options.node = ""
        self.options.attributes = ""

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        if not pm.objExists(self.options.node):
            pm.error("Could not find : " + self.options.node)
            return False

        node = pm.PyNode(self.options.node)

        for attr in self.options.attributes.split(";"):
            if attr:
                node.attr(attr).unlock()
                node.attr(attr).set(k=True, cb=True)

        return True
