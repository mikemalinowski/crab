import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class InsertControlBehaviour(crab.Behaviour):
    identifier = 'Connect Attribute'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(InsertControlBehaviour, self).__init__(*args, **kwargs)

        self.options.source = ''
        self.options.destination = ''

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        source = pm.PyNode(self.options.source)
        destination = pm.PyNode(self.options.destination)

        source.connect(destination)

        return True
