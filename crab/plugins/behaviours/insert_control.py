import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class InsertControlBehaviour(crab.Behaviour):
    identifier = 'Insert Control'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(InsertControlBehaviour, self).__init__(*args, **kwargs)

        self.options.parent = ''
        self.options.match_to = ''
        self.options.lock = 'sx;sy;sz'
        self.options.hide = 'v;sx;sy;sz'
        self.options.shape = 'cube'

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        # -- Get hte parent as a pymel object
        parent = pm.PyNode(self.options.parent)

        # -- Store its children so we can re-parent them
        children = parent.getChildren(type='transform')

        # -- Create a transform to use as a control
        control = crab.create.control(
            description=self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=pm.PyNode(self.options.match_to),
            shape=self.options.shape,
            lock_list=self.options.lock,
            hide_list=self.options.hide,
        )

        if self.options.match_to:
            match_node = pm.PyNode(self.options.match_to)

            org = crab.utils.hierarchy.find_above(
                control,
                crab.config.ORG,
            )

            org.setMatrix(
                match_node.getMatrix(worldSpace=True),
                worldSpace=True,
            )

        # -- Place the children under the control
        for child in children:
            child.setParent(control)

        return True


# ------------------------------------------------------------------------------
class AddControl(crab.Behaviour):
    identifier = 'Add Control'
    version = 1

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(AddControl, self).__init__(*args, **kwargs)

        self.options.parent = ''
        self.options.match_to = ''
        self.options.lock = 'sx;sy;sz'
        self.options.hide = 'v;sx;sy;sz'
        self.options.shape = 'cube'

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        # -- Get hte parent as a pymel object
        parent = pm.PyNode(self.options.parent)

        # -- Create a transform to use as a control
        control = crab.create.control(
            description=self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=None,
            shape=self.options.shape,
            lock_list=self.options.lock,
            hide_list=self.options.hide,
        )

        if self.options.match_to:

            match_node = pm.PyNode(self.options.match_to)

            org = crab.utils.hierarchy.find_above(
                control,
                crab.config.ORG,
            )

            org.setMatrix(
                match_node.getMatrix(worldSpace=True),
                worldSpace=True,
            )

        return True
