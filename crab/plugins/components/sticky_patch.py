import crab
import pymel.core as pm


# --------------------------------------------------------------------------------------------------
class StickyPatchComponent(crab.Component):
    """
    Component to create a setup which follows a skin cluster
    """
    identifier = 'General : Sticky Patch'

    # ----------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(StickyPatchComponent, self).__init__(*args, **kwargs)

    # -------------------------------------------------------------------------
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
            'PatchJoint',
        )

        return True

    # ----------------------------------------------------------------------------------------------
    def create_guide(self, parent):

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

        # -- Re-get the surface, as we're not working with a polyPlane any longer
        # -- but instead a mesh shape
        surface = xform.getShape()

        # -- Parent the surface under guide root
        xform.setParent(parent)

        # -- Tag the surface so we can retrieve it later
        self.tag(
            xform,
            'GuideSurface'
        )

        # -- Now create the follicle
        follicle = self.create_follicle(
            description='Guide{}'.format(self.options.description),
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
            'GuideFollicle'
        )

        return True

    # --------------------------------------------------------------------------
    def link_guide(self):
        """
        This should perform the required steps to have the skeletal
        structure driven by the guide (if the guide is implemented). This
        will then be triggered by Rig.edit process.

        :return: None
        """
        # -- Get the two objects we need to join together
        guide_follicle = self.find_first('GuideFollicle')
        joint = self.find_first('PatchJoint')

        # -- Attempt to remove any constraint on the slider
        # -- joint, as we will recreate it
        for cns_type in ['parentConstraint', 'scaleConstraint']:
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

    # --------------------------------------------------------------------------
    def unlink_guide(self):
        """
        This should perform the operation to unlink the guide from the
        skeleton, leaving the skeleton completely free of any ties
        between it and the guide.

        This is run as part of the Rig.build process.

        :return: None
        """
        # -- Get the slider joint, as this is the node we need
        # -- to 'free'
        slider_joint = self.find_first('PatchJoint')

        # -- Remove any constraints that are operating on
        # -- the joint
        for cns_type in ['parentConstraint', 'scaleConstraint']:
            try:
                pm.delete(
                    slider_joint.getChildren(
                        type=cns_type,
                    ),
                )

            except: pass

        return True

    # --------------------------------------------------------------------------
    def create_rig(self, parent):

        # -- Duplicate the guide mesh
        guide_mesh = self.find_first('GuideSurface')
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
            description='Guide{}'.format(self.options.description),
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
            shape='cube',
            parent=follicle_xfo,
            match_to=follicle_xfo,
            hide_list='v',
        )

        # -- Finally we bind the joint to the follicle
        self.bind(
            self.find_first('PatchJoint'),
            control,
            mo=False,
        )

        return True

    # --------------------------------------------------------------------------
    @classmethod
    def create_follicle(cls, description, side, parent, surface, u=0.5, v=0.5):

        follicle = crab.create.generic(
            node_type='follicle',
            prefix=crab.config.MECHANICAL,
            description=description,
            side=side,
            parent=parent,
            find_transform=True,
        )
        follicle = follicle.getShape()

        surface.attr('outMesh').connect(follicle.inputMesh)
        surface.attr('worldMatrix[0]').connect(follicle.inputWorldMatrix)

        follicle.outTranslate.connect(follicle.getParent().translate)
        follicle.outRotate.connect(follicle.getParent().rotate)

        follicle.attr('parameterU').set(u)
        follicle.attr('parameterV').set(v)

        return follicle

    # --------------------------------------------------------------------------
    def copy_weights(self, from_this, to_this):

        try:
            # skin = current_skin_host.inputs(type='skinCluster')[0]
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
            surfaceAssociation='closestPoint',
            influenceAssociation=['name', 'closestJoint', 'label'],
        )
