import crab
import pymel.core as pm


# ----------------------------------------------------------------------------------------------------------------------
class AddProxyAttrBehaviour(crab.Behaviour):

    # -- Unique identifier for the behaviur
    identifier = "Add Proxy Attribute"
    version = 0

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(AddProxyAttrBehaviour, self).__init__(*args, **kwargs)

        self.options.target = ""
        self.options.source_attr = ""
        self.options.display_name = ""

    # ------------------------------------------------------------------------------------------------------------------
    def apply(self):

        if not pm.objExists(self.options.target):
            print("{name} does not exist".format(name=self.options.target))
            return False

        if not pm.objExists(self.options.source_attr):
            print("{name} attribute does not exist".format(name=self.options.source_attr))
            return False

        target = pm.PyNode(self.options.target)

        target.addAttr(
            self.options.display_name,
            proxy=self.options.source_attr,
        )

        return True