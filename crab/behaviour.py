from . import utils
from . import config


# ------------------------------------------------------------------------------
class Behaviour(object):
    """
    A behaviour is a rigging behaviour which may or may not have a dag element
    to it and may be dependent on other elements of the control rig. Whilst
    components are atomic behaviours can cross the boundaries of any component.
    """

    # -- Unique identifier for the behaviur
    identifier = ''
    version = 0

    # --------------------------------------------------------------------------
    def __init__(self, rig=None):

        # -- All the options should be defined within this
        # -- dictionary
        self.options = utils.AttributeDict()
        self.options.description = 'unknown'
        self.options.side = config.MIDDLE

        # -- By default assume we do not have a root yet
        self.rig = rig

    # --------------------------------------------------------------------------
    def apply(self):
        """
        You should implement this function to build your behaviour. You may
        utilise the options dictionary to read information you need.
        
        :return: True if the apply is successful 
        """
        return True
