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
        self.options.parent_label = 'Parent'
        self.options.target_offsets = ''

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        # -- Get a list of any target offsets
        target_offsets = dict()

        for target_data in self.options.target_offsets.split(';'):
            if '=' in target_data:
                target, offset = target_data.split('=')
                target_offsets[target] = pm.PyNode(offset)

        self.create(
            description=self.options.description,
            side=self.options.side,
            target=pm.PyNode(self.options.target),
            spaces=[
                pm.PyNode(space)
                for space in self.options.spaces.split(';')
            ],
            labels=self.options.labels.split(';'),
            parent_label=self.options.parent_label,
            applied_space=self.options.default_space,
            translation_only=self.options.translation_only,
            rotation_only=self.options.rotation_only,
            target_offsets=target_offsets,
        )

    # --------------------------------------------------------------------------
    @classmethod
    def create(cls,
               description,
               side,
               target,
               spaces,
               labels,
               applied_space,
               parent_label,
               translation_only=False,
               rotation_only=False,
               target_offsets=None):

        # -- If there are no labels then we extract the description
        # -- from each space and use that as the labels
        if not labels:
            labels = [
                crab.config.get_description(space)
                for space in spaces
            ]

        if not target_offsets:
            target_offsets = dict()

        # -- This change allows us to specify the name (label) assigned
        # -- to the default parent space, making it easier to identify
        # -- for animators.
        default_space = crab.utils.hierarchy.find_above(target, crab.config.ORG)
        spaces.insert(0, default_space)
        labels.insert(0, parent_label)

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

            # -- Check if we have a target offset for this space, if we
            # -- do then we need to move the zero to this target offset
            # -- whilst we make the constraint
            xform_to_restore = None

            if space.name() in target_offsets:

                xform_to_restore = zero.getMatrix()
                zero.setMatrix(
                    target_offsets[space.name()].getMatrix(
                        worldSpace=True,
                    ),
                    worldSpace=True,
                )

            skip_translate = []
            skip_rotate = []

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
                description='%sSpaceSwitch' % description.replace(' ', ''),
                side=side,
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
            if labels[idx] == applied_space:
                default_id = idx

            # -- If we need to restore this zeros transform, do so now
            if xform_to_restore:
                zero.setMatrix(
                    xform_to_restore,
                    worldSpace=True,
                )

        for axis in ['X', 'Y', 'Z']:
            if translation_only:
                zero.attr('rotate%s' % axis).disconnect()

            if rotation_only:
                zero.attr('translate%s' % axis).disconnect()

        # -- Set the default space
        target.spaces.set(default_id)

        return True
