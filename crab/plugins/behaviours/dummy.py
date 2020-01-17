import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class Duplicate(crab.Behaviour):
    """
    This is meant as an example only to show how a behaviour
    can operate
    """
    identifier = 'Duplicate'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(Duplicate, self).__init__(*args, **kwargs)

        self.options.parent = ''
        self.options.target = ''

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):
        result = pm.duplicate(self.options.target)[0]
        result.setParent(self.options.parent, a=True)