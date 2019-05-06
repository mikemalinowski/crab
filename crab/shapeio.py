import os
import json
import pymel.core as pm


from . import constants


# ------------------------------------------------------------------------------
def write(node, filepath):
    """
    Writes the curve data of the given node to the given filepath

    :param node: Node to read from
    :type node: pm.nt.DagNode

    :param filepath: Path to write the data into
    :type filepath: str

    :return: Data being stored
    """
    data = read(node)

    if not data:
        return

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)

    return data


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
    :type data: dict or string

    :return: list(pm.nt.NurbsCurve, ...)
    """
    # -- If the data is a filepath we need to extract it
    if not isinstance(data, dict):

        # -- Check for a filepath
        if not os.path.exists(data):
            # -- Look for a filename in the shape dir
            data = os.path.join(
                os.path.dirname(__file__),
                'shapes',
                '%s.json' % data
            )

        # -- If the path still does not exist then we cannot do
        # -- anything with it
        if not os.path.exists(data):
            constants.log.warning('Could not find shape data for %s' % data)
            return None

        with open(data, 'r') as f:
            data = json.load(f)

    # -- Define a list which we will collate all the shapes
    # -- in
    shapes = list()

    # -- Cycle over each curve element in the data
    for curve_data in data['curves']:

        # -- Create a curve with the given cv's
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
