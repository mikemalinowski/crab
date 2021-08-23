from .. import config
import pymel.core as pm


# ------------------------------------------------------------------------------
def face_widget(
        description,
        side,
        parent=None,
        target_node=None,
        offset_h=0.0,
        offset_v=0.0,
        flip=False,
        scale=1.0,
        pos_h_target_attr=None,
        neg_h_target_attr=None,
        pos_v_target_attr=None,
        neg_v_target_attr=None):

    """

    Creates a dynamic control structure which adjusts its shape in line with its required outputs,
    Structure conforms to the following hierarchy:

        ORG -> CTL

    :param description: Descriptive section of the name
    :type description: str

    :param side: Tag for the location to be used during the name generation
    :type side: str

    :param parent: Optional parent to assign to the node
    :type parent: str

    :param target_node: Optional target to assign to the node
    :type target_node: str

    :param offset_h: Optional offset to position the control horizontally
    :type offset_h: float

    :param offset_v: Optional offset to position the control vertically
    :type offset_v: float

    :param flip: Optional reverse horizontal axis
    :type flip: bool

    :param scale: Optional scale control up or down
    :type scale: float

    :param pos_h_target_attr: Optional attribute to be driven by the positive x output
    :type pos_h_target_attr: str

    :param neg_h_target_attr: Optional attribute to be driven by the positive x output
    :type neg_h_target_attr: str

    :param pos_v_target_attr: Optional attribute to be driven by the positive x output
    :type pos_v_target_attr: str

    :param neg_v_target_attr: Optional attribute to be driven by the positive x output
    :type neg_v_target_attr: str

    :return: FaceWidget
    """

    new_widget = FaceWidget(description, side, offset_h, offset_v, flip, scale)
    new_widget.create_widget()

    if parent:
        new_widget.set_parent(parent)

    if not target_node:
        return new_widget

    if pos_h_target_attr:
        new_widget.connect_pos_h(target_node, pos_h_target_attr)

    if neg_h_target_attr:
        new_widget.connect_neg_h(target_node, neg_h_target_attr)

    if pos_v_target_attr:
        new_widget.connect_pos_v(target_node, pos_v_target_attr)

    if neg_v_target_attr:
        new_widget.connect_neg_v(target_node, neg_v_target_attr)

    return new_widget


class FaceWidget(object):

    def __init__(self, name, side, offset_h=0.0, offset_v=0.0, flip=False, scale=1.0,):

        # process args
        self.border = config.name(
            prefix=config.ORG,
            description=name,
            side=side)
        self.controller = config.name(
            prefix=config.CONTROL,
            description=name,
            side=side)
        self.offset_h = offset_h
        self.offset_v = offset_v
        self.flip = flip
        self.scale = scale

        # store outfacing attr names
        self.pos_h_out_attr = 'posH'
        self.neg_h_out_attr = 'negH'
        self.pos_v_out_attr = 'posV'
        self.neg_v_out_attr = 'negV'
        self.pos_h_target_attr = 'posH_target'
        self.neg_h_target_attr = 'negH_target'
        self.pos_v_target_attr = 'posV_target'
        self.neg_v_target_attr = 'negV_target'

        # store remap nodes
        self.pos_h_remap = None
        self.neg_h_remap = None
        self.pos_v_remap = None
        self.neg_v_remap = None

    def create_widget(self):
        self.create_border()
        self.create_controller()
        pm.parent(
            self.controller,
            self.border
        )

        self.move(self.offset_h, self.offset_v)
        if self.flip:
            self.mirror()
        self.border.scale.set(self.scale, self.scale, self.scale)
        self.lock_border()

    def create_border(self):
        self.border = pm.curve(
            name=self.border,
            d=3,
            periodic=2,
            k=(-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
            point=((0, 0.5, 0.25),
                   (0, 0.5, 0.5),
                   (0, 0.25, 0.5),
                   (0, -0.25, 0.5),
                   (0, -0.5, 0.5),
                   (0, -0.5, 0.25),
                   (0, -0.5, -0.25),
                   (0, -0.5, -0.5),
                   (0, -0.25, -0.5),
                   (0, 0.25, -0.5),
                   (0, 0.5, -0.5),
                   (0, 0.5, -0.25),
                   (0, 0.5, 0.25),
                   (0, 0.5, 0.5),
                   (0, 0.25, 0.5))
        )
        self.border.getShape().template.set(True)
        for attribute in [self.pos_h_out_attr,
                          self.neg_h_out_attr,
                          self.pos_v_out_attr,
                          self.neg_v_out_attr]:
            pm.addAttr(self.border,
                       longName=attribute,
                       at='double',
                       min=0.0,
                       max=1.0,
                       dv=0.0)
        for attribute in [self.pos_h_target_attr,
                          self.neg_h_target_attr,
                          self.pos_v_target_attr,
                          self.neg_v_target_attr]:
            pm.addAttr(self.border,
                       longName=attribute,
                       dt='string')

    def create_controller(self):
        self.controller = pm.curve(
            name=self.controller,
            d=3,
            periodic=2,
            k=(-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
            point=((0, 0.4, 0.25),
                   (0, 0.4, 0.4),
                   (0, 0.25, 0.4),
                   (0, -0.25, 0.4),
                   (0, -0.4, 0.4),
                   (0, -0.4, 0.25),
                   (0, -0.4, -0.25),
                   (0, -0.4, -0.4),
                   (0, -0.25, -0.4),
                   (0, 0.25, -0.4),
                   (0, 0.4, -0.4),
                   (0, 0.4, -0.25),
                   (0, 0.4, 0.25),
                   (0, 0.4, 0.4),
                   (0, 0.25, 0.4))
        )
        for axis in ['X', 'Y', 'Z']:
            pm.setAttr('{}.rotate{}'.format(self.controller, axis), keyable=False)
            pm.setAttr('{}.scale{}'.format(self.controller, axis), keyable=False)
            pm.setAttr('{}.translate{}'.format(self.controller, axis), keyable=False)

        self.controller.translateX.lock()
        self.controller.translateY.showInChannelBox(True)
        self.controller.translateZ.showInChannelBox(True)
        self.controller.rotate.lock()
        self.controller.scale.lock()
        self.controller.visibility.setKeyable(False)
        self.controller.visibility.lock()
        pm.transformLimits(self.controller, tx=(0, 0), ty=(0, 0), tz=(0, 0))
        pm.transformLimits(self.controller, etx=(False, False), ety=(True, True), etz=(True, True))

    def extend_pos_h(self):
        self.controller.setLimit('translateMaxY', 1.0)
        cv_index_list = [0, 1, 2, 9, 10, 11]
        cv_list = self.build_cv_list(cv_index_list)
        pm.move(1.0, cv_list, objectSpace=True, relative=True, y=True)
        self.pos_h_remap = self.connect_control(
            'Y',
            self.pos_h_out_attr,
            inverse=False
        )
        self.controller.translateY.setKeyable(True)

    def extend_neg_h(self):
        self.controller.setLimit('translateMinY', -1.0)
        cv_index_list = [3, 4, 5, 6, 7, 8]
        cv_list = self.build_cv_list(cv_index_list)
        pm.move(-1.0, cv_list, objectSpace=True, relative=True, y=True)
        self.neg_h_remap = self.connect_control(
            'Y',
            self.neg_h_out_attr,
            inverse=True
        )
        self.controller.translateY.setKeyable(True)

    def extend_pos_v(self):
        self.controller.setLimit('translateMaxZ', 1.0)
        cv_index_list = [0, 1, 2, 3, 4, 5]
        cv_list = self.build_cv_list(cv_index_list)
        pm.move(1.0, cv_list, objectSpace=True, relative=True, z=True)
        self.pos_v_remap = self.connect_control(
            'Z',
            self.pos_v_out_attr,
            inverse=False
        )
        self.controller.translateZ.setKeyable(True)

    def extend_neg_v(self):
        self.controller.setLimit('translateMinZ', -1.0)
        cv_index_list = [6, 7, 8, 9, 10, 11]
        cv_list = self.build_cv_list(cv_index_list)
        pm.move(-1.0, cv_list, objectSpace=True, relative=True, z=True)
        self.neg_v_remap = self.connect_control(
            'Z',
            self.neg_v_out_attr,
            inverse=True
        )
        self.controller.translateZ.setKeyable(True)

    def build_cv_list(self, cv_index_list=[]):
        cv_list = []
        for cv in cv_index_list:
            cv_list.append('{}.cv[{}]'.format(self.border.name(), cv))
        return cv_list

    def connect_control(self, control_axis, output_attr, inverse=False):
        remap_node = config.name(
            prefix=config.MATH,
            description='remapValue{}'.format(output_attr),
            side=config.MIDDLE)
        remap_node = pm.createNode('remapValue', name=remap_node.format(output_attr))
        pm.connectAttr(
            '{}.translate{}'.format(self.controller, control_axis),
            '{}.inputValue'.format(remap_node)
        )
        pm.connectAttr(
            '{}.outValue'.format(remap_node),
            '{}.{}'.format(self.border, output_attr)
        )
        if inverse:
            remap_node.inputMax.set(-1)

        return remap_node

    def connect_pos_h(self, target_node, target_attr):
        if not pm.uniqueObjExists(target_node):
            pm.displayWarning('Target Node not found {} Skipping...'.format(target_node))
            return

        if not pm.hasAttr(target_node, target_attr):
            pm.displayWarning('Target attr not found {} Skipping...'.format(target_attr))
            return

        self.extend_pos_h()
        pm.connectAttr(
            '{}.{}'.format(self.border, self.pos_h_out_attr),
            '{}.{}'.format(target_node, target_attr)
        )
        pm.setAttr(
            '{}.{}'.format(self.border, self.pos_h_target_attr),
            '{}.{}'.format(target_node, target_attr),
            type="string"
        )

    def connect_neg_h(self, target_node, target_attr):
        if not pm.uniqueObjExists(target_node):
            pm.displayWarning('Target node not found {} Skipping...'.format(target_node))
            return

        if not pm.hasAttr(target_node, target_attr):
            pm.displayWarning('Target attr not found {} Skipping...'.format(target_attr))
            return

        self.extend_neg_h()
        pm.connectAttr(
            '{}.{}'.format(self.border, self.neg_h_out_attr),
            '{}.{}'.format(target_node, target_attr)
        )
        pm.setAttr(
            '{}.{}'.format(self.border, self.neg_h_target_attr),
            '{}.{}'.format(target_node, target_attr),
            type="string"
        )

    def connect_pos_v(self, target_node, target_attr):
        if not pm.uniqueObjExists(target_node):
            pm.displayWarning('Target Node not found {} Skipping...'.format(target_node))
            return

        if not pm.hasAttr(target_node, target_attr):
            pm.displayWarning('Target attr not found {} Skipping...'.format(target_attr))
            return

        self.extend_pos_v()
        pm.connectAttr(
            '{}.{}'.format(self.border, self.pos_v_out_attr),
            '{}.{}'.format(target_node, target_attr)
        )
        pm.setAttr(
            '{}.{}'.format(self.border, self.pos_v_target_attr),
            '{}.{}'.format(target_node, target_attr),
            type="string"
        )

    def connect_neg_v(self, target_node, target_attr):
        if not pm.uniqueObjExists(target_node):
            pm.displayWarning('Target Node not found {} Skipping...'.format(target_node))
            return

        if not pm.hasAttr(target_node, target_attr):
            pm.displayWarning('Target attr not found {} Skipping...'.format(target_attr))
            return

        self.extend_neg_v()
        pm.connectAttr(
            '{}.{}'.format(self.border, self.neg_v_out_attr),
            '{}.{}'.format(target_node, target_attr)
        )
        pm.setAttr(
            '{}.{}'.format(self.border, self.neg_v_target_attr),
            '{}.{}'.format(target_node, target_attr),
            type="string"
        )

    def move(self, offset_h, offset_v):
        self.border.translateY.set(offset_h)
        self.border.translateZ.set(offset_v)

    def mirror(self):
        self.border.rotateZ.set(180)

    def lock_border(self):
        self.border.translate.lock()
        self.border.rotate.lock()
        self.border.scale.lock()
        self.border.visibility.lock()

    def unlock_border(self):
        self.border.translate.unlock()
        self.border.rotate.unlock()
        self.border.scale.unlock()
        self.border.visibility.unlock()

    def set_parent(self, parent):
        self.border.setParent(parent)




