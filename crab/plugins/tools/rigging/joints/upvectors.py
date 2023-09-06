import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
class GenerateUpvectorPoint(crab.RigTool):

    identifier = "generate_upvector_position"
    display_name = "Generate Upvector Position"
    icon = "joints.png"

    # ----------------------------------------------------------------------------------
    def __init__(self):
        super(GenerateUpvectorPoint, self).__init__()

        self.options.length_factor = 1.0

    # ----------------------------------------------------------------------------------
    def run(self):

        if len(pm.selected()) < 3:
            print("You must select at least three objects")
            return False

        # -- Cache the selection
        user_selection = pm.selected()[:]

        # -- Calculate the position
        position = crab.utils.maths.calculate_upvector_position(
            user_selection[0],
            user_selection[1],
            user_selection[2],
            length=self.options.length_factor,
        )

        # -- Create the locator
        locator = pm.spaceLocator()
        locator.rename(
            "{}_{}_{}_vector".format(
                user_selection[0].name(),
                user_selection[1].name(),
                user_selection[2].name(),
            ),
        )

        # -- Position the locator
        locator.setTranslation(
            position,
            space="world",
        )

        return True
