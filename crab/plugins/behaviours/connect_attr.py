import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class InsertControlBehaviour(crab.Behaviour):
    identifier = "Connect Attribute"
    version = 1

    tooltips = dict(
        description="A descriptive to label the behaviour",
        side="Typically LF, MD or RT - denoting the side/location of the behaviour",
        source="The longName to the attribute you want to read the values from",
        destination="The longName to the attribute you want to drive",
    )

    # -- We expect these options to be fullfilled with objects
    REQUIRED_NODE_OPTIONS = ["source", "destination"]

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(InsertControlBehaviour, self).__init__(*args, **kwargs)

        self.options.source = ""
        self.options.destination = ""

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        source = pm.PyNode(self.options.source)
        destination = pm.PyNode(self.options.destination)

        source.connect(destination)

        return True

    # --------------------------------------------------------------------------
    def can_build(self, available_nodes):
        if self.options.source not in available_nodes:
            print("%s is cannot be found" % self.options.source)
            return False

        if self.options.destination not in available_nodes:
            print("%s cannot be found" % self.options.destination)
            return False

        return True


# ------------------------------------------------------------------------------
class SetAttributeBehaviour(crab.Behaviour):

    identifier = "Attributes : Set"
    version = 1

    tooltips = dict(
        description="A descriptive to label the behaviour",
        side="Typically LF, MD or RT - denoting the side/location of the behaviour",
        objects="List of objects to set the values on",
        attribute_name="The name of the attribute that should be set (excluding object name)",
        attribute_value="The value to set to the attribute",
        is_string="If the attribute is a string/text attribute, then tick this",
        is_number="If the attribute is a float or integer then please tick this",
    )

    REQUIRED_NODE_OPTIONS = ["objects"]

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(SetAttributeBehaviour, self).__init__(*args, **kwargs)

        self.options.objects = ""
        self.options.attribute_name = ""
        self.options.attribute_value = ""
        self.options.is_string = False
        self.options.is_number = True

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        value = self.options.attribute_value

        if self.options.is_number:
            value = float(self.options.attribute_value)

        if "*" in self.options.objects:
            node_list = pm.ls(self.options.objects)

        else:
            node_list = self.options.objects.split(";")

        for node in node_list:
            if node and pm.objExists(node):
                try:
                    pm.PyNode(node).attr(self.options.attribute_name).set(value)

                except:
                    pass

        return True


