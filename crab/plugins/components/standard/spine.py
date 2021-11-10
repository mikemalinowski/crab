import crab
import itertools
import pymel.core as pm


# ------------------------------------------------------------------------------
class SpineComponent(crab.Component):
    """
    A segment represents a single rig element capable of building
    a guide along with a rig over that guide.
    """

    identifier = 'Core : Biped : Spine'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(SpineComponent, self).__init__(*args, **kwargs)

        # -- General Options
        self.options.description = ''
        self.options.lock = 'sx;sy;sz'
        self.options.hide = 'v;sx;sy;sz'

        # -- Spine Specific Options
        self.options.spine_count = 2
        self.options.align_rotations_to_world = True

    # --------------------------------------------------------------------------
    def create_skeleton(self, parent):

        # -- The hip serves as the root joint of the spine, so we start
        # -- with that
        hip = crab.create.joint(
            description='{}Hip'.format(self.options.description),
            side=self.options.side,
            parent=parent,
            match_to=parent,
        )

        # -- As this is the root joint for the component we need to mark it
        # -- as such. This allows us to begin tagging objects against this component
        self.mark_as_skeletal_root(hip)

        # -- Tags are used as a mechanism for other functions of a component (such
        # -- as guide or rig build functions) to search for an object without knowing
        # -- its actual name. Other tools can also harness the power of tags too.
        self.tag(
            target=hip,
            label='SkeletalHip',
        )

        # -- Set the translation  of the hip. You can just hard code some default
        # -- values, and when writing your own components, if you know the up axis
        # -- is always Y or always Z you do not need to 'resolve_translation'. This
        # -- simply wrangles the vector to allow it to work in both Y up and Z up
        # -- maya configurations.
        hip.setTranslation(
            crab.utils.transform.resolve_translation(
                [
                    0,
                    100,
                    0,
                ],
            ),
            space='object',
        )

        # -- We will now cycle the spine joints and create them sequentially, starting
        # -- with the hip as the parent
        parent_joint = hip

        for n in range(self.options.spine_count + 1):

            # -- Our label is Spine unless its the last one, in which we know
            # -- we're dealing with the chest
            label = 'Spine' if n < self.options.spine_count else 'Chest'

            # -- Create the spine joint - we can allow crab to do the counting
            # -- for us automatically for the name
            spine = crab.create.joint(
                description='{}{}'.format(self.options.description, label),
                side=self.options.side,
                parent=parent_joint,
                match_to=parent_joint,
            )

            # -- Tag this as a spine joint
            self.tag(
                target=spine,
                label='Skeletal{}'.format(label),
            )

            # -- Now translate the joint up
            spine.setTranslation(
                crab.utils.transform.resolve_translation(
                    [
                        0,
                        20,
                        0,
                    ],
                ),
                space='object',
            )

            # -- Update the parent_joint variable so the next spine
            # -- joint to be made is a child of this one
            parent_joint = spine

        # -- Finally we select the last created joint, as this makes it easier
        # -- for the user to add further joints.
        pm.select(parent_joint)

        # -- We must return True otherwise crab will assume something has failed and
        # -- stop.
        return True

    # --------------------------------------------------------------------------
    def create_rig(self, parent):

        # -- We shall be creating a series of controls throughout this function, and
        # -- many of those will have similar arguments. To make the code overhead shorter
        # -- I am placing those arguments in a dictionary so i can pass them using **kwargs
        consistent_options = dict(
            side=self.options.side,
            lock_list=self.options.lock,
            hide_list=self.options.hide,
        )

        # -- We start by creating our main control - crab will have created a component
        # -- node internally already for us. Note that we're using the tagging mechanism
        # -- to find the joint which we want to match to.
        hip = crab.create.control(
            description='{}Hip'.format(self.options.description),
            parent=parent,
            match_to=self.find_first('SkeletalHip'),
            shape='builtin_hip',
            **consistent_options
        )

        # -- If we need to create the controls using world rotation alignment
        # -- lets do that before we create any further controls.
        if self.options.align_rotations_to_world:
            crab.utils.hierarchy.get_org(hip).setRotation(
                pm.dt.Quaternion(),
                worldSpace=True,
            )

        # -- Create the hip swivel. This allows for the hip joint to be manipulated
        # -- without the spine joints being affected
        swivel = crab.create.control(
            description='{}HipSwivel'.format(self.options.description),
            parent=hip,
            match_to=hip,
            shape='builtin_hipswivel',
            **consistent_options
        )

        # -- We need to constrain the skeletal joint to the control. We use a specific
        # -- crab function to do this, as it creates the constraint but also ties some
        # -- metadata between them to allow crab to understand that any further joints
        # -- which are not part of this component should be parented under this control
        self.bind(
            self.find_first('SkeletalHip'),
            swivel,
            maintainOffset=True,
        )

        # -- Now we need to find the rest of the spine joints and the chest. We can
        # -- deal with all of these in the same consistent way
        further_joints = self.find('SkeletalSpine')
        further_joints.extend(self.find('SkeletalChest'))

        # -- We will create these controls sequentially - so we track the
        # -- current parent
        control_parent = hip

        for joint in further_joints:

            # -- Each joint will have two controls, that way the spine can
            # -- be manipulated hierarchically, as well as having the ability
            # -- to manipulate a spine joint without the children being affected.

            # -- Create the control for this joint - notice how we can ask crab
            # -- to extract most of the information from the joint itself
            control = crab.create.control(
                description=crab.config.get_description(joint),
                parent=control_parent,
                match_to=joint,
                shape='builtin_spine',
                **consistent_options
            )

            # -- Create a swivel visibility attribute, but start by adding
            # -- an attribute separator
            crab.utils.organise.add_separator_attr(control)

            control.addAttr(
                'showSwivel',
                at='bool',
                dv=False,
                k=True,
            )

            # -- If we need to create the controls using world rotation alignment
            # -- lets do that before we create any further controls.
            if self.options.align_rotations_to_world:
                crab.utils.hierarchy.get_org(control).setRotation(
                    pm.dt.Quaternion(),
                    worldSpace=True,
                )

            # -- Create our swivel control
            control_swivel = crab.create.control(
                description='{}Swivel'.format(crab.config.get_description(joint)),
                parent=control,
                match_to=control,
                shape='buitlin_spineswivel',
                **consistent_options
            )

            # -- Hook up the visibility property
            control.showSwivel.connect(control_swivel.visibility, lock=True)

            # -- Bind the joint to the control to allow the joint to follow the
            # -- control, anda to ensure crab understands this is the control that
            # -- and subsequent components should be parented off if any components
            # -- are made a child of it
            self.bind(
                joint,
                control_swivel,
                maintainOffset=True,
            )

            # -- Update the control_parent variable to ensure the next control
            # -- we build will be a child of this one
            control_parent = control

        # -- Finally we return True to ensure crab knows we fully succeeded in building
        # -- the rig component
        return True

