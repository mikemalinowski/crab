import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class SpaceSwitch(crab.Behaviour):
    """
    This is meant as an example only to show how a behaviour
    can operate
    """
    identifier = 'SpaceSwitch'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(SpaceSwitch, self).__init__(*args, **kwargs)

        self.options.target = ''
        self.options.spaces = ''
        self.options.labels = ''

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        # -- Start by getting the objects as pymel objects
        target = pm.PyNode(self.options.target)
        spaces = [
            pm.PyNode(space)
            for space in self.options.spaces.split(';')
        ]

        # -- Get our labels
        labels = self.options.labels.split(';')

        # -- If there are no labels then we extract the description
        # -- from each space and use that as the labels
        if not labels:
            labels = [
                crab.config.get_description(space)
                for space in spaces
            ]

        # -- Add the targets parent
        spaces.insert(0, target.getParent())
        labels.insert(0, 'Parent')

        # -- Add a spacer attribute
        crab.utils.organise.add_separator_attr(target)

        # -- Add the space switch attribute
        target.addAttr(
            'spaces',
            at='enum',
            enumName=':'.join(labels),
        )
        space_attr = target.attr('spaces')

        for idx, space in enumerate(spaces):

            # -- Create a constraint
            cns = pm.parentConstraint(
                space,
                target,
                maintainOffset=True,
            )

            # -- Create the condition node
            condition = pm.createNode('condition')
            space_attr.connect(condition.firstTerm)
            condition.secondTerm.set(idx)

            # -- Set the various possible output values
            condition.colorIfTrueR.set(1)
            condition.colorIfFalseR.set(0)

            # -- Hook the condition into the constraint
            condition.outColorR.connect(cns.getWeightAliasList()[-1])

        return True
