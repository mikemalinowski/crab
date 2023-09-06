import os
import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
def get_icon(name):
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "icons",
        "%s.png" % name,
    )


# --------------------------------------------------------------------------------------
def get_namespace(node):
    if ":" in node:
        return ":".join(pm.selected()[0].name().split(":")[:-1])

    return None


# --------------------------------------------------------------------------------------
class SelectAllTool(crab.tools.AnimTool):
    """
    This will select all the controls within the entire scene.
    """

    identifier = "selection_select_all"
    display_name = "Select : All"
    icon = get_icon("select_all")

    def run(self):
        pm.select(crab.utils.access.get_controls(current_only=len(pm.selected()) > 0))


# --------------------------------------------------------------------------------------
class SelectOppositeTool(crab.tools.AnimTool):
    """
    This will select the "Opposite" controls. For example, given a left control your
    selection will be switched to the right and vice versa.

    If SHIFT is held down, the opposite controls will be ADDED to the selection
    rather than replacing it.
    """

    identifier = "selection_select_opposite"
    display_name = "Select : Opposite"
    icon = get_icon("select_opposite")

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
            kwargs["add"] = 1

        pm.select(nodes_to_select, **kwargs)


# --------------------------------------------------------------------------------------
class ResetSelection(crab.tools.AnimTool):
    """
    Restores the channel box attributes to the values that are defined as their
    defaults. If no defaults are defined they will be set to zero (except scale
    attributes will be set to one).
    """

    identifier = "reset_selected"
    display_name = "Reset : Selected"
    icon = get_icon("reset_selection")
    tooltips = dict(
        KeyOnReset="If True, then the selected controls will be keyframed once altered",
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

            if "scale" in attr_name:
                value = 1.0

            elif "translate" in attr_name or "rotate" in attr_name:
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


# --------------------------------------------------------------------------------------
class ResetCharacter(crab.tools.AnimTool):
    """
    Restores the channel box attributes of an entire rig (defined by namespace) to the values
    that are defined as their defaults. If no defaults are defined they will be set to
    zero (except scale attributes will be set to one).
    """

    identifier = "reset_character"
    display_name = "Reset : All"
    icon = get_icon("reset_character")

    tooltips = dict(
        KeyOnReset="If True, then the selected controls will be keyframed once altered",
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
