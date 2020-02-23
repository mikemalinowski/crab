import re
import crab
import pymel.core as pm

from crab.vendor import qute


# ------------------------------------------------------------------------------
class NameTool(crab.RigTool):

    identifier = 'Naming : Assign Name'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(NameTool, self).__init__()

        self.options.name = ''

    # --------------------------------------------------------------------------
    def run(self):

        # -- Ask for the prefix
        prefix, success = qute.QInputDialog.getItem(
            None,
            'Name Prefix',
            'Select a Prefix Type',
            crab.config.PREFIXES,
            editable=False,
        )

        if not success:
            return

        # -- Ask for the description
        description = qute.quick.getText(
            'Name Description',
            'Descriptive Field',
        )

        if not description:
            return

        # -- Ask for the location
        location, success = qute.QInputDialog.getItem(
            None,
            'Name Location',
            'Select a Location Type',
            crab.config.LOCATIONS,
            editable=False,
        )

        if not success:
            return

        # -- Now we can start renaming all the selected
        # -- objects
        for node in pm.selected():
            node.rename(
                crab.config.name(
                    prefix=prefix,
                    description=description,
                    side=location,
                ),
            )
