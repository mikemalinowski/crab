import crab

import pymel.core as pm


class TwistUtility(crab.Component):
    """
    This will create a twist bone between two other bones
    """
    identifier = 'Utility : Twist'

    # ----------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(TwistUtility, self).__init__(*args, **kwargs)

        self.options.target_root = ''
        self.options.target_effector = ''

        self.options.upv_x = 0
        self.options.upv_y = 100
        self.options.upv_z = 0

    # ----------------------------------------------------------------------------------------------
    def create_skeleton(self, parent):

        twist_joint = crab.create.joint(
            description=self.options.description,
            side=self.options.side,
            parent=parent,
        )

        self.mark_as_skeletal_root(twist_joint)
        self.tag(twist_joint, 'TwistJoint')

    # ----------------------------------------------------------------------------------------------
    def create_rig(self, parent):

        start_target = pm.PyNode(self.options.target_root)
        end_target = pm.PyNode(self.options.target_effector)

        # -- Create an organisational structure to manage the local
        # -- space of nodes
        org = crab.create.org(
            description=self.options.description,
            parent=parent,
            side=self.options.side,
        )

        # -- Create the upvector
        upvector = crab.create.generic(
            node_type='transform',
            prefix=crab.config.MARKER,
            description=self.options.description + 'TwistVector',
            parent=org.getParent(),
            match_to=org,
            side=self.options.side,
        )

        upvector.translateX.set(self.options.upv_x)
        upvector.translateY.set(self.options.upv_y)
        upvector.translateZ.set(self.options.upv_z)

        # -- We need to be aiming our structure at the
        # -- end point, as we do not control our general
        # -- transforms
        pm.aimConstraint(
            end_target,
            org,
            offset=[0, 0, 0],
            weight=1,
            aimVector=[1, 0, 0],
            upVector=[0, 1, 0],
            worldUpType='object',
            worldUpObject=upvector.name(),
            worldUpVector=[0, 1, 0],
            maintainOffset=False,
        )

        # -- Create our start and end targets
        start = crab.create.generic(
            node_type='transform',
            prefix=crab.config.MECHANICAL,
            description=self.options.description + 'Start',
            side=self.options.side,
            parent=org,
            match_to=org,
        )

        start.setTranslation(
            start_target.getTranslation(space='world'),
            space='world',
        )

        # -- Constrain the start to the start target
        pm.parentConstraint(
            start_target,
            start,
            maintainOffset=True,
        )

        # -- Create our start and end targets
        end = crab.create.generic(
            node_type='transform',
            prefix=crab.config.MECHANICAL,
            description=self.options.description + 'End',
            side=self.options.side,
            parent=start,
            match_to=start,
        )

        end.setTranslation(
            end_target.getTranslation(space='world'),
            space='world',
        )

        # -- Constrain the end to the end target
        pm.parentConstraint(
            end_target,
            end,
            maintainOffset=True,
        )

        # -- Determine the base distance between our start
        # -- and end
        base_distance = self.distance_between(
            start,
            end,
        )

        # -- Create the node which will handle the filtered
        # -- rotation, as we can then use this to take a
        # -- percentage from
        reader = self.pose_reader(
            start=start,
            end=end,
        )

        # -- Scoop all our controls
        controls = list()

        # -- Create a control for this node
        control = crab.create.control(
            description=self.options.description + 'Twist',
            match_to=self.find_first('TwistJoint'),
            side=self.options.side,
            parent=org,
            shape='pin',
            lock_list='tx;ty;tz;sx;sy;sz',
            hide_list='tx;ty;tz;sx;sy;sz;v',
        )

        # -- Create the attribute which will allow us
        # -- to blend the effect in an out
        crab.utils.organise.add_separator_attr(control)

        control.addAttr(
            'twist',
            at='float',
            k=True,
            min=0,
            max=1,
            dv=1,
        )

        # -- Get the org node, as we will transform
        # -- this to the same rotation as the reader
        control_org = crab.utils.hierarchy.find_above(
            control,
            crab.config.ORG,
        )

        control_org.setRotation(
            reader.getRotation(space='world'),
            space='world',
        )

        # -- Get zero node - this is the node
        # -- we will apply the behaviour to
        zero = crab.utils.hierarchy.find_above(
            control,
            crab.config.ZERO,
        )

        # -- We need to determine what percentage
        # -- this twister should take
        distance = self.distance_between(
            start,
            control,
        )

        # -- Now create the multiply node
        mul_node = crab.create.generic(
            node_type='floatMath',
            prefix=crab.config.MATH,
            description=self.options.description + 'Blender',
            side=self.options.side,
        )

        # -- Set the node to multiply
        mul_node.operation.set(2)

        # -- Connect and set the variables
        reader.rotateX.connect(
            mul_node.floatA,
        )

        # -- Multiply the reader rotation by
        # -- the percentage along the bone
        mul_node.floatB.set(distance / base_distance)

        # -- Now we create the second mul node which
        # -- allows us to blend the effect in and
        # -- out
        mul_out = crab.create.generic(
            node_type='floatMath',
            prefix=crab.config.MATH,
            description=self.options.description + 'Mute',
            side=self.options.side,
        )

        # -- Set the node to multiply
        mul_out.operation.set(2)

        # -- Finally, lets hook up our rotation
        mul_node.outFloat.connect(
            mul_out.floatA,
        )

        control.twist.connect(
            mul_out.floatB,
        )

        mul_out.outFloat.connect(
            zero.rotateX,
        )

        # -- Ensure the twister sits between the start
        # -- and end target
        pm.pointConstraint(
            start_target,
            zero,
            mo=True,
            w=max(0.0, 1.0 - (distance / base_distance)),
        )
        pm.pointConstraint(
            end_target,
            zero,
            mo=True,
            w=distance / base_distance,
        )

        # -- Finally, bind the driven object to the
        # -- control
        self.bind(
            self.find_first('TwistJoint'),
            control,
            maintainOffset=True,
        )

        # -- Store all the controls so we can add
        # -- them to the output plug
        controls.append(control)

        return controls

    # ----------------------------------------------------------------------------------------------
    def pose_reader(self, start, end):

        matrix_mul = crab.create.generic(
            node_type='multMatrix',
            prefix=crab.config.MATH,
            description=self.options.description + 'TwistMul',
            side=self.options.side,
        )

        end.matrix.connect(matrix_mul.matrixIn[0])
        start.matrix.connect(matrix_mul.matrixIn[1])

        decompose_matrix = crab.create.generic(
            node_type='decomposeMatrix',
            prefix=crab.config.MATH,
            description=self.options.description + 'TwistDec',
            side=self.options.side,
        )

        matrix_mul.matrixSum.connect(decompose_matrix.inputMatrix)

        quat_to_euler = crab.create.generic(
            node_type='quatToEuler',
            prefix=crab.config.MATH,
            description=self.options.description + 'TwistQ2E',
            side=self.options.side,
        )

        decompose_matrix.outputQuatX.connect(quat_to_euler.inputQuatX)
        decompose_matrix.outputQuatW.connect(quat_to_euler.inputQuatW)

        reader = crab.create.generic(
            node_type='transform',
            prefix=crab.config.MECHANICAL,
            description=self.options.description + 'TwistReader',
            side=self.options.side,
            match_to=start,
            parent=start,
        )

        quat_to_euler.outputRotate.connect(reader.rotate)

        return reader

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def distance_between(cls, a, b):
        pos_a = a.getTranslation(space='world')
        pos_b = b.getTranslation(space='world')

        return (pos_b - pos_a).length()
