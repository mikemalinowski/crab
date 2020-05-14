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


class SetAttributeBehaviour(crab.Behaviour):

    identifier = 'Attributes : Set'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(SetAttributeBehaviour, self).__init__(*args, **kwargs)

        self.options.objects = ''
        self.options.attribute_name = ''
        self.options.attribute_value = ''
        self.options.is_string = False
        self.options.is_number = True

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        value = self.options.attribute_value

        if self.options.is_number:
            value = float(self.options.attribute_value)

        for node in self.options.objects.split(';'):
            if node and pm.objExists(node):
                pm.PyNode(node).attr(self.options.attribute_name).set(value)

        return True


