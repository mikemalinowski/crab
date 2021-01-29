
from .. import utils
from .. import config


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

    # -- The preview allows you to specify the location of a gif to show the user
    # -- what this behaviour will result in. If not specified then no rich help
    # -- will be presented for this item
    preview = None

    # -- This allows for tooltips to be specified for the options of this component
    tooltips = dict()

    # -- This allows an icon to be defined
    icon = utils.resources.get('behaviour.png')

    # --------------------------------------------------------------------------
    def __init__(self, rig=None):
        # -- All the options should be defined within this
        # -- dictionary
        self.options = utils.types.AttributeDict()
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

    # --------------------------------------------------------------------------
    @classmethod
    def rich_help(cls):
        if cls.preview:
            return dict(
                title=cls.identifier.title(),
                gif=cls.preview,
                description=cls.__doc__.strip() if cls.__doc__ else '',
            )
