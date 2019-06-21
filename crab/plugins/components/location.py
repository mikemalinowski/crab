import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class LocationComponent(crab.Component):
    """
    A segment represents a single rig element capable of building
    a guide along with a rig over that guide.
    """

    identifier = 'Location'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(LocationComponent, self).__init__(*args, **kwargs)

        self.options.description = 'Location'
        self.options.lock = 'sx;sy;sz'
        self.options.hide = 'v;sx;sy;sz'

    # --------------------------------------------------------------------------
    def create_skeleton(self, parent):
        """
        This should create your guide representation for your segment.
        The parent will be a pre-constructed crabSegment transform node.

        :param parent:
        :return:
        """
        # -- Create the joint for this singular
        root_joint = crab.create.generic(
            node_type='joint',
            prefix=crab.config.SKELETON,
            description='%s' % self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=parent,
        )

        # -- Define this joint as being the skeleton root for
        # -- this component
        self.mark_as_skeletal_root(root_joint)

        # -- We'll tag this joint with a label so we can easily
        # -- find it from within the create_rig function.
        self.tag(
            target=root_joint,
            label='RootJoint'
        )

        # -- Select the tip joint
        pm.select(root_joint)

        return True

    # --------------------------------------------------------------------------
    def create_rig(self, parent):

        # -- We're given the skeleton component instance, so we can
        # -- utilise the find method to find the joint we need to build
        # -- a control against
        root_joint = self.find_first('RootJoint')

        # -- Create a transform to use as a control
        root_control = crab.create.control(
            description='Rig%s' % self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=root_joint,
            shape='cog',
            lock_list=self.options.lock,
            hide_list=self.options.hide,
        )

        location_control = crab.create.control(
            description='%s' % self.options.description,
            side=self.options.side,
            parent=root_control,
            match_to=root_control,
            shape='arrow_z',
            lock_list=self.options.lock,
            hide_list=self.options.hide,
        )

        # -- All joints should have a binding. The binding allows crab
        # -- to know what control parent to utilise when building skeletal
        # -- components.
        # -- The act of binding also constrains the skeleton joint to the
        # -- control
        self.bind(
            root_joint,
            root_control,
            constrain=False,
        )

        # -- Constrain the joint to the location
        pm.parentConstraint(
            location_control,
            root_joint,
            mo=False,
        )

        # -- Select our tip joint
        pm.select(root_control)
