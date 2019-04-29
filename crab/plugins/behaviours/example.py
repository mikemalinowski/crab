import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class ParentConstraint(crab.Behaviour):
    """
    This is meant as an example only to show how a behaviour
    can operate
    """
    identifier = 'ExampleParentConstraint'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(ParentConstraint, self).__init__(*args, **kwargs)

        self.options.constraint_this = ''
        self.options.constraint_to = ''
        self.options.maintainOffset = False

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):
        pm.parentConstraint(
            self.options.constraint_to,
            self.options.constraint_this,
            mo=self.options.maintainOffset,
        )
        return True
