import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class SingularComponent(crab.Component):
    """
    A segment represents a single rig element capable of building
    a guide along with a rig over that guide.
    """

    identifier = 'Singular'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(SingularComponent, self).__init__(*args, **kwargs)

        self.options.lock = ''
        self.options.hide = ''

    # --------------------------------------------------------------------------
    def create_skeleton(self, parent):
        """
        This should create your guide representation for your segment.
        The parent will be a pre-constructed crabSegment transform node.

        :param parent:  
        :return: 
        """
        # -- Create the joint for this singular
        root_joint = crab.utils.create(
            node_type='joint',
            prefix=crab.config.SKELETON,
            description=self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=parent,
        )

        # -- Define this joint as being the skeleton root for
        # -- this component
        self.define_skeleton_root(root_joint)

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
    def create_rig(self, parent, skeleton_component):

        # -- We're given the skeleton component instance, so we can
        # -- utilise the find method to find the joint we need to build
        # -- a control against
        root_joint = skeleton_component.find('RootJoint')[0]

        # -- Create a transform to use as a control
        node = crab.utils.create(
            node_type='transform',
            prefix=crab.config.CONTROL,
            description=self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=root_joint,
        )

        # -- All joints should have a binding. The binding allows crab
        # -- to know what control parent to utilise when building skeletal
        # -- components.
        # -- The act of binding also constrains the skeleton joint to the
        # -- control
        self.bind(
            root_joint,
            node,
        )

        # -- Select our tip joint
        pm.select(node)
