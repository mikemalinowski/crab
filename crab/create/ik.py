# import itertools
# import pymel.core as pm
#
# from . import basics
# from . import controls
# from .. import utils
# from .. import config
#
#
# # ------------------------------------------------------------------------------
# def simple_ik(start, end, description, side, parent=None, visible=False, solver='ikRPsolver', polevector=None):
#     """
#     This is a convenience function for generating an IK handle
#     and having it named.
#
#     :param start:
#     :param end:
#     :param visible:
#     :return:
#     """
#     # -- Hook up the Ik Handle
#     ikh, eff = pm.ikHandle(
#         startJoint=start,
#         endEffector=end,
#         solver=solver,
#         priority=1,
#     )
#     ikh.visibility.set(visible)
#
#     ikh.rename(
#         config.name(
#             prefix='IKH',
#             description=description,
#             side=side,
#         ),
#     )
#
#     if parent:
#         ikh.setParent(parent)
#
#     if polevector:
#         pm.poleVectorConstraint(
#             polevector,
#             ikh,
#         )
#
#     return ikh
#
#
# # ------------------------------------------------------------------------------
# class IKFKSetup(object):
#     """
#     We utilise three chain IKFK systems in multiple places, so this is an encapsulation
#     of the common part of that process.
#     """
#
#     # --------------------------------------------------------------------------
#     def __init__(self, trace_joints, constrain_tracers=True):
#
#         # -- Store our incoming options so we can query them from
#         # -- anywhere in the class
#         self.trace_joints = trace_joints
#         self.description = config.get_description(trace_joints[0])
#         self.side = config.get_side(trace_joints[0])
#         self.constrain_tracers = constrain_tracers
#
#         # -- Configuration parameters
#         self.upvector_length = 1
#         self.create_ik_control = True
#         self.align_ik_to_world = False
#         self.constrain_tracers = True
#
#         # -- Define our output properties. These are the accessors to the
#         # -- objects which we will have created
#         self.org = None
#         self.blended_joints = list()
#         self.ik_joints = list()
#         self.fk_controls = list()
#
#         self.ik_control = None
#         self.ik_upvector_control = None
#         self.ik_controls = list()
#
#         # -- Define our attributes
#         self.ikfk_blend_attr = None
#         self.ik_vis_attr = None
#         self.fk_vis_attr = None
#
#     def build(self):
#
#         # -- Create the overall organisational node
#         self.org = basics.org(
#             'IKFK{}'.format(self.description),
#             side=self.side,
#         )
#
#         # -- Add our IKFK blend and visibility attributes
#         self.org.addAttr(
#             'ikFk',
#             at='float',
#             min=0,
#             max=1,
#             dv=0,
#             k=True,
#         )
#
#         self.org.addAttr(
#             'ikVis',
#             at='bool',
#             min=0,
#             max=1,
#             dv=1,
#             k=True,
#         )
#
#         self.org.addAttr(
#             'fkVis',
#             at='bool',
#             min=0,
#             max=1,
#             dv=1,
#             k=True,
#         )
#
#         # -- Expose all these attributes
#         self.ikfk_blend_attr = self.org.ikFk
#         self.ik_vis_attr = self.org.ikVis
#         self.fk_vis_attr = self.org.fkVis
#
#         # -- Trace the chain
#         blend_org = basics.org(
#             'Blend{}'.format(self.description),
#             side=self.side,
#             parent=self.org,
#         )
#
#         self.blended_joints = utils.joints.replicate_chain(
#             from_this=self.trace_joints[0],
#             to_this=self.trace_joints[-1],
#             parent=blend_org,
#         )
#
#         # -- Create the IK chain
#         ik_org = basics.org(
#             'IK{}'.format(self.description),
#             side=self.side,
#             parent=self.org,
#         )
#
#         self.ik_joints = utils.joints.replicate_chain(
#             from_this=self.trace_joints[0],
#             to_this=self.trace_joints[-1],
#             parent=ik_org,
#         )
#
#         # -- Create the pole vector
#         self.ik_upvector_control = controls.control(
#             'UpVector{}'.format(self.description),
#             side=self.side,
#             parent=self.org,
#             shape='cube',
#         )
#
#         zero = utils.hierarchy.get_org(self.ik_upvector_control)
#         zero.setTranslation(
#             utils.maths.calculate_upvector_position(
#                 self.ik_joints[0],
#                 self.ik_joints[1],
#                 self.ik_joints[-1],
#                 length=self.upvector_length,
#             ),
#         )
#
#         # -- Add the pole vector as a control so it recieved the ikfk blending
#         # -- attributes
#         self.ik_controls.append(self.ik_upvector_control)
#
#         # -- Create the IK chain
#         ik_handle = simple_ik(
#             description=self.description,
#             side=self.side,
#             start=self.ik_joints[0],
#             end=self.ik_joints[-1],
#             polevector=self.ik_upvector_control
#
#         )
#
#         # -- Create the ik control (if required)
#         if self.create_ik_control:
#
#             # -- Create the pole vector
#             self.ik_control = controls.control(
#                 'IK{}'.format(config.get_description(self.trace_joints[-1])),
#                 side=self.side,
#                 parent=self.org,
#                 match_to=self.ik_joints[-1],
#                 shape='cube',
#             )
#
#             # -- Check if we need to align the control to world
#             if self.align_ik_to_world:
#                 utils.hierarchy.get_org(self.ik_control).setRotation(
#                     pm.dt.Quaternion(),
#                     space='world',
#                 )
#
#             # -- Nest the ik_handle under the control
#             ik_handle.setParent(self.ik_control)
#
#             # -- Ensure this is treated as a control, and therefore recieved all the IKFK
#             # -- attributes required
#             self.ik_controls.append(self.ik_control)
#
#         # -- Create the FK controls
#         fk_org = basics.org(
#             'FK{}'.format(self.description),
#             side=self.side,
#             parent=self.org,
#         )
#
#         expected_fk_parent = fk_org
#
#         # -- Create the matrix blend nodes
#         for tracer, blended_joint, ik_joint in zip(self.trace_joints, self.blended_joints, self.ik_joints):
#
#             # -- Create the fk control that will mimic this tracer
#             fk_control = controls.control(
#                 description='FK{}'.format(config.get_description(tracer)),
#                 side=config.get_side(tracer),
#                 counter=config.get_counter(tracer),
#                 parent=expected_fk_parent,
#                 match_to=tracer,
#                 shape='cube',
#             )
#
#             self.fk_controls.append(fk_control)
#
#             # -- Make this control the parent of the next control
#             expected_fk_parent = fk_control
#
#             # -- Firstly, we need to name our Ik and Blend joints
#             ik_joint.rename(
#                 config.name(
#                     prefix='IKJ',
#                     description=config.get_description(tracer),
#                     side=config.get_side(tracer),
#                     counter=config.get_counter(tracer),
#                 )
#             )
#
#             blended_joint.rename(
#                 config.name(
#                     'BLEND',
#                     description=config.get_description(tracer),
#                     side=config.get_side(tracer),
#                     counter=config.get_counter(tracer),
#                 )
#             )
#
#             # -- Create the matrix blend node
#             matrix_blender = pm.createNode('blendMatrix')
#
#             # -- Hook in the inputs of these
#             pm.connectAttr(
#                 '{}.worldMatrix[0]'.format(ik_joint.longName()),
#                 '{}.target[0].targetMatrix'.format(matrix_blender.longName()),
#                 force=True,
#             )
#
#             pm.connectAttr(
#                 '{}.worldMatrix[0]'.format(fk_control.longName()),
#                 '{}.target[1].targetMatrix'.format(matrix_blender.longName()),
#                 force=True,
#             )
#
#             # -- Now we can hook in the output of this node to the blend node
#             pm.connectAttr(
#                 '{}.outputMatrix'.format(matrix_blender.longName()),
#                 '{}.offsetParentMatrix'.format(blended_joint.longName()),
#                 force=True,
#             )
#
#             # -- Drive the blend
#             pm.connectAttr(
#                 '{}.ikFk'.format(self.org.longName()),
#                 '{}.target[1].weight'.format(matrix_blender.longName()),
#                 force=True,
#             )
#
#             # -- We need to ensure that the blend joint does not inherit
#             # -- transforms, as this breaks the offset matrix
#             blended_joint.inheritsTransform.set(False)
#
#             # -- We also need to zero the local values of the joint, as everything will
#             # -- be given to us by the matrix
#             utils.joints.zero(blended_joint)
#
#             # -- Constrain the tracer if required
#             if self.constrain_tracers:
#                 pm.parentConstraint(
#                     blended_joint,
#                     tracer,
#                     maintainOffset=True,
#                 )
#                 pm.scaleConstraint(
#                     blended_joint,
#                     tracer,
#                     maintainOffset=True,
#                 )
#
#         # -- Add IK FK attributes to all controls
#         for control in itertools.chain(self.fk_controls, self.ik_controls):
#
#             # -- Add the seperator
#             utils.organise.add_separator_attr(control)
#
#             # -- Now we need to add the IKFK attributes as proxies
#             control.addAttr(
#                 'ikFk',
#                 proxy='{}.ikFk'.format(self.org.longName()),
#                 at='float',
#                 keyable=True,
#             )
#
#             control.addAttr(
#                 'ikVis',
#                 proxy='{}.ikVis'.format(self.org.longName()),
#                 at='float',
#                 keyable=True,
#             )
#
#             control.addAttr(
#                 'fkVis',
#                 proxy='{}.fkVis'.format(self.org.longName()),
#                 at='float',
#                 keyable=True,
#             )