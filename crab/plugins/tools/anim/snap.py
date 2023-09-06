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
class SnapTool(crab.tools.AnimTool):
    """
    Snaps whichever limb is currently selected
    """

    identifier = "snap_ikfk"
    display_name = "Snap : IKFK"
    icon = None

    tooltips = dict(
        KeyOnReset="If True, the controls will be keyframed once altered",
        SelectionOnly="If true only objects in the current selection will be affected",
        AcrossTimeSpan=(
            "If True, this will be performed per-frame for the "
            "whole visual timespan"
        ),
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
            for n in crab.utils.access.component_nodes(pm.selected()[0], "transform")
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
            start_time=int(
                pm.playbackOptions(
                    q=True,
                    min=True,
                ),
            ) if self.options.AcrossTimeSpan else None,
            end_time=int(
                pm.playbackOptions(
                    q=True,
                    max=True,
                ),
            ) if self.options.AcrossTimeSpan else None,
            key=self.options.KeyOnSnap,
        )
