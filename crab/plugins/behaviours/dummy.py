import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class Duplicate(crab.Behaviour):
    """
    This is meant as an example only to show how a behaviour
    can operate
    """
    identifier = "Duplicate"
    version = 1

    tooltips = dict(
        parent="The node which the dupicated object should be parented under",
        target="The object to duplicate",
    )

    REQUIRED_NODE_OPTIONS = ["parent", "target"]

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(Duplicate, self).__init__(*args, **kwargs)

        self.options.parent = ""
        self.options.target = ""

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):
        result = pm.duplicate(self.options.target)[0]
        result.setParent(self.options.parent, a=True)
