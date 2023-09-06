import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------
class StickyPatchComponent(crab.Component):
    """
    Component to create a setup which follows a skin cluster
    """
    identifier = "Utilities : Sticky Patch"
    legacy_identifiers = ["Sticky Patch", "General : Sticky Patch"]

    # ----------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(StickyPatchComponent, self).__init__(*args, **kwargs)

        self.options.use_nurbs = False

    # ---------------------------------------------------------------------------------
    def create_skeleton(self, parent):

        # -- Create the joint
        joint = crab.create.joint(
            description=self.options.description,
            side=self.options.side,
            parent=parent,
        )

        self.mark_as_skeletal_root(joint)

        # -- Tag the joint so we can easily access it later
        self.tag(
            joint,
            "PatchJoint",
        )

        return True

    # ----------------------------------------------------------------------------------
    def create_guide(self, parent):

        if self.options.use_nurbs:
            xform, _ = pm.nurbsPlane(
                p=[0, 0, 0],
                ax=[0, 0, 1],
                w=1,
                lr=1,
                d=3,
                u=1,
                v=1,
                ch=1
            )

        else:
            # -- Create the mesh
            xform, _ = pm.polyPlane(
                w=1,
                h=1,
                sx=1,
                sy=1,
                ax=[0, 1, 0],
                cuv=2,
                ch=1,
            )

        # -- Clear all history
        pm.delete(xform, constructionHistory=True)

        # -- Re-get the surface, as we"re not working with a polyPlane any longer
        # -- but instead a mesh shape
        surface = xform.getShape()

        # -- Parent the surface under guide root
        xform.setParent(parent)

        # -- Tag the surface so we can retrieve it later
        self.tag(
            xform,
            "GuideSurface"
        )

        # -- Now create the follicle
        follicle = self.create_follicle(
            description="Guide{}".format(self.options.description),
            side=self.options.side,
            parent=parent,
            surface=surface,
            u=0.5,
            v=0.5,
        )
        follicle.visibility.set(False)

        # -- Tag the surface so we can retrieve it later
        self.tag(
            follicle,
            "GuideFollicle"
        )

        return True

    # ----------------------------------------------------------------------------------
    def link_guide(self):
        """
        This should perform the required steps to have the skeletal
        structure driven by the guide (if the guide is implemented). This
        will then be triggered by Rig.edit process.

        :return: None
        """
        # -- Get the two objects we need to join together
        guide_follicle = self.find_first("GuideFollicle")
        joint = self.find_first("PatchJoint")

        # -- Attempt to remove any constraint on the slider
        # -- joint, as we will recreate it
        for cns_type in ["parentConstraint", "scaleConstraint"]:
            try:
                pm.delete(
                    joint.getChildren(
                        type=cns_type,
                    ),
                )

            except: pass

        # -- Build the constraint between the two
        pm.parentConstraint(
            guide_follicle,
            joint,
            maintainOffset=False,
        )

        return True

    # ----------------------------------------------------------------------------------
    def unlink_guide(self):
        """
        This should perform the operation to unlink the guide from the
        skeleton, leaving the skeleton completely free of any ties
        between it and the guide.

        This is run as part of the Rig.build process.

        :return: None
        """
        # -- Get the slider joint, as this is the node we need
        # -- to "free"
        slider_joint = self.find_first("PatchJoint")

        # -- Remove any constraints that are operating on
        # -- the joint
        for cns_type in ["parentConstraint", "scaleConstraint"]:
            try:
                pm.delete(
                    slider_joint.getChildren(
                        type=cns_type,
                    ),
                )

            except: pass

        return True

    # ----------------------------------------------------------------------------------
    def create_rig(self, parent):

        # -- Duplicate the guide mesh
        guide_mesh = self.find_first("GuideSurface")
        surface_xfo = pm.duplicate(guide_mesh)[0]
        surface_xfo.setParent(parent, r=False)

        # -- Ensure the parameters are set up for our needs
        surface_xfo.inheritsTransform.set(False)
        surface_xfo.visibility.set(False)

        # -- Pull out the mesh shape
        surface = surface_xfo.getShape()

        # -- Copy the skin weights between the two
        self.copy_weights(
            from_this=guide_mesh,
            to_this=surface_xfo
        )

        # -- Now create the follicle
        follicle = self.create_follicle(
            description="Guide{}".format(self.options.description),
            side=self.options.side,
            parent=parent,
            surface=surface,
            u=0.5,
            v=0.5,
        )

        # -- Get the transform so we can properly bind
        follicle_xfo = follicle.getParent()
        follicle_xfo.inheritsTransform.set(False)

        # -- Scale constraint the node so that any rig scaling still comes through
        pm.scaleConstraint(
            follicle_xfo.getParent(),
            follicle_xfo,
        )

        # -- Create our offset control
        control = crab.create.control(
            description=self.options.description,
            side=self.options.side,
            shape="cube",
            parent=follicle_xfo,
            match_to=follicle_xfo,
            hide_list="v",
        )

        # -- Finally we bind the joint to the follicle
        self.bind(
            self.find_first("PatchJoint"),
            control,
            mo=False,
        )

        return True

    # ----------------------------------------------------------------------------------
    @classmethod
    def create_follicle(cls, description, side, parent, surface, u=0.5, v=0.5):

        follicle = crab.create.generic(
            node_type="follicle",
            prefix=crab.config.MECHANICAL,
            description=description,
            side=side,
            parent=parent,
            find_transform=True,
        )
        follicle = follicle.getShape()

        if isinstance(surface, pm.nt.Mesh):
            surface.attr("outMesh").connect(follicle.inputMesh)

        else:
            surface.attr("local").connect(follicle.inputSurface)

        # -- Hook up the transform input
        surface.attr("worldMatrix[0]").connect(follicle.inputWorldMatrix)

        follicle.outTranslate.connect(follicle.getParent().translate)
        follicle.outRotate.connect(follicle.getParent().rotate)

        follicle.attr("parameterU").set(u)
        follicle.attr("parameterV").set(v)

        return follicle

    # ----------------------------------------------------------------------------------
    def copy_weights(self, from_this, to_this):

        try:
            # skin = current_skin_host.inputs(type="skinCluster")[0]
            skin = pm.PyNode(pm.mel.findRelatedSkinCluster(from_this.name()))

        except:
            # -- If there is no skin cluster we skip this step (this is
            # -- useful whilst progressively building
            return

        # -- Get a list of the influence objects being used
        # -- by the skin currently
        influences = skin.influenceObjects()

        # -- Apply a new skin cluster
        new_skin = pm.skinCluster(
            influences,
            to_this,
            toSelectedBones=True,
            maximumInfluences=skin.getMaximumInfluences()
        )

        # -- Copy the skin weights between them
        pm.copySkinWeights(
            sourceSkin=skin,
            destinationSkin=new_skin,
            noMirror=True,
            surfaceAssociation="closestPoint",
            influenceAssociation=["name", "closestJoint", "label"],
        )


# -- Add a tool to convert poly mesh to nurbs mesh on this component
class ConvertPolyToNurbs(crab.RigTool):

    identifier = "stickypatch_convert_to_nurbs"
    display_name = "Convert Sticky Mesh To Nurbs"

    # ----------------------------------------------------------------------------------
    def run(self, mesh=None, nurbs=None):
        """
        This is the main exection function for your tool. You may inspect
        the options dictionary of the tool to tailor the behaviour of your
        tool.

        :return: True of successful.
        """
        mesh_xfo = mesh or pm.selected()[0]
        nurbs_xfo = nurbs or pm.selected()[1]

        mesh = mesh_xfo.getShape()
        nurbs = nurbs_xfo.getShape()

        # -- Copy the skinning between the mesh and the nurbs
        crab.tools.rigging().request("skinning_copy_to_unbound_mesh")().run(
            mesh,
            nurbs,
        )

        # -- Find the follicle
        follicle = mesh.outputs(type="follicle")[0]

        # -- Disconnect the links between the follicle and the mesh
        follicle.inputMesh.disconnect()
        follicle.inputWorldMatrix.disconnect()

        # -- Now connect the equivalent attributes to the surface
        nurbs.local.connect(follicle.inputSurface)
        nurbs.attr("worldMatrix[0]").connect(follicle.inputWorldMatrix)

        # -- Repoint the meta
        meta_node_attr = mesh_xfo.message.outputs(plugs=True, connections=True)[0][1]
        meta_node_attr.disconnect()
        nurbs_xfo.message.connect(meta_node_attr)

        # -- Set component option
        option_attr = meta_node_attr.node().attr("Options")
        option_data = eval(option_attr.get())
        option_data["use_nurbs"] = True

        # -- Parent nurbs
        nurbs_xfo.setParent(mesh_xfo.getParent())
        return True


# -- Add a tool to convert poly mesh to nurbs mesh on this component
class ConvertNurbsToPoly(crab.RigTool):

    identifier = "stickypatch_convert_to_mesh"
    display_name = "Convert Sticky Nurbs To Mesh"

    # ----------------------------------------------------------------------------------
    def run(self, mesh=None, nurbs=None):
        """
        This is the main exection function for your tool. You may inspect
        the options dictionary of the tool to tailor the behaviour of your
        tool.

        :return: True of successful.
        """
        nurbs_xfo = nurbs or pm.selected()[0]
        mesh_xfo = mesh or pm.selected()[1]

        mesh = mesh_xfo.getShape()
        nurbs = nurbs_xfo.getShape()

        # -- Copy the skinning between the mesh and the nurbs
        crab.tools.rigging().request("skinning_copy_to_unbound_mesh")().run(
            nurbs,
            mesh,
        )

        # -- Find the follicle
        follicle = mesh.outputs(type="follicle")[0]

        # -- Disconnect the links between the follicle and the mesh
        follicle.inputSurface.disconnect()
        follicle.inputWorldMatrix.disconnect()

        # -- Now connect the equivalent attributes to the surface
        mesh.outMesh.connect(follicle.inputMesh)
        mesh.attr("worldMatrix[0]").connect(follicle.inputWorldMatrix)

        # -- Repoint the meta
        meta_node_attr = nurbs_xfo.message.outputs(plugs=True, connections=True)[0][1]
        meta_node_attr.disconnect()
        mesh_xfo.message.connect(meta_node_attr)

        # -- Set component option
        option_attr = meta_node_attr.node().attr("Options")
        option_data = eval(option_attr.get())
        option_data["use_nurbs"] = False

        # -- Parent nurbs
        mesh_xfo.setParent(nurbs_xfo.getParent())

        return True
