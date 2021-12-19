from .. import utils
from .. import config
from ..vendor import qute

import json
import uuid


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

    # -- These allow you to mark certain options as being expected
    # -- to be fullfilled
    REQUIRED_NODE_OPTIONS = []

    # -- This allows for options to be optional, but if something is declared
    # -- then they should exist
    OPTIONAL_NODE_OPTIONS = []

    # --------------------------------------------------------------------------
    def __init__(self, rig=None, instance_id=None):

        # -- This is a uuid for the behaviour
        self.uuid = instance_id or str(uuid.uuid4())

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
    def ui(self, parent=None):
        """
        This is an optional mechanism to implement a custom UI widget to be displayed
        in tools for a behaviour.

        This MUST return a class which inherits from BehaviourUI. The class should
        not be instanced, but it should take two init arguments - the first being
        a behaviour class instance (which should be used to read and write to, and
        the second being the parent widget.

        :return: True if the apply is successful
        """
        return None

    # --------------------------------------------------------------------------
    @classmethod
    def rich_help(cls):
        if cls.preview:
            return dict(
                title=cls.identifier.title(),
                gif=cls.preview,
                description=cls.__doc__.strip() if cls.__doc__ else '',
            )

    # --------------------------------------------------------------------------
    def save(self):
        """
        This will save any option data in the behaviour
        """
        all_behaviour_data = json.loads(self.rig.meta().attr(config.BEHAVIOUR_DATA).get())

        for behaviour_data in all_behaviour_data:

            if behaviour_data.get('id') == self.uuid:
                behaviour_data['options'] = self.options

        # -- Now write the data into the attribute
        self.rig.meta().attr(config.BEHAVIOUR_DATA).set(
            json.dumps(all_behaviour_data),
        )

    # --------------------------------------------------------------------------
    def remove(self):
        """
        This will remove the behaviour with the given id. The id's of behaviours
        can be found by calling ```rig.assigned_behaviours()```.

        :param behaviour_id: uuid of the behaviour to remove
        :type behaviour_id: str

        :return: True if the behaviour was removed
        """
        # -- Get the current behaviour manifest
        current_data = json.loads(self.rig.meta().attr(config.BEHAVIOUR_DATA).get())

        # -- Look for a behaviour with the given behaviour id
        for idx, behaviour_data in enumerate(current_data):
            if behaviour_data['id'] == self.uuid:
                current_data.pop(idx)

                # -- Now write the data into the attribute
                self.rig.meta().attr(config.BEHAVIOUR_DATA).set(
                    json.dumps(current_data),
                )

                return True

        return False

    # --------------------------------------------------------------------------
    def shift_order(self, shift_offset):
        """
        Behaviours are built in sequence, this method allows you to shift
        a behaviour forward or backward in the sequence.

        :param shift_offset: The offset you want to shift by, so a value
            of 1 would shift it down the list by one, whilst a value of -1
            would shift it up once in the list
        :type shift_offset: int

        :return: True if the operation was successful
        """
        # -- Get the current behaviour manifest
        current_data = json.loads(self.rig.meta().attr(config.BEHAVIOUR_DATA).get())

        # -- Look for a behaviour with the given behaviour id
        for idx, behaviour_data in enumerate(current_data):
            if behaviour_data['id'] == self.uuid:

                # -- Offset the data be the required amount
                current_data.insert(
                    current_data.index(behaviour_data) + shift_offset,
                    current_data.pop(current_data.index(behaviour_data)),
                    )

                # -- Now write the data into the attribute
                self.rig.meta().attr(config.BEHAVIOUR_DATA).set(
                    json.dumps(current_data),
                )
                return True

        return False

    # --------------------------------------------------------------------------
    def can_build(self, available_nodes):
        """
        This is a validation step, allowing the behaviour to decide if it
        is able to build with the given nodes.

        Note: When implementing this ensure you implement good script editor
        output to the user so they can understand what is broken or missing.

        :param available_nodes: List of node names that will be available
            during the rig build
        :type available_nodes: list(str, str, str, ..)

        :return: True if the behaviour believes it can build successfully
        :rtype: bool
        """
        all_options = self.REQUIRED_NODE_OPTIONS + self.OPTIONAL_NODE_OPTIONS

        for option in all_options:

            # -- Skip if the option does not exist
            if option not in self.options:
                continue

            declared_nodes = [n for n in self.options[option].split(';') if n]

            if not declared_nodes and option in self.REQUIRED_NODE_OPTIONS:
                print('%s option requires a value' % option)
                return False

            for declared_node in declared_nodes:
                if declared_node not in available_nodes:
                    print('%s could not be found (%s)' % (declared_node, self.options.description))
                    return False

        return True


# ------------------------------------------------------------------------------
class BehaviourUI(qute.QWidget):

    # --------------------------------------------------------------------------
    def __init__(self, behaviour_instance, parent):
        super(BehaviourUI, self).__init__(parent)

        self.behaviour_instance = behaviour_instance

    # --------------------------------------------------------------------------
    @classmethod
    def unhandled_options(cls):
        """
        This should return a list of any options in the behaviour that
        are not handled by this ui and should therefore be displayed
        using the built in mechanisms of crab
        """
        return list()
