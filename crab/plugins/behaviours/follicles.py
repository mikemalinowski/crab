import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class AddFollicleBehaviour(crab.Behaviour):
    identifier = "Add Follicle"
    version = 1

    tooltips = dict(
        parent="The node to parent the follicle under",
        surface="The name of the mesh or surface to attach to",
        drive="Optionally a node to constrain to the follicle",
    )

    REQUIRED_NODE_OPTIONS = ["parent", "surface"]
    OPTIONAL_NODE_OPTIONS = ["drive"]

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(AddFollicleBehaviour, self).__init__(*args, **kwargs)

        self.options.parent = ""
        self.options.surface = ""
        self.options.drive = ""

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self, parent=None, surface=None, drive=None):

        if not parent and pm.objExists(self.options.parent):
            parent = pm.PyNode(self.options.parent)

        if not surface and pm.objExists(self.options.surface):
            surface = pm.PyNode(self.options.surface)

        if not surface and pm.selected():
            surface = pm.selected()[0]

        if not drive and pm.objExists(self.options.drive):
            drive = pm.PyNode(self.options.drive)

        # -- Drive is optional
        if self.options.drive:
            drive = pm.PyNode(self.options.drive)

        # -- If we have the transform then we need to get the
        # -- shape
        if isinstance(surface, pm.nt.Transform):
            surface = surface.getShape()

        # -- We need to test whether the surface is a mesh or not
        is_mesh = False

        if isinstance(surface, pm.nt.Mesh):
            is_mesh = True

        follicle = crab.create.generic(
            node_type="follicle",
            prefix=crab.config.MECHANICAL,
            description=self.options.description,
            side=self.options.side,
            parent=parent,
            find_transform=True,
        )
        follicle = follicle.getShape()

        if is_mesh:
            surface.attr("outMesh").connect(follicle.inputMesh)

        else:
            surface.attr("local").connect(follicle.inputSurface)

        surface.attr("worldMatrix[0]").connect(follicle.inputWorldMatrix)

        follicle.outTranslate.connect(follicle.getParent().translate)
        follicle.outRotate.connect(follicle.getParent().rotate)

        if drive:

            # -- Set the UV positions
            if is_mesh:
                u, v = surface.getUVAtPoint(
                    drive.getTranslation(space="world"),
                    space="world",
                )

            else:
                _, u, v = surface.closestPoint(
                    drive.getTranslation(space="world"),
                    space="world",
                )

            follicle.attr("parameterU").set(u)
            follicle.attr("parameterV").set(v)

            pm.parentConstraint(
                follicle.getParent(),
                drive,
                maintainOffset=True,
            )
