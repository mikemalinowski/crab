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


# ------------------------------------------------------------------------------
class PrefixTool(crab.RigTool):

    identifier = 'Naming : Rename : Prefix'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(PrefixTool, self).__init__()

        self.options.prefix = ''

    # --------------------------------------------------------------------------
    def run(self):

        prefix = self.options.prefix

        if not prefix:
            return

        # -- Now we can start renaming all the selected
        # -- objects
        for node in pm.selected():
            old_name = node.name()
            node.rename(
                prefix + old_name
            )


# ------------------------------------------------------------------------------
class SuffixTool(crab.RigTool):

    identifier = 'Naming : Rename : Suffix'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(SuffixTool, self).__init__()

        self.options.suffix = ''

    # --------------------------------------------------------------------------
    def run(self):

        suffix = self.options.suffix

        if not suffix:
            return

        # -- Now we can start renaming all the selected
        # -- objects
        for node in pm.selected():
            old_name = node.name()
            node.rename(
                old_name + suffix
            )


# ------------------------------------------------------------------------------
class FindReplaceTool(crab.RigTool):

    identifier = 'Naming : Rename : Find / Replace'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(FindReplaceTool, self).__init__()

        self.options.find = ''
        self.options.replace = ''

    # --------------------------------------------------------------------------
    def run(self):

        find = self.options.find
        replace = self.options.replace

        if not find:
            return

        # -- Now we can start renaming all the selected
        # -- objects
        for node in pm.selected():
            old_name = node.name()
            node.rename(
                old_name.replace(find, replace)
            )
