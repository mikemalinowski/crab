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
        self.options.translation_only = False
        self.options.rotation_only = False
        self.options.default_space = ''

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
        spaces.insert(0, crab.utils.hierarchy.find_above(target, crab.config.ORG))
        labels.insert(0, 'Parent')

        # -- Add a spacer attribute
        crab.utils.organise.add_separator_attr(target)

        # -- Add the space switch attribute
        target.addAttr(
            'spaces',
            at='enum',
            enumName=':'.join(labels),
            k=True,
        )
        space_attr = target.attr('spaces')
        default_id = 0

        zero = crab.utils.hierarchy.find_above(target, crab.config.ZERO)

        for idx, space in enumerate(spaces):

            skip_translate = []
            skip_rotate = []

            # if self.options.translation_only:
            #     skip_rotate = ['x', 'y', 'z']
            #
            # if self.options.rotation_only:
            #     skip_translate = ['x', 'y', 'z']

            # -- Create a constraint
            cns = pm.parentConstraint(
                space,
                zero,
                maintainOffset=True,
                skipRotate=skip_rotate,
                skipTranslate=skip_translate,
            )

            # -- Create the condition node
            condition = crab.create.generic(
                node_type='condition',
                prefix=crab.config.LOGIC,
                description='%sSpaceSwitch' % self.options.description.replace(' ', ''),
                side=self.options.side,
            )
            space_attr.connect(condition.firstTerm)
            condition.secondTerm.set(idx)

            # -- Set the various possible output values
            condition.colorIfTrueR.set(1)
            condition.colorIfFalseR.set(0)

            # -- Hook the condition into the constraint
            condition.outColorR.connect(cns.getWeightAliasList()[-1])

            # -- Check if this is the space we need to assign
            # -- as the default space
            if labels[idx] == self.options.default_space:
                default_id = idx

        for axis in ['X', 'Y', 'Z']:
            if self.options.translation_only:
                zero.attr('rotate%s' % axis).disconnect()

            if self.options.rotation_only:
                zero.attr('translate%s' % axis).disconnect()

        # -- Set the default space
        target.spaces.set(default_id)

        return True
