import json
import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class ShapeStoreProcess(crab.Process):
    """
    This is an example only plugin showing what a process plugin might
    be used for.
    
    In this case, we're going to snapshot all the NurbsCurve shape
    nodes within the rig and store that information in a string attribute
    allowing us to re-apply the sames post build. 
    
    This mechanism allows a rigger to make control shape adjustments and have
    them retained through the rig iteration.
    """

    # -- Define the identifier for the plugin
    identifier = 'shapeStore'
    version = 1

    # --------------------------------------------------------------------------
    def snapshot(self):
        """
        This is called before the control rig is destroyed, so we will 
        store all the control information here. 
        
        :return: 
        """
        # -- Create an attribute on the rig node to store the shape
        # -- information on
        if not self.rig.root.hasAttr('shapeInfo'):
            self.rig.root.addAttr(
                'shapeInfo',
                dt='string',
            )
            self.rig.root.shapeInfo.set('{}')

        # -- Get the control root
        control_root = self.rig.find('ControlRoot')[0]

        # -- Define the data structure variable which we will
        # -- ultimately store
        data_sets = list()

        # -- Cycle over all the nodes in the control rig, skipping any
        # -- which do not look like controls
        for node in control_root.getChildren(ad=True, type='transform'):
            if node.name().startswith(crab.config.CONTROL):

                # -- Attempt to read the shape data
                # -- from the node
                curve_dictionary = read(node)

                # -- If there was any shape data we store it
                if curve_dictionary:
                    data_sets.append(curve_dictionary)

        # -- Store all the data into the rig so we can call
        # -- upon it at a later stage
        self.rig.root.attr('shapeInfo').set(json.dumps(data_sets))

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def post_build(self):
        """
        This is called after the entire rig has been built, so we will attempt
        to re-apply the shape information.
        
        :return: 
        """
        # -- If the rig node does not have the attribute we store
        # -- shape info on, then there is little more we can do.
        if not self.rig.root.hasAttr('shapeInfo'):
            return

        # -- Read the stored data, and return if anything goes wrong
        try:
            shape_data = json.loads(
                self.rig.root.attr('shapeInfo').get(),
            )

        except ValueError:
            return

        # -- Cycle over the data looking for matching names
        for data in shape_data:

            if not pm.objExists(data['node']):
                continue

            # -- Get the node in question
            node = pm.PyNode(data['node'])

            # -- Remove any pre-existing shapes
            if node.getShapes():
                pm.delete(node.getShapes())

            # -- Now apply our new shapes
            apply(
                pm.PyNode(data['node']),
                data,
            )


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def read(node):
    """
    Looks at all the NurbsCurve shape nodes under  the given node
    and attempts to read them
    """
    shapes = list()

    # -- If we have a transform, add any nurbs curves
    # -- from it
    for shape in node.getShapes():
        if isinstance(shape, pm.nt.NurbsCurve):
            shapes.append(shape)

    if not shapes:
        return None

    # -- Define out output data. Right now we're only storing
    # -- cv's, but we wrap it in a dict so we can expand it
    # -- later without compatibility issues.
    data = dict(
        node=node.name(),
        curves=list()
    )

    # -- Cycle the shapes and store thm
    for shape in shapes:

        node_data = dict(
            cvs=list(),
            form=shape.f.get(),
            degree=shape.degree(),
            knots=shape.getKnots()
        )

        # -- Collect the positional data to an accuracy that is
        # -- reasonable.
        for cv in shape.getCVs():
            node_data['cvs'].append(
                [
                    round(value, 5)
                    for value in cv
                ]
            )

        data['curves'].append(node_data)

    return data


# ------------------------------------------------------------------------------
def apply(node, data):
    """
    Applies the given shape data to the given node.
    
    :param node: Node to apply to
    :type node: pm.nt.DagNode
    
    :param data: Shape data to apply
    :type data: dict
    
    :return: list(pm.nt.NurbsCurve, ...) 
    """
    shapes = list()
    for curve_data in data['curves']:

        # -- Create a curve with teh given cv's
        transform = pm.curve(
            p=curve_data['cvs'],
            d=curve_data['degree'],
            k=curve_data['knots'],
        )

        # -- Parent the shape under the node
        shape = transform.getShape()

        pm.parent(
            shape,
            node,
            shape=True,
            r=True,
        )

        # -- Delete the transform
        pm.delete(transform)

        shapes.append(shape)

    pm.select(node)

    return shapes
