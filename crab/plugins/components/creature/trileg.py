import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class TriLegComponent(crab.Component):
    """
    Creates a tri leg (dog leg, dinosaur leg etc)
    """

    identifier = 'Core : Creature : Tri Leg'

    def __init__(self, *args, **kwargs):
        super(TriLegComponent, self).__init__(*args, **kwargs)

        self.upper_twists = 0
        self.mid_twists = 0
        self.lower_twists = 0

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
        # -- The hip serves as the root joint of the spine, so we start
        # -- with that. We can just use maya.cmds.joint to create our joints
        # -- but we'll use the crab creation methods, as they auto generate
        # -- the correct naming for the joints
        upper_leg = crab.create.joint(
            description='{}UpperLeg'.format(self.options.description),
            side=self.options.side,
            parent=parent,
        )

        # -- We could use normal maya transform methods, but crab offers
        # -- some utility functionality, so lets make sure of it
        crab.utils.transform.apply(
            node=upper_leg,
            ty=100,
            rx=90,
            ry=-30.53,
            rz=-90,
        )

        lower_leg = crab.create.joint(
            description='{}LowerLeg'.format(self.options.description),
            side=self.options.side,
            parent=upper_leg,
        )

        crab.utils.transform.apply(
            node=lower_leg,
            tx=45.277,
            rx=0,
            rz=-72.803,
        )

        ankle = crab.create.joint(
            description='{}Ankle'.format(self.options.description),
            side=self.options.side,
            parent=lower_leg,
        )

        crab.utils.transform.apply(
            node=ankle,
            tx=44.598,
            rx=180,
            rz=56.31,
        )

        foot = crab.create.joint(
            description='{}Foot'.format(self.options.description),
            side=self.options.side,
            parent=ankle,
        )

        crab.utils.transform.apply(
            node=foot,
            tx=28.862,
            rz=-75.964,
        )

        toe = crab.create.joint(
            description='{}Toe'.format(self.options.description),
            side=self.options.side,
            parent=foot,
        )

        crab.utils.transform.apply(
            node=toe,
            tx=12,
            ry=90,
        )

        # -- We need to mark the joint that is the root joint - this ensures that
        # -- crab understands that this is the root of the component
        self.mark_as_skeletal_root(upper_leg)

        # -- Now we need to tag all of our joints so we can easily access
        # -- them in the control rig phase. Tagging is a convenient way of being
        # -- able to access specific nodes within a component regardless of how
        # -- they are named.
        self.tag(upper_leg, 'SkeletonUpperLeg')
        self.tag(lower_leg, 'SkeletonLowerLeg')
        self.tag(ankle, 'SkeletonAnkle')
        self.tag(foot, 'SkeletonFoot')
        self.tag(toe, 'SkeletonToe')

        return True

    # ------------------------------------------------------------------------------
    def create_rig(self, parent):
        """
        This function is called every time the rig build process is invoked. We
        must build the control rig, and connect our skeleton joints to the control
        rig.

        :param parent: The parent node we should nest our control rig elements
         under

        :return: True if we built successfully
        """
        # -- Start by creating an organisational node which we
        # -- will then place everything under - this is not a
        # -- requirement, but it does keep things tidy.
        org = crab.create.org(
            description=self.options.description,
            side=self.options.side,
            parent=parent,
        )

        # -- We need to create a doubled hierarchy for this particular
        # -- setup, so we need to duplicate the skl hierarchy.
        spring_chain = crab.utils.joints.replicate_chain(
            from_this=self.find_first('SkeletonUpperLeg'),
            to_this=self.find_first('SkeletonToe'),
            parent=org,
            replacements={
                'SKL_': 'SPR_',
            },
        )

        rp_chain = crab.utils.joints.replicate_chain(
            from_this=self.find_first('SkeletonUpperLeg'),
            to_this=self.find_first('SkeletonToe'),
            parent=spring_chain[0],
            replacements={
                'SKL_': 'RP_',
            },
        )

        # -- Move all rotations to orients - this ensures the IK solve
        # -- will calculate the correct rotation angles
        joints = spring_chain[:]
        joints.extend(rp_chain)
        pm.select(joints)
        crab.tools.rigging().request('joints_oriswitch_rotations_to_orients')().run()


        # -- Create the controller that stores all the attribute
        # -- information. We create this early so we can drive
        # -- controls with it
        config_control = crab.create.control(
            description='%sConfig' % self.options.description,
            side=self.options.side,
            parent=org,
            match_to=rp_chain[0],
            shape='config',
            lock_list='sx;sy;sz;ty;tz;tz;rx;ry;rz',
            hide_list='sx;sy;sz;ty;tz;tz;rx;ry;rz;v',
        )
        config_control.addAttr('ikfk', at='float', dv=0, k=True, min=0, max=1)
        config_control.addAttr('ik_vis', at='float', dv=1, k=True, min=0, max=1)
        config_control.addAttr('fk_vis', at='float', dv=0, k=True, min=0, max=1)

        # -- Lets start by creating a control to adjust/manipulate the
        # -- upper leg joint. By using the crab utility function to create
        # -- our controls we are guaranteed a crab control hierarchy, which other
        # -- tools and behaviours (such as space switches) are reliant upon.
        upper_joint_manipulator = crab.create.control(
            description=crab.config.get_description(spring_chain[0]),
            side=crab.config.get_side(spring_chain[0]),
            parent=org,
            match_to=spring_chain[0],
            shape='paddle',
        )

        pm.parentConstraint(
            upper_joint_manipulator,
            spring_chain[0],
            maintainOffset=False,
        )

        # -- Now create the foot control
        foot_control = crab.create.control(
            description='{}Foot'.format(self.options.description),
            side=self.options.side,
            parent=org,
            match_to=self.find_first('SkeletonFoot'),
            shape='foot'
        )
        config_control.attr('ik_vis').connect(foot_control.attr('visibility'))

        # -- The reverse foot control acts like a heel control
        reverse_foot_control = crab.create.control(
            description='{}ReverseFoot'.format(self.options.description),
            side=self.options.side,
            parent=foot_control,
            match_to=self.find_first('SkeletonToe'),
            shape='rocker',
            lock_list='tx;ty;tz;sx;sy;sz',
            hide_list='tx;ty;tz;sx;sy;sz;v',
        )
        config_control.attr('ik_vis').connect(reverse_foot_control.attr('visibility'))

        # -- Scale up the control
        crab.utils.shapes.scale(
            reverse_foot_control,
            uniform=crab.utils.maths.distance_between(
                spring_chain[-1],
                spring_chain[-2],
            )
        )

        # -- The final control is the toe
        toe_control = crab.create.control(
            description = '{}Toe'.format(self.options.description),
            side=self.options.side,
            parent=foot_control,
            match_to=self.find_first('SkeletonToe'),
            shape='rocker',
            lock_list='tx;ty;tz;sx;sy;sz',
            hide_list='tx;ty;tz;sx;sy;sz;v',
        )
        config_control.attr('ik_vis').connect(toe_control.attr('visibility'))

        # -- Invert the toe rocker control
        crab.utils.shapes.scale(
            toe_control,
            z=-1,
        )

        pm.parentConstraint(
            toe_control,
            rp_chain[-1],
            skipTranslate=['x','y','z'],
        )

        # -- Create the spring solver upvector
        spring_solver_pivot = crab.create.generic(
            node_type='transform',
            prefix=crab.config.PIVOT,
            description='{}ForwardLeg'.format(self.options.description),
            side=self.options.side,
            parent=foot_control,
            match_to=foot_control,
        )

        # -- Create the spring solver upvector
        spring_solver_upvector = crab.create.control(
            description='{}ForwardLegUpvector'.format(self.options.description),
            side=self.options.side,
            parent=spring_solver_pivot,
            shape='sphere'
        )

        # -- Place the upvector along the chain plane
        spring_solver_upvector.setTranslation(
            crab.utils.maths.calculate_upvector_position(
                spring_chain[0],
                spring_chain[1],
                spring_chain[2],
            ),
            worldSpace=True,
        )

        # -- Now create the ik solvers
        pm.mel.eval('ikSpringSolver;')

        spring_solver = crab.create.ik.simple_ik(
            start=spring_chain[0],
            end=spring_chain[-2],
            description='{}SpringSolver'.format(self.options.description),
            side=self.options.side,
            parent=reverse_foot_control,
            visible=False,
            solver='ikSpringSolver',
            polevector=spring_solver_upvector
        )

        # -- Create the ankle solver upvector
        ankle_solver_pivot = crab.create.generic(
            node_type='transform',
            prefix=crab.config.PIVOT,
            description='{}Ankle'.format(self.options.description),
            side=self.options.side,
            parent=foot_control,
            match_to=foot_control,
        )

        # -- Create the ankle solver upvector
        ankle_solver_upvector = crab.create.control(
            description='{}AnkleUpvector'.format(self.options.description),
            side=self.options.side,
            parent=ankle_solver_pivot,
            shape='sphere',
        )
        config_control.attr('ik_vis').connect(ankle_solver_upvector.attr('visibility'))

        ankle_solver_upvector.setTranslation(
            crab.utils.maths.calculate_upvector_position(
                rp_chain[1],
                rp_chain[2],
                rp_chain[3],
            ),
            worldSpace=True,
        )

        # -- Now create the ik solvers
        ankle_solver = crab.create.ik.simple_ik(
            start=rp_chain[1],
            end=rp_chain[-2],
            description='{}AnkleSolver'.format(self.options.description),
            side=self.options.side,
            parent=spring_solver,
            visible=False,
            solver='ikRPsolver',
            polevector=ankle_solver_upvector
        )

        # -- Next we create the IK Toe solver
        toe_solver = crab.create.ik.simple_ik(
            start=rp_chain[-2],
            end=rp_chain[-1],
            description='{}ToeSolver'.format(self.options.description),
            side=self.options.side,
            parent=reverse_foot_control,
            visible=False,
            solver='ikSCsolver',
        )

        # -- Add the attributes to the foot control
        crab.utils.organise.add_separator_attr(foot_control)

        for attr_name in ['heelBias', 'kneeRoll', 'ankleRoll']:
            foot_control.addAttr(
                attr_name,
                at='float',
                k=True,
            )

        # -- Hook up the attributes
        foot_control.heelBias.connect(
            rp_chain[0].rotateZ,
        )

        foot_control.kneeRoll.connect(
            spring_solver_pivot.rotateY,
        )

        foot_control.ankleRoll.connect(
            ankle_solver_pivot.rotateY,
        )

        # -- Now we need to build the FK controllers
        fk_parent = org
        blend_parent = org
        blends = list()

        for ik_joint in rp_chain:

            # -- Create the fk control
            fk_control = crab.create.control(
                description='FK' + crab.config.get_description(ik_joint),
                side=self.options.side,
                parent=fk_parent,
                match_to=ik_joint,
                shape='paddle',
                lock_list='sx;sy;sz;ty;tz',
                hide_list='sx;sy;sz;ty;tz;v',
            )
            config_control.attr('fk_vis').connect(fk_control.attr('visibility'))

            # -- Now create the blend transforms
            blend_transform = crab.create.generic(
                node_type='transform',
                prefix=crab.config.MECHANICAL,
                description='Blend' + crab.config.get_description(ik_joint),
                parent=blend_parent,
                side=self.options.side,
            )
            blends.append(blend_transform)

            # -- Constrain the blend transform between the fk
            # -- and the ik control
            pm.parentConstraint(
                ik_joint,
                blend_transform,
                mo=False,
            )

            # -- Create the constraint setup between the IK and the FK
            cns = pm.parentConstraint(
                fk_control,
                blend_transform,
                mo=False,
            )

            cns.interpType.set(2)  # -- Shortest interpolation

            # -- Hook up the IK constraint blend - which needs reversing
            reverse_node = pm.createNode('reverse')
            config_control.attr('ikfk').connect(reverse_node.inputX)
            reverse_node.outputX.connect(cns.getWeightAliasList()[0])

            # -- Hook up the FK constraint blend, which is direct
            config_control.attr('ikfk').connect(cns.getWeightAliasList()[1])

            # -- Redefine the parent variables
            fk_parent = fk_control
            blend_parent = blend_transform

        # -- Finally perform the binding - this constraints the relevent skeletal nodes
        # -- to the nodes in our control rig - but crucially the binding informs crab what
        # -- control any child component control rigs should use as their parent.
        self.bind(
            self.find_first('SkeletonUpperLeg'),
            blends[0],
        )
        self.bind(
            self.find_first('SkeletonLowerLeg'),
            blends[1],
        )
        self.bind(
            self.find_first('SkeletonAnkle'),
            blends[2],
        )
        self.bind(
            self.find_first('SkeletonFoot'),
            blends[3],
        )
        self.bind(
            self.find_first('SkeletonToe'),
            blends[4],
        )

        return True

    # --------------------------------------------------------------------------
    def link_guide(self):
        """
        This should perform the required steps to have the skeletal
        structure driven by the guide (if the guide is implemented). This
        will then be triggered by Rig.edit process.

        We use this function to lock the axis of the skeleton which we
        need to be zero'd in order for IK to work properly.

        :return: None
        """
        tags = [
            'SkeletonLowerLeg',
            'SkeletonAnkle',
            'SkeletonFoot',
            'SkeletonToe',
        ]

        for tag in tags:

            # -- Get the
            joint = self.find_first(tag)

            if joint:
                joint.translateY.lock()
                joint.translateZ.lock()
                joint.rotateX.lock()
                joint.rotateY.lock()

        return True

    # --------------------------------------------------------------------------
    def unlink_guide(self):
        """
        This should perform the operation to unlink the guide from the
        skeleton, leaving the skeleton completely free of any ties
        between it and the guide.

        This is run as part of the Rig.build process.

        We use this to ensure any locks we placed previously are unlocked
        before the control rig is built.

        :return: None
        """
        tags = [
            'SkeletonLowerLeg',
            'SkeletonAnkle',
            'SkeletonFoot',
            'SkeletonToe',
        ]

        for tag in tags:

            # -- Get the
            joint = self.find_first(tag)

            if joint:
                joint.translateY.unlock()
                joint.translateZ.unlock()
                joint.rotateX.unlock()
                joint.rotateY.unlock()

        return True
