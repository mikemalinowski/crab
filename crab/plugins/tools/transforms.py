import crab

import pymel.core as pm


# ------------------------------------------------------------------------------
class ScaleTranslationsTool(crab.RigTool):

    identifier = 'Transforms : Scales Translation Values'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(ScaleTranslationsTool, self).__init__()

        self.options.scale = 1.0

    # --------------------------------------------------------------------------
    def run(self, these_nodes=None):

        # -- Take the given variables as a priority. If they are
        # -- not given we use the options, and if they are also
        # -- not given then we take the current selection
        these_nodes = these_nodes or pm.selected()

        for node in these_nodes:
            for axis in ['X', 'Y', 'Z']:
                attr = node.attr('translate%s' % axis)
                attr.set(attr.get() * self.options.scale)
