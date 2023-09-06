import re
import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
class GenerateCubeMeshTool(crab.RigTool):

    identifier = "meshes_generate_cubes"
    display_name = "Generate Cubes"
    icon = "meshes.png"

    tooltips = dict(
        size="How large the mesh cubes should be",
        size_regexes=(
            "If given this can be a regex:size;regex:size pattern, any "
            "joints matching that regex will then use that size instead of the default"
        ),
    )

    # ----------------------------------------------------------------------------------
    def __init__(self):
        super(GenerateCubeMeshTool, self).__init__()

        self.options.size = 4
        self.options.size_regexes = ""

    # ----------------------------------------------------------------------------------
    def run(self):
        cubes = list()

        regexes = {}
        if self.options.size_regexes:
            for size_details in self.options.size_regexes.split(";"):

                regex = re.compile(size_details.split(":")[0])
                value = float(size_details.split(":")[1])

                regexes[regex] = value

        for joint in pm.PyNode("deformers").members():

            size = self.options.size

            for regex, size_variant in regexes.items():
                if regex.search(joint.name()):
                    size = size_variant
                    break

            cube, shape = pm.polyCube(
                width=size,
                height=size,
                depth=size,
            )

            pm.delete(cube, constructionHistory=True)

            cube.setMatrix(
                joint.getMatrix(worldSpace=True),
                worldSpace=True,
            )

            pm.skinCluster(
                joint,
                cube,
                toSelectedBones=True,
            )

            cubes.append(cube)

        mesh, skin = pm.polyUniteSkinned(
            cubes,
            ch=1,
            mergeUVSets=1,
            centerPivot=True,
        )

        pm.select(mesh)
        pm.mel.BakeNonDefHistory()
