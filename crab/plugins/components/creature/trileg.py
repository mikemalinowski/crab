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

        self.options.description = ''
        self.options.twist_count = 3
        self.options.mirror = True
        self.options.side = crab.config.LEFT
        self.options.align_foot_to_world = True
        self.options.use_spring_solver = True
        self.options.upvector_distance_multiplier = 0.5
        
        # -- Define our private variables
        self._config_control = None
        self._foot_control = None
        self._foot_tip_control = None
        self._toe_control = None
        self._knee_upv_control = None
        self._ankle_upv_control = None
        self._upper_joint_manipulator = None
        self._reverse_foot_control = None
        
        self._knee_chain = None
        self._knee_solver = None
        self._knee_solver_pivot = None

        self._ankle_chain = None
        self._ankle_solver = None
        self._ankle_solver_pivot = None

        self._blends = list()

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
        if crab.utils.transform.up_axis() == 'y':
            crab.utils.transform.apply(
                node=upper_leg,
                ty=100,
                rx=90,
                ry=-30.53,
                rz=-90,
            )

        else:
            crab.utils.transform.apply(
                node=upper_leg,
                tz=100,
                rx=90,
                ry=59.47,
                rz=0,
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

        # -- Create our twists if we need to
        twist_pairings = [
            [upper_leg, lower_leg],
            [lower_leg, ankle],
            [ankle, foot],
        ]
        rig = crab.get()

        for i in range(self.options.twist_count):

            for root, tip in twist_pairings:

                component = rig.add_component(
                    'Utility : Twist',
                    parent=root,
                    target_root=root.name(),
                    target_effector=tip.name(),
                    side=self.options.side,
                    description='{}Twist'.format(crab.config.get_description(root))
                )

                joint = component.find_first('TwistJoint')
                v = float(i) / float(self.options.twist_count-1)

                joint.setTranslation(
                    crab.utils.maths.lerp(
                        v1=root.getTranslation(space='world'),
                        v2=tip.getTranslation(space='world'),
                        a=float(i) / float(self.options.twist_count-1),
                    ),
                    space='world',
                )

        # -- Finally, if we need to mirror, set that up now
        if self.options.mirror:

            # -- We need to disable mirroring on the copy, otherwise
            # -- we will cycle indefinitely!
            altered_options = self.options.copy()
            altered_options['mirror'] = False
            altered_options['side'] = crab.config.RIGHT if self.options.side == crab.config.LEFT else crab.config.LEFT

            crab.get().add_component(
                TriLegComponent.identifier,
                **altered_options
            )

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

        skeletal_chain = crab.utils.hierarchy.get_between(
            from_this=self.find_first('SkeletonUpperLeg'),
            to_this=self.find_first('SkeletonToe'),
        )
        print(skeletal_chain)
        
        # -- Create our base controls
        self.create_core_controls(skeletal_chain, org)
        
        # -- Create the spring setup
        self.create_knee_chain(skeletal_chain, org)
        
        self.create_ankle_setup(skeletal_chain, org)

        self.create_toe_setup()

        # -- Drive the knee chain root by the upper joint control
        pm.parentConstraint(
            self._upper_joint_manipulator,
            self._knee_chain[0],
            maintainOffset=False,
        )

        # -- Create and setup the heel and ankle rolls
        self.hookup_roll_attrs()

        # -- Create the FK controls and blending
        self.create_blend_setup(org)

        # -- Finally perform the binding - this constraints the relevent skeletal nodes
        # -- to the nodes in our control rig - but crucially the binding informs crab what
        # -- control any child component control rigs should use as their parent.
        self.bind(
            self.find_first('SkeletonUpperLeg'),
            self._blends[0],
        )
        self.bind(
            self.find_first('SkeletonLowerLeg'),
            self._blends[1],
        )
        self.bind(
            self.find_first('SkeletonAnkle'),
            self._blends[2],
        )
        self.bind(
            self.find_first('SkeletonFoot'),
            self._blends[3],
        )
        self.bind(
            self.find_first('SkeletonToe'),
            self._blends[4],
        )

        return True

    # --------------------------------------------------------------------------
    def create_core_controls(self, skeletal_chain, parent):

        # -- Create the controller that stores all the attribute
        # -- information. We create this early so we can drive
        # -- controls with it
        self._config_control = crab.create.control(
            description='%sConfig' % self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=skeletal_chain[0],
            shape='config',
            lock_list='sx;sy;sz;ty;tz;tz;rx;ry;rz',
            hide_list='sx;sy;sz;ty;tz;tz;rx;ry;rz;v',
        )
        self._config_control.addAttr('ikfk', at='float', dv=0, k=True, min=0, max=1)
        self._config_control.addAttr('ik_vis', at='float', dv=1, k=True, min=0, max=1)
        self._config_control.addAttr('fk_vis', at='float', dv=0, k=True, min=0, max=1)

        # -- Lets start by creating a control to adjust/manipulate the
        # -- upper leg joint. By using the crab utility function to create
        # -- our controls we are guaranteed a crab control hierarchy, which other
        # -- tools and behaviours (such as space switches) are reliant upon.
        self._upper_joint_manipulator = crab.create.control(
            description=crab.config.get_description(skeletal_chain[0]),
            side=crab.config.get_side(skeletal_chain[0]),
            parent=parent,
            match_to=skeletal_chain[0],
            shape='paddle',
        )

        # -- Now create the foot control
        self._foot_control = crab.create.control(
            description='{}Foot'.format(self.options.description),
            side=self.options.side,
            parent=parent,
            match_to=self.find_first('FootGuidePivot'),
            shape='foot'
        )
        self._config_control.attr('ik_vis').connect(self._foot_control.attr('visibility'))

        if self.options.align_foot_to_world:
            crab.utils.hierarchy.get_org(self._foot_control).setRotation(pm.dt.Quaternion(), space='world')

        # -- Now create the foot control
        self._foot_tip_control = crab.create.control(
            description='{}FootTip'.format(self.options.description),
            side=self.options.side,
            parent=self._foot_control,
            match_to=self.find_first('FootTipGuidePivot'),
            shape='sphere'
        )
        self._config_control.attr('ik_vis').connect(self._foot_tip_control.attr('visibility'))

        # -- The reverse foot control acts like a heel control
        self._reverse_foot_control = crab.create.control(
            description='{}ReverseFoot'.format(self.options.description),
            side=self.options.side,
            parent=self._foot_tip_control,
            match_to=self.find_first('SkeletonToe'),
            shape='rocker',
            lock_list='tx;ty;tz;sx;sy;sz',
            hide_list='tx;ty;tz;sx;sy;sz;v',
        )
        self._config_control.attr('ik_vis').connect(self._reverse_foot_control.attr('visibility'))

        # -- Scale up the control
        crab.utils.shapes.scale(
            self._reverse_foot_control,
            uniform=crab.utils.maths.distance_between(
                skeletal_chain[-1],
                skeletal_chain[-2],
            )
        )

        # -- The final control is the toe
        self._toe_control = crab.create.control(
            description = '{}Toe'.format(self.options.description),
            side=self.options.side,
            parent=self._foot_tip_control,
            match_to=self.find_first('SkeletonToe'),
            shape='rocker',
            lock_list='tx;ty;tz;sx;sy;sz',
            hide_list='tx;ty;tz;sx;sy;sz;v',
        )
        self._config_control.attr('ik_vis').connect(self._toe_control.attr('visibility'))

        # -- Invert the toe rocker control
        crab.utils.shapes.scale(
            self._toe_control,
            z=-1,
        )

        # -- Create the ankle solver upvector
        self._ankle_upv_control = crab.create.control(
            description='{}AnkleUpvector'.format(self.options.description),
            side=self.options.side,
            parent=None,
            shape='sphere',
        )
        self._config_control.attr('ik_vis').connect(self._ankle_upv_control.attr('visibility'))

        crab.utils.hierarchy.get_org(self._ankle_upv_control).setTranslation(
            crab.utils.maths.calculate_upvector_position(
                skeletal_chain[1],
                skeletal_chain[2],
                skeletal_chain[3],
                length=self.options.upvector_distance_multiplier,
            ),
            worldSpace=True,
        )

        # -- Create the spring solver upvector
        self._knee_upv_control = crab.create.control(
            description='{}ForwardLegUpvector'.format(self.options.description),
            side=self.options.side,
            parent=None,
            shape='sphere'
        )
        
        self._config_control.attr('ik_vis').connect(self._knee_upv_control.attr('visibility'))

        # -- Place the upvector along the chain plane
        crab.utils.hierarchy.get_org(self._knee_upv_control).setTranslation(
            crab.utils.maths.calculate_upvector_position(
                skeletal_chain[0],
                skeletal_chain[1],
                skeletal_chain[2],
                length=self.options.upvector_distance_multiplier,
            ),
            worldSpace=True,
        )

    # --------------------------------------------------------------------------
    def create_blend_setup(self, parent):

        # -- Now we need to build the FK controllers
        fk_parent = parent
        blend_parent = parent

        for ik_joint in self._ankle_chain:

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
            self._config_control.attr('fk_vis').connect(fk_control.attr('visibility'))

            # -- Now create the blend transforms
            blend_transform = crab.create.generic(
                node_type='transform',
                prefix=crab.config.MECHANICAL,
                description='Blend' + crab.config.get_description(ik_joint),
                parent=blend_parent,
                side=self.options.side,
            )
            self._blends.append(blend_transform)

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
            self._config_control.attr('ikfk').connect(reverse_node.inputX)
            reverse_node.outputX.connect(cns.getWeightAliasList()[0])

            # -- Hook up the FK constraint blend, which is direct
            self._config_control.attr('ikfk').connect(cns.getWeightAliasList()[1])

            # -- Redefine the parent variables
            fk_parent = fk_control
            blend_parent = blend_transform

    # --------------------------------------------------------------------------
    def hookup_roll_attrs(self):

        # -- Add the attributes to the foot control
        crab.utils.organise.add_separator_attr(self._foot_control)

        for attr_name in ['heelBias', 'kneeRoll', 'ankleRoll']:
            self._foot_control.addAttr(
                attr_name,
                at='float',
                k=True,
            )

        # -- Hook up the attributes
        self._foot_control.heelBias.connect(
            self._ankle_chain[0].rotateZ,
        )

        if self.options.align_foot_to_world:
            self._foot_control.kneeRoll.connect(
                self._knee_solver_pivot.attr('r' + crab.utils.transform.up_axis()),
            )

            self._foot_control.ankleRoll.connect(
                self._ankle_solver_pivot.attr('r' + crab.utils.transform.up_axis()),
            )

        else:
            self._foot_control.kneeRoll.connect(
                self._knee_solver_pivot.rotateY,
            )

            self._foot_control.ankleRoll.connect(
                self._ankle_solver_pivot.rotateY,
            )

        return

    # --------------------------------------------------------------------------
    def create_toe_setup(self):

        pm.parentConstraint(
            self._toe_control,
            self._ankle_chain[-1],
            skipTranslate=['x','y','z'],
        )

        # -- Next we create the IK Toe solver
        toe_solver = crab.create.ik.simple_ik(
            start=self._ankle_chain[-2],
            end=self._ankle_chain[-1],
            description='{}ToeSolver'.format(self.options.description),
            side=self.options.side,
            parent=self._reverse_foot_control,
            visible=False,
            solver='ikSCsolver',
        )

    # --------------------------------------------------------------------------
    def create_ankle_setup(self, skeletal_chain, parent):

        self._ankle_chain = crab.utils.joints.replicate_chain(
            from_this=self.find_first('SkeletonUpperLeg'),
            to_this=self.find_first('SkeletonToe'),
            parent=parent,
            replacements={
                'SKL_': 'ankle_',
            },
        )

        # -- Move all rotations to orients - this ensures the IK solve
        # -- will calculate the correct rotation angles
        pm.select(self._ankle_chain)
        crab.tools.rigging().request('joints_oriswitch_rotations_to_orients')().run()

        # -- Create the ankle solver upvector
        self._ankle_solver_pivot = crab.create.generic(
            node_type='transform',
            prefix=crab.config.PIVOT,
            description='{}Ankle'.format(self.options.description),
            side=self.options.side,
            parent=self._foot_tip_control,
            match_to=self._foot_control,
        )
        
        # -- Parent the control correctly
        crab.utils.hierarchy.get_org(self._ankle_upv_control).setParent(self._ankle_solver_pivot, absolute=True)

        # -- Now create the ik solvers
        self._ankle_solver = crab.create.ik.simple_ik(
            start=self._ankle_chain[1],
            end=self._ankle_chain[-2],
            description='{}AnkleSolver'.format(self.options.description),
            side=self.options.side,
            parent=self._knee_solver,
            visible=False,
            solver='ikRPsolver',
            polevector=self._ankle_upv_control,
        )

        self._ankle_chain[0].setParent(self._knee_chain[0])

    # --------------------------------------------------------------------------
    def create_knee_chain(self, skeletal_chain, parent):
        """
        This is the main three joint ik
        """
        # -- We need to create a doubled hierarchy for this particular
        # -- setup, so we need to duplicate the skl hierarchy.
        self._knee_chain = crab.utils.joints.replicate_chain(
            from_this=self.find_first('SkeletonUpperLeg'),
            to_this=self.find_first('SkeletonFoot'),
            parent=parent,
            replacements={
                'SKL_': 'SPR_',
            },
        )

        # -- Move all rotations to orients - this ensures the IK solve
        # -- will calculate the correct rotation angles
        pm.select(self._knee_chain)
        crab.tools.rigging().request('joints_oriswitch_rotations_to_orients')().run()

        # -- Now create the ik solvers
        pm.mel.eval('ikSpringSolver;')

        # -- Create the spring solver upvector
        self._knee_solver_pivot = crab.create.generic(
            node_type='transform',
            prefix=crab.config.PIVOT,
            description='{}ForwardLeg'.format(self.options.description),
            side=self.options.side,
            parent=self._foot_tip_control,
            match_to=self._foot_control,
        )

        crab.utils.hierarchy.get_org(self._knee_upv_control).setParent(self._knee_solver_pivot, absolute=True)

        self._knee_solver = crab.create.ik.simple_ik(
            start=self._knee_chain[0],
            end=self._knee_chain[-1],
            description='{}KneeSolver'.format(self.options.description),
            side=self.options.side,
            parent=self._reverse_foot_control,
            visible=False,
            solver='ikSpringSolver' if self.options.use_spring_solver else 'ikRPsolver',
            polevector=self._knee_upv_control
        )

        return

    def create_guide(self, parent):

        # -- Get a list of the skeletal joints we want to use to
        # -- generate guides from
        foot_joint = self.find_first('SkeletonFoot')
        toe_joint = self.find_first('SkeletonToe')

        pm.parentConstraint(
            toe_joint,
            parent,
            mo=False,
        )

        # -- Define our common options
        options = dict(
            side=self.options.side,
            parent=parent,
        )

        inv = 1.0
        if self.options.side == crab.config.RIGHT:
            inv = -1.0

        foot_pivot = crab.create.guide(
            description='%sFootGuidePivot' % self.options.description,
            match_to=toe_joint,
            **options
        )
        self.tag(foot_pivot, 'FootGuidePivot')

        foot_pivot = crab.create.guide(
            description='%sFootTipGuidePivot' % self.options.description,
            translation_offset=[0.0, 0.0, 5.0],
            match_to=toe_joint,
            **options
        )
        self.tag(foot_pivot, 'FootTipGuidePivot')

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
        # tags = [
        #     'SkeletonLowerLeg',
        #     'SkeletonAnkle',
        #     'SkeletonFoot',
        #     'SkeletonToe',
        # ]
        #
        # for tag in tags:
        #
        #     # -- Get the
        #     joint = self.find_first(tag)
        #
        #     if joint:
        #         joint.translateY.lock()
        #         joint.translateZ.lock()
        #         joint.rotateX.lock()
        #         joint.rotateY.lock()

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
                for attr in crab.utils.transform.transform_attrs():
                    joint.attr(attr).unlock()
                    joint.attr(attr).disconnect()
                print('unlcoked : %s' % joint)
            else:
                print('no dice : %s' % tag)
        pm.refresh()
        return True
