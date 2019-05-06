import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class ColorControlsProcess(crab.Process):
    """
    Makes any bones which are part of the control hierarchy invisible
    by setting their draw style to None.
    """

    # -- Define the identifier for the plugin
    identifier = 'ColourControls'
    version = 1

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def post(self):
        """
        This is called after the entire rig has been built, so we will attempt
        to re-apply the shape information.

        :return:
        """
        control_root = self.rig.find('ControlRoot')[0]
        ignore_colour = crab.config.NON_ANIMATABLE_COLOUR

        for control in control_root.getChildren(ad=True, type='transform'):

            # -- Get the colour to assign to this shape
            colour = self.get_colour(control)
            control.useOutlinerColor.set(True)

            if control.getShapes():
                # -- Set the outliner colour
                control.outlinerColorR.set(colour[0] * (1.0 / 255))
                control.outlinerColorG.set(colour[1] * (1.0 / 255))
                control.outlinerColorB.set(colour[2] * (1.0 / 255))

            else:
                control.outlinerColorR.set(ignore_colour[0] * (1.0 / 255))
                control.outlinerColorG.set(ignore_colour[1] * (1.0 / 255))
                control.outlinerColorB.set(ignore_colour[2] * (1.0 / 255))

            for shape in control.getShapes():

                # -- Set the display colour
                shape.overrideEnabled.set(True)
                shape.overrideRGBColors.set(True)

                shape.overrideColorR.set(colour[0] * (1.0 / 255))
                shape.overrideColorG.set(colour[1] * (1.0 / 255))
                shape.overrideColorB.set(colour[2] * (1.0 / 255))

    # --------------------------------------------------------------------------
    @classmethod
    def get_colour(cls, node):
        if node.name().endswith(crab.config.LEFT):
            return crab.config.LEFT_COLOR

        if node.name().endswith(crab.config.RIGHT):
            return crab.config.RIGHT_COLOR

        return crab.config.MIDDLE_COLOR
