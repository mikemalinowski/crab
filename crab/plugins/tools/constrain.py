import crab

import pymel.core as pm


# ------------------------------------------------------------------------------
class MirrorJointsTool(crab.RigTool):

    identifier = 'Follicles : Create'

    # --------------------------------------------------------------------------
    def __init__(self):
        super(MirrorJointsTool, self).__init__()

        self.options.surface = ''

    # --------------------------------------------------------------------------
    def run(self):

        # -- Always prioritise the values set in the tool
        # -- options over the context
        if pm.objExists(self.options.surface):
            surface = pm.PyNode(self.options.surface)

        else:
            # -- If there is nothing selected then we cannot do
            # -- any more work
            if not pm.selected():
                return

            # -- Get the first selected object
            surface = pm.selected()[0]

        # -- If we have the transform then we need to get the
        # -- shape
        if isinstance(surface, pm.nt.Transform):
            surface = surface.getShape()

        follicle = pm.createNode('follicle')

        surface.attr('local').connect(follicle.inputSurface)
        surface.attr('worldMatrix[0]').connect(follicle.inputWorldMatrix)

        follicle.outTranslate.connect(follicle.getParent().translate)
        follicle.outRotate.connect(follicle.getParent().rotate)