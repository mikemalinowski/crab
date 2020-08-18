import re
import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class NameTool(crab.RigTool):

    identifier = 'Naming : Assign Name'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(NameTool, self).__init__()

        self.options.prefix = crab.config.PREFIXES
        self.options.description = ''
        self.options.location = crab.config.LOCATIONS

    # --------------------------------------------------------------------------
    def run(self):

        prefix = self.options.prefix
        description = self.options.description
        location = self.options.location

        if not description:
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
