import os
import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
def get_icon(name):
    return os.path.join(
        os.path.dirname(__file__),
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
    Selects all the controls from within the active scene
    """

    identifier = 'Select : All'
    icon = get_icon('select_all')

    def run(self):
        pm.select(crab.utils.access.get_controls())


# ------------------------------------------------------------------------------
class SelectOppositeTool(crab.tools.AnimTool):
    """
    Selects all the controls from within the active scene
    """

    identifier = 'Select : Opposite'
    icon = get_icon('select_opposite')

    def run(self):
        nodes_to_select = list()

        for node in pm.selected():

            side = crab.config.get_side(node)
            opp = crab.config.MIDDLE

            if node.name().endswith(crab.config.RIGHT):
                opp = crab.config.LEFT

            if node.name().endswith(crab.config.LEFT):
                opp = crab.config.RIGHT

            opp_name = node.name().replace(side, opp)

            if pm.objExists(opp_name):
                nodes_to_select.append(opp_name)

        pm.select(nodes_to_select)


# ------------------------------------------------------------------------------
class SelectAllOnCharacter(crab.tools.AnimTool):
    """
    Selects all the controls on the currently active character
    """

    identifier = 'Select : All : Character'
    icon = get_icon('select_all_character')

    def run(self):
        pm.select(crab.utils.access.get_controls(current_only=True))


# ------------------------------------------------------------------------------
class KeyAllTool(crab.tools.AnimTool):
    """
    Keys alls the controls in the scene
    """
    identifier = 'Key : All'
    icon = get_icon('key_all')

    def run(self):
        pm.setKeyframe(crab.utils.access.get_controls())


# ------------------------------------------------------------------------------
class KeyAllOnCharacterTool(crab.tools.AnimTool):
    """
    Keys all the controls on the currently active character
    """

    identifier = 'Key : All : Character'
    icon = get_icon('key_character')

    def run(self):
        pm.setKeyframe(crab.utils.access.get_controls(current_only=True))


# ------------------------------------------------------------------------------
class CopyPoseTool(crab.tools.AnimTool):
    """
    Copies the pose of the currently selected objects
    """

    identifier = 'Pose : Copy'
    icon = get_icon('pose_store')

    Pose = dict()

    def run(self):
        for ctl in pm.selected():
            CopyPoseTool.Pose[ctl.name().split(':')[-1]] = ctl.getMatrix()


# ------------------------------------------------------------------------------
class PastePoseTool(crab.tools.AnimTool):
    """
    Applies the pose of the currently selected object
    """

    identifier = 'Pose : Paste'
    icon = get_icon('pose_apply')

    def __init__(self):
        super(PastePoseTool, self).__init__()

        self.options.selection_only = False

    def run(self):
        selected_names = [
            node.name()
            for node in pm.selected()
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
class ResetSelection(crab.tools.AnimTool):
    """
    Reselects the current objects.
    """

    identifier = 'Reset : Selected'
    icon = get_icon('reset_selection')

    def __init__(self):
        super(ResetSelection, self).__init__()

        self.options.KeyOnReset = False

    def run(self):

        nodes = pm.selected()

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
    Resets all the controls on the currently active character
    """
    identifier = 'Reset : Character'
    icon = get_icon('reset_character')

    def __init__(self):
        super(ResetCharacter, self).__init__()

        self.options.KeyOnReset = False

    def run(self):

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
    identifier = 'Snap : IKFK'
    icon = None

    def __init__(self):
        super(SnapTool, self).__init__()

        self.options.KeyOnSnap = False
        self.options.SelectionOnly = False
        self.options.AcrossTimeSpan = False

    def run(self):

        # -- Get a list of all the results
        results = [
            n
            for n in crab.utils.access.component_nodes(pm.selected()[0], crab.config.CONTROL)
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
