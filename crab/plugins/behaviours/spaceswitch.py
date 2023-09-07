import os
import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class SpaceSwitch(crab.Behaviour):
    """
    This is meant as an example only to show how a behaviour
    can operate
    """
    identifier = "SpaceSwitch"
    version = 1

    dict(
        target="The name of the control which you want to add the spaceswitch to",
        spaces="A list of target objects which should act as spaces",
        labels="A list of labels to make up the space switch attribute. This should be in the same order as the Spaces option",
        translation_only="If ticked, the rotation of the target will not be affected",
        rotation_only="If ticked, the translation of the target will not be affected",
        default_space="This should be an entry specified in \"labels\" (or Parent Label) and defines which space is active by default",
        parent_label="All space switches expose their parent as a space, how do you want to label this?",
        target_offsets="This can be used to define the specific location the target should jump to when active in this space. This should be in the form of Label=Node;Label=Node;"
    )

    preview = os.path.join(
        os.path.dirname(__file__),
        "spaceswitch.gif",
    )

    REQUIRED_NODE_OPTIONS = ["target", "spaces"]

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(SpaceSwitch, self).__init__(*args, **kwargs)

        self.options.target = ""
        self.options.spaces = ""
        self.options.labels = ""
        self.options.translation_only = False
        self.options.rotation_only = False
        self.options.default_space = ""
        self.options.parent_label = "Parent"
        self.options.target_offsets = ""
        self.options.include_scale = False

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        # -- Get a list of any target offsets
        labels = [str(label) for label in self.options.labels.split(";") if label]
        spaces = [space for space in self.options.spaces.split(";") if space]
        target_offsets = [None for _ in spaces]

        for target_data in self.options.target_offsets.split(";"):
            if "=" in target_data:
                target, offset = target_data.split("=")

                # -- If the target is a label rather than an objectd
                # -- we just need to get the object from the label
                if target in labels:
                    idx = labels.index(target)

                else:
                    # -- Assign the offset to the offset list
                    idx = spaces.index(target)

                target_offsets[idx] = pm.PyNode(offset)

        self.create(
            description=self.options.description,
            side=self.options.side,
            target=pm.PyNode(self.options.target),
            spaces=[
                pm.PyNode(space)
                for space in spaces
            ],
            labels=self.options.labels.split(";"),
            parent_label=self.options.parent_label,
            applied_space=self.options.default_space,
            translation_only=self.options.translation_only,
            rotation_only=self.options.rotation_only,
            target_offsets=target_offsets,
            include_scale=self.options.include_scale,
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
               target_offsets=None,
               include_scale=False):

        # -- If there are no labels then we extract the description
        # -- from each space and use that as the labels
        if not labels:
            labels = [
                crab.config.get_description(space)
                for space in spaces
            ]

        if not target_offsets:
            target_offsets = [None for _ in spaces]

        # -- This change allows us to specify the name (label) assigned
        # -- to the default parent space, making it easier to identify
        # -- for animators.
        default_space = crab.utils.hierarchy.find_above(target, crab.config.ORG)
        spaces.insert(0, default_space)
        labels.insert(0, parent_label)
        target_offsets.insert(0, None)

        # -- Add a spacer attribute
        crab.utils.organise.add_separator_attr(target)

        # -- Add the space switch attribute
        target.addAttr(
            "spaces",
            at="enum",
            enumName=":".join(labels),
            k=True,
        )
        space_attr = target.attr("spaces")
        default_id = 0

        zero = crab.utils.hierarchy.find_above(target, crab.config.ZERO)

        for idx, space in enumerate(spaces):

            # -- Check if we have a target offset for this space, if we
            # -- do then we need to move the zero to this target offset
            # -- whilst we make the constraint
            xform_to_restore = None

            if target_offsets[idx]:

                # -- Create a unique transform, as target offsets allow
                # -- for multi use
                space = crab.create.generic(
                    node_type="transform",
                    prefix=crab.config.MARKER,
                    description=crab.config.get_description(target),
                    side=crab.config.get_side(target),
                    parent=space,
                    match_to=target_offsets[idx],
                )

                xform_to_restore = zero.getMatrix()
                zero.setMatrix(
                    space.getMatrix(
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

            scale_cns = None
            if include_scale:
                scale_cns = pm.scaleConstraint(
                    space,
                    zero,
                    maintainOffset=False,
                )

            # -- Create the condition node
            condition = crab.create.generic(
                node_type="condition",
                prefix=crab.config.LOGIC,
                description="%sSpaceSwitch" % description.replace(" ", ""),
                side=side,
            )
            space_attr.connect(condition.firstTerm)
            condition.secondTerm.set(idx)

            # -- Set the various possible output values
            condition.colorIfTrueR.set(1)
            condition.colorIfFalseR.set(0)

            # -- Hook the condition into the constraint
            condition.outColorR.connect(cns.getWeightAliasList()[-1])

            if scale_cns:
                condition.outColorR.connect(scale_cns.getWeightAliasList()[-1])

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

        for axis in ["X", "Y", "Z"]:
            if translation_only:
                zero.attr("rotate%s" % axis).disconnect()

            if rotation_only:
                zero.attr("translate%s" % axis).disconnect()

        # -- Set the default space
        target.spaces.set(default_id)

        return True

    def can_build(self, available_nodes):
        result = super(SpaceSwitch, self).can_build(available_nodes=available_nodes)

        if not result:
            return False

        for data in self.options.target_offsets.split(";"):
            if "=" in data:
                for node_name, label in data.split("="):
                    if node_name.strip() not in available_nodes:
                        print("Target offset %s cannot be found" % node_name)
                        return False

        return True
