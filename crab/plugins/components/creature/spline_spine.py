import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
class SplineSpineComponent(crab.Component):
    """
    This creates a spline spine component consisting of a variable amount of joints
    and four controls.
    """

    identifier = "Core : Creature : Spline Spine"

    FACING_AXIS = [
        "Positive X",
        "Negative X",
        "Positive Y",
        "Negative Y",
        "Positive Z",
        "Negative Z",
    ]

    UP_AXIS = [
        "Positive Y",
        "Negative Y",
        "Closest Y",
        "Positive Z",
        "Negative Z",
        "Closest Z",
        "Positive X",
        "Negative X",
        "Closest X",
    ]

    def __init__(self, *args, **kwargs):
        super(SplineSpineComponent, self).__init__(*args, **kwargs)

        self.options.description = "Spine"
        self.options.joint_count = 10
        self.options.align_controls_world = True
        self.options.facing_axis = "Positive Y"
        self.options.up_axis = "Positive X"
        self.options.linear_hierarchy = False

        self.options._facing_axis = self.FACING_AXIS
        self.options._up_axis = self.UP_AXIS

    # ----------------------------------------------------------------------------------
    def create_skeleton(self, parent):
        """
        This function is where we need to build the skeleton. This is invoked only
        the first time the component is first added to the rig.

        :param parent: This is given to us by crab, and is the parent node
          for the root joint of this component
        :type parent: pm.nt.Transform

        :return: True if we build successfully.
        """

        # -- Joints in maya always parent under the currently
        # -- selected object. So we will keep track of the parent
        # -- variable, and to start with, this will be the parent
        # -- we"re given by crab.
        joint_parent = parent

        # -- Lets start by creating our joint elements
        for idx in range(self.options.joint_count):

            # -- Joints in maya are always parented under
            current_joint = crab.create.joint(
                self.options.description,
                self.options.side,
                parent=joint_parent,
                is_deformer=True,
            )

            # -- Translate the joint upward
            attr_name = "translate%s" % crab.utils.transform.up_axis().upper()
            offset = 100.0 / (self.options.joint_count - 1)
            current_joint.attr(attr_name).set(offset)

            # -- If this was our first joint, we need to tag it as
            # -- such
            if idx == 0:
                self.mark_as_skeletal_root(current_joint)

            # -- We tag the joint so we can easily access them later
            self.tag(
                current_joint,
                "SkeletalJoint",
            )

            # -- Mark this current joint as the parent for the next
            # -- joint
            joint_parent = current_joint

        return True

    # ----------------------------------------------------------------------------------
    def link_guide(self):
        """
        The linking of the guide is where we build a guide control rig and link that
        to the guide controls

        :return:
        """
        # -- Get a list of all our skeletal joints
        skeletal_joints = self.find("SkeletalJoint")

        spline_builder = SplineIKSetup(
            description="%sGuide" % self.options.description,
            side=self.options.side,
            joints_to_trace=skeletal_joints,
            parent=self.guide_root(),
            facing_axis=self.options.facing_axis,
            up_axis=self.options.up_axis,
        )
        spline_builder.create()

        self.tag(
            spline_builder.org,
            "SplineGuideOrg",
        )

        for driver, guide in zip(spline_builder.drivers, self.find("GuideDriver")):

            driver.setMatrix(
                guide.getMatrix(worldSpace=True),
                worldSpace=True,
            )

            # -- Constrain the driver to the guide
            pm.parentConstraint(
                guide,
                driver,
                mo=True,
            )

        for skeleton_joint, mech_joint in zip(skeletal_joints, spline_builder.mechanical_joints):
            print("linking shit")
            pm.parentConstraint(
                mech_joint,
                skeleton_joint,
            )

    # ----------------------------------------------------------------------------------
    def unlink_guide(self):
        """
        When we unlink the guide we are essentially removing the guide control rig
        from the scene. Note that we leave the actual guide controls alone - as these
        are the authority for placement.

        :return:
        """
        # -- triggered on build?
        for spline_guide in self.find("SplineGuideOrg"):
            print("Removing guide spline : %s" % spline_guide)
            pm.delete(spline_guide)

        print("unlinking guide")

    # ----------------------------------------------------------------------------------
    def create_guide(self, parent):
        """
        This particular component uses a guide rather than allowing the rigger
        to manipulate the joints directly. We use a guide because if the joints
        are directly manipulated then we may not be able to achieve a spline that
        is capable of representing the transforms.

        The actual objects created here though are just the guide controls - as
        these are the only nodes we need to be persistent. The benefit of building
        the guide spline setup in the link_guide function is that it is rebuilt
        each time we put the rig into edit mode - meaning it can be kept up to date
        with any control rig changes.

        :param parent:

        :return:
        """

        # -- Get the skeletal joints
        skeletal_joints = self.find("SkeletalJoint")

        # -- Create base guide
        base_guide = crab.create.guide(
            description="%sBase" % self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=skeletal_joints[0],
        )
        self.tag(
            base_guide,
            "GuideDriver",
        )

        # -- Create base guide child
        base_tweak_guide = crab.create.guide(
            description="%sBaseTweaker" % self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=skeletal_joints[(int(len(skeletal_joints) / 3) * 1)],
        )
        self.tag(
            base_tweak_guide,
            "GuideDriver",
        )

        # -- Create base guide child
        tip_tweak_guide = crab.create.guide(
            description="%sTipTweaker" % self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=skeletal_joints[(int(len(skeletal_joints) / 3) * 2)],
        )
        self.tag(
            tip_tweak_guide,
            "GuideDriver",
        )

        # -- Create tip guide
        tip_guide = crab.create.guide(
            description="%sTip" % self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=skeletal_joints[-1],
        )
        self.tag(
            tip_guide   ,
            "GuideDriver",
        )

        return True

    # ----------------------------------------------------------------------------------
    def create_rig(self, parent):
        """
        Here we build the actual control rig for the spline spine

        :return:
        """
        print(self.options.facing_axis)
        # -- Get the guide drivers, so we can place them correctly
        guide_drivers = self.find("GuideDriver")

        org = crab.create.org(
            description=self.options.description,
            side=self.options.side,
            parent=parent,
        )

        # -- Create base guide
        master_control = crab.create.control(
            description="%sMaster" % self.options.description,
            side=self.options.side,
            parent=org,
            match_to=guide_drivers[0],
            shape="sphere",
        )

        # -- Create base guide
        base_control = crab.create.control(
            description="%sBase" % self.options.description,
            side=self.options.side,
            parent=master_control,
            match_to=guide_drivers[0],
            shape="sphere",
        )

        # -- Create tip guide
        tip_control = crab.create.control(
            description="%sTip" % self.options.description,
            side=self.options.side,
            parent=master_control,
            match_to=guide_drivers[3],
            shape="sphere",
        )

        # -- Create base guide child
        base_tweak_control = crab.create.control(
            description="%sBaseTweaker" % self.options.description,
            side=self.options.side,
            parent=base_control,
            match_to=guide_drivers[1],
            shape="sphere",
        )

        # -- Create base guide child
        tip_tweak_control = crab.create.control(
            description="%sTipTweaker" % self.options.description,
            side=self.options.side,
            parent=tip_control,
            match_to=guide_drivers[2],
            shape="sphere",
        )

        # -- If we need a linear hierarchy then reparent the controls
        if self.options.linear_hierarchy:
            crab.utils.hierarchy.get_org(tip_tweak_control).setParent(base_tweak_control)
            crab.utils.hierarchy.get_org(tip_control).setParent(tip_tweak_control)

        # -- Tag all our controls - but tag them in the same order
        # -- as the drivers
        self.tag(base_control, "MappedControl")
        self.tag(base_tweak_control, "MappedControl")
        self.tag(tip_tweak_control, "MappedControl")
        self.tag(tip_control, "MappedControl")

        # -- Now constrain the ik spline setup to these controls
        skeletal_joints = self.find("SkeletalJoint")

        spline_builder = SplineIKSetup(
            description=self.options.description,
            side=self.options.side,
            joints_to_trace=skeletal_joints,
            parent=org,
            facing_axis=self.options.facing_axis,
            up_axis=self.options.up_axis,
        )
        spline_builder.create()

        for driver, control in zip(spline_builder.drivers, self.find("MappedControl")):
            pm.parentConstraint(
                control,
                driver,
                mo=False,
            )

        for skeleton_joint, mech_joint in zip(skeletal_joints, spline_builder.mechanical_joints):
            self.bind(
                skeleton_joint,
                mech_joint,
            )

        return True


# --------------------------------------------------------------------------------------
class SplineIKSetup(object):
    """
    Because we build the spline mechanism in both the Guide and the Control
    state, its easier to have all this code seperate from the plugin functions
    themselves.

    TODO: Implement the facing axis and up axis variables
    """

    # ----------------------------------------------------------------------------------
    def __init__(self, description, side, joints_to_trace, parent, facing_axis="Positive Y", up_axis="Positive X"):
        super(SplineIKSetup, self).__init__()

        # -- Store our inputs
        self.description = description
        self.side = side
        self.joints_to_trace = joints_to_trace
        self.parent = parent
        self.facing_axis=SplineSpineComponent.FACING_AXIS.index(facing_axis)
        self.up_axis=SplineSpineComponent.UP_AXIS.index(up_axis)

        # -- Define our outputs
        self.mechanical_joints = list()
        self.drivers = list()
        self.upvectors = list()
        self.pivots = list()
        self.org = None

    # ----------------------------------------------------------------------------------
    def create(self):

        self.org = crab.create.org(
            description=self.description,
            side=self.side,
            parent=self.parent,
        )

        # -- Create a chain replication
        self.mechanical_joints = crab.utils.joints.replicate_chain(
            from_this=self.joints_to_trace[0],
            to_this=self.joints_to_trace[-1],
            parent=self.org,
            world=True,
            replacements={crab.config.SKELETON: crab.config.MECHANICAL}
        )

        # -- Create the IK handle
        ik_handle, curve = crab.create.ik.spline_ik(
            self.mechanical_joints[0],
            self.mechanical_joints[-1],
            self.description,
            self.side,
            parent=self.org,
            visible=False,
            polevector=None,
            createCurve=True,
            rootOnCurve=True,
            parentCurve=True,
            simplifyCurve=True,
            numSpans=1,
            rootTwistMode=False,
            twistType="linear",
        )
        ik_handle.setParent(self.org)

        # -- Name the curve
        curve.rename(
            crab.config.name(
                prefix=crab.config.SPLINE,
                description="%sSplineIK" % self.description,
                side=self.side,
            ),
        )

        # -- Parent the curve under the given parent
        curve.setParent(self.org)

        # -- Now we need to create a cluster for each cv
        for i in range(4):

            # -- Create a cluster from the cv
            pm.select(curve.cv[i])
            cls_handle, cls_xfo = pm.cluster()

            # -- Name the cluster
            cls_xfo.rename(
                crab.config.name(
                    prefix=crab.config.CLUSTER,
                    description="%sSplineCluster" % self.description,
                    side=self.side,
                ),
            )

            # -- Parent it under the same umbrella as the curve
            cls_xfo.setParent(self.parent)

            # -- Create the driver for this item
            driver = crab.create.generic(
                node_type="transform",
                prefix=crab.config.MARKER,
                description=self.description,
                side=self.side,
                parent=self.org,
                match_to=cls_xfo,
            )

            # -- Clusters are a nightmare with pivots, so lets manually set the
            # -- position of the driver before moving the cluster under it
            translation = cls_xfo.getPivots(worldSpace=True)[0]
            driver.setTranslation(translation, space="world")

            # -- Store the driver
            self.drivers.append(driver)

            # -- Make the cluster a child of the driver
            cls_xfo.setParent(driver)

            # -- Check if we need to create an upvector. We only do this for the
            # -- first and last
            if i == 0 or i == 3:

                # -- Create the upvector rotator
                rotator = crab.create.generic(
                    node_type="transform",
                    prefix=crab.config.PIVOT,
                    description="%sUpvRotator" % self.description,
                    side=self.side,
                    parent=driver,
                    match_to=driver,
                )

                # -- Now add the upvector
                upvector = crab.create.generic(
                    node_type="transform",
                    prefix=crab.config.UPVECTOR,
                    description=self.description,
                    side=self.side,
                    parent=rotator,
                    match_to=driver,
                )

                # -- Offset the upvector
                upvector.translateX.set(100)

                # -- Store the upvector so we can access it
                self.upvectors.append(upvector)

        # -- Now we need to set the parenting hierarchy for the
        # -- drivers
        self.drivers[1].setParent(self.drivers[0])
        self.drivers[2].setParent(self.drivers[3])

        # -- Create the upvector setup, start by setting the facing axis
        ik_handle.dForwardAxis.set(self.facing_axis)
        ik_handle.dWorldUpAxis.set(self.up_axis)

        # -- Create the upvector links
        ik_handle.dTwistControlEnable.set(True)
        ik_handle.dWorldUpType.set(2)  # -- Object Up (Start/End)
        self.upvectors[0].attr("worldMatrix[0]").connect(ik_handle.dWorldUpMatrix)
        self.upvectors[1].attr("worldMatrix[0]").connect(ik_handle.dWorldUpMatrixEnd)

        # -- Now we need to hook up the stretch mechanism
        curve_info = pm.createNode("curveInfo")
        curve.getShape().attr("worldSpace[0]").connect(curve_info.inputCurve)

        # -- Create the float math, which allows us to divde the curve
        # -- up
        float_node = pm.createNode("floatMath")
        float_node.attr("operation").set(3)  # Divide
        curve_info.arcLength.connect(float_node.floatA)
        float_node.floatB.set(len(self.mechanical_joints) - 1)

        for idx, mechanical_joint in enumerate(self.mechanical_joints):

            # -- Skip the first bone
            if idx == 0:
                continue

            float_node.outFloat.connect(mechanical_joint.attr("translate%s" % SplineSpineComponent.UP_AXIS[self.up_axis][-1].upper()))

        return True