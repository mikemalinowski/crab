import os
import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
def get_icon(name):
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'icons',
        '%s.png' % name,
    )


# ------------------------------------------------------------------------------
def get_namespace(node):
    if ':' in node:
        return ':'.join(pm.selected()[0].name().split(':')[:-1])

    return None


# ------------------------------------------------------------------------------
class SelectAllTool(crab.tools.AnimTool):
    """
    This will select all the controls within the entire scene.
    """

    identifier = 'selection_select_all'
    display_name = 'Select : All'
    icon = get_icon('select_all')

    def run(self):
        pm.select(crab.utils.access.get_controls())


# ------------------------------------------------------------------------------
class SelectOppositeTool(crab.tools.AnimTool):
    """
    This will select the 'Opposite' controls. For example, given a left control your
    selection will be switched to the right and vice versa.

    If SHIFT is held down, the opposite controls will be ADDED to the selection
    rather than replacing it.
    """

    identifier = 'selection_select_opposite'
    display_name = 'Select : Opposite'
    icon = get_icon('select_opposite')

    def run(self, nodes=None):
        current_selection = nodes or pm.selected()
        nodes_to_select = list()

        for node in current_selection:

            side = crab.config.get_side(node)
            opp = crab.config.MIDDLE

            if node.name().endswith(crab.config.RIGHT):
                opp = crab.config.LEFT

            if node.name().endswith(crab.config.LEFT):
                opp = crab.config.RIGHT

            opp_name = node.name().replace(side, opp)

            if pm.objExists(opp_name):
                nodes_to_select.append(opp_name)

        kwargs = dict()

        if pm.getModifiers() == 1:  # Shift
            kwargs['add'] = 1

        pm.select(nodes_to_select, **kwargs)


# ------------------------------------------------------------------------------
class SelectAllOnCharacter(crab.tools.AnimTool):
    """
    This selects all the controls within the currently active namespace. The active
    namespace is based upon the namespace of the currently selected object.
    """

    identifier = 'selection_select_all_character'
    display_name = 'Select : All : Character'
    icon = get_icon('select_all_character')

    def run(self):
        pm.select(crab.utils.access.get_controls(current_only=True))


# ------------------------------------------------------------------------------
class KeyAllTool(crab.tools.AnimTool):
    """
    This will place a keyframe on all controls within the entire scene at their
    current values and at the current time.
    """

    identifier = 'keyframe_all'
    display_name = 'Key : All'
    icon = get_icon('key_all')

    def run(self):
        pm.setKeyframe(crab.utils.access.get_controls())


# ------------------------------------------------------------------------------
class KeyAllOnCharacterTool(crab.tools.AnimTool):
    """
    This will keyframe all the controls within the currently selected rig at their
    current values on the current frame.
    """

    identifier = 'keyframe_all_character'
    display_name = 'Key : All : Character'
    icon = get_icon('key_character')

    def run(self):
        pm.setKeyframe(crab.utils.access.get_controls(current_only=True))


# ------------------------------------------------------------------------------
class CopyPoseTool(crab.tools.AnimTool):
    """
    This will store the current local space transform of the selected
    controls and store them.
    """

    identifier = 'poses_copy'
    display_name = 'Pose : Copy'
    icon = get_icon('pose_store')

    Pose = dict()

    def run(self, nodes=None):
        nodes = nodes or pm.selected()

        for ctl in nodes:
            CopyPoseTool.Pose[ctl.name().split(':')[-1]] = ctl.getMatrix()


# ------------------------------------------------------------------------------
class PastePoseTool(crab.tools.AnimTool):
    """
    This will apply the previously stored local space transforms back to the objects.

    If 'Selection Only' is turned on, then the pose will only be applied to matching objects
    which are also selected.
    """

    identifier = 'poses_copy_paste'
    display_name = 'Pose : Paste'
    icon = get_icon('pose_apply')

    tooltips = dict(
        selection_only='If True the pose will only be applied to matched controls in the current selection',
    )

    def __init__(self):
        super(PastePoseTool, self).__init__()

        self.options.selection_only = False

    def run(self, nodes=None):
        nodes = nodes or pm.selected()

        selected_names = [
            node.name()
            for node in nodes
        ]

        if not selected_names:
            return

        ns = get_namespace(selected_names[0])

        for ctl, pose in CopyPoseTool.Pose.items():

            # -- Add the namespace onto the ctl
            resolved_name = ctl
            if ns:
                resolved_name = ns + ':' + ctl

            if not pm.objExists(resolved_name):
                continue

            if self.options.selection_only and ctl not in selected_names:
                continue

            pm.PyNode(resolved_name).setMatrix(pose)


# ------------------------------------------------------------------------------
class CopyWorldSpaceTool(crab.tools.AnimTool):
    """
    This will store the current world space transform of the selected
    controls and store them.
    """

    identifier = 'poses_copyworldspace'
    display_name = 'Pose : Copy : World Space'
    icon = get_icon('pose_store')

    TRANSFORM_DATA = dict()

    def run(self):

        # -- Clear out any dictionary data
        CopyWorldSpaceTool.TRANSFORM_DATA = dict()

        for node in pm.selected():
            CopyWorldSpaceTool.TRANSFORM_DATA[node.name()] = node.getMatrix(worldSpace=True)


# ------------------------------------------------------------------------------
class PasteWorldSpaceTool(crab.tools.AnimTool):
    """
    This will apply the previously stored world space transforms back to the objects.

    If 'Selection Only' is turned on, then the pose will only be applied to matching objects
    which are also selected.
    """

    identifier = 'poses_copyworldspace_paste'
    display_name = 'Pose : Paste : World Space'
    icon = get_icon('pose_apply')

    def run(self):

        for name, matrix in CopyWorldSpaceTool.TRANSFORM_DATA.items():
            if pm.objExists(name):
                pm.PyNode(name).setMatrix(
                    CopyWorldSpaceTool.TRANSFORM_DATA[name],
                    worldSpace=True,
                )


# ------------------------------------------------------------------------------
class ResetSelection(crab.tools.AnimTool):
    """
    Restores the channel box attributes to the values that are defined as their defaults. If
    no defaults are defined they will be set to zero (except scale attributes will be set
    to one).
    """

    identifier = 'reset_selected'
    display_name = 'Reset : Selected'
    icon = get_icon('reset_selection')
    tooltips = dict(
        KeyOnReset='If True, then the selected controls will be keyframed once altered',
    )

    def __init__(self):
        super(ResetSelection, self).__init__()

        self.options.KeyOnReset = False

    def run(self, nodes=None):

        nodes = nodes or pm.selected()

        for node in nodes:
            self.reset_node(node)

        if self.options.KeyOnReset:
            pm.setKeyframe(nodes)

    # --------------------------------------------------------------------------
    @classmethod
    def reset_node(cls, node):

        for attr in node.listAttr(k=True):

            attr_name = attr.name(includeNode=False)

            if 'scale' in attr_name:
                value = 1.0

            elif 'translate' in attr_name or 'rotate' in attr_name:
                value = 0.0

            else:
                continue

            try:
                attr.set(value)
            except:
                pass

        for attr in node.listAttr(k=True, ud=True):
            value = pm.attributeQuery(
                attr.name(includeNode=False),
                node=node,
                listDefault=True,
            )

            try:
                attr.set(value)

            except:
                continue


# ------------------------------------------------------------------------------
class ResetCharacter(crab.tools.AnimTool):
    """
    Restores the channel box attributes of an entire rig (defined by namespace) to the values
    that are defined as their defaults. If no defaults are defined they will be set to
    zero (except scale attributes will be set to one).
    """

    identifier = 'reset_character'
    display_name = 'Reset : Character'
    icon = get_icon('reset_character')

    tooltips = dict(
        KeyOnReset='If True, then the selected controls will be keyframed once altered',
    )

    def __init__(self):
        super(ResetCharacter, self).__init__()

        self.options.KeyOnReset = False

    def run(self, nodes=None):

        if nodes:
            pm.select(nodes)

        if not pm.selected():
            return

        nodes = crab.utils.access.get_controls(current_only=True)

        for node in nodes:
            ResetSelection.reset_node(node)

        if self.options.KeyOnReset:
            pm.setKeyframe(nodes)


# ------------------------------------------------------------------------------
class SnapTool(crab.tools.AnimTool):
    """
    Snaps whichever limb is currently selected
    """

    identifier = 'snap_ikfk'
    display_name = 'Snap : IKFK'
    icon = None

    tooltips = dict(
        KeyOnReset='If True, the controls will be keyframed once altered',
        SelectionOnly='If true only objects in the current selection will be affected',
        AcrossTimeSpan='If True, this will be performed per-frame for the whole visual timespan',
    )

    def __init__(self):
        super(SnapTool, self).__init__()

        self.options.KeyOnSnap = False
        self.options.SelectionOnly = False
        self.options.AcrossTimeSpan = False

    def run(self):

        # -- Get a list of all the results
        results = [
            n
            for n in crab.utils.access.component_nodes(pm.selected()[0], 'transform')
            if crab.config.CONTROL in n.name()
        ]

        # -- Create a unique list of labels
        labels = list()
        for node in results:
            labels.extend(crab.utils.snap.labels(node))
        labels = list(set(labels))

        if not labels:
            return

        # -- Apply the snap.
        crab.utils.snap.snap_label(
            label=labels[0],
            restrict_to=pm.selected() if self.options.SelectionOnly else None,
            start_time=int(pm.playbackOptions(q=True, min=True)) if self.options.AcrossTimeSpan else None,
            end_time=int(pm.playbackOptions(q=True, max=True)) if self.options.AcrossTimeSpan else None,
            key=self.options.KeyOnSnap,
        )
