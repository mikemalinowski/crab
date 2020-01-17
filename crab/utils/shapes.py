import os
import json
import pymel.core as pm

from .. import constants

AXIS = dict(
    y=[
        0.0,
        1.0,
        0.0,
    ],
    z=[
        0.0,
        0.0,
        1.0,
    ],
)


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
        curves=list(),
        up_axis=pm.upAxis(q=True, axis=True),
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
# noinspection PyTypeChecker
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
            data = find_shape(data)

        # -- If the path still does not exist then we cannot do
        # -- anything with it
        if not data or not os.path.exists(data):
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
            p=[refine_from_up_axis(p, up_axis=data.get('up_axis', 'z')) for p in
               curve_data['cvs']],
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


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def refine_from_up_axis(position, up_axis='z'):
    """
    This will take a position vector, and alter it if the up axis is
    set to Z. This is because it is assumed that all shapes are drawn
    within a Y-Up orientation.

    :param position: List of length3

    :return: List of length 3
    """
    # -- Get the current axis setting
    current_up_axis = pm.upAxis(q=True, axis=True)

    # -- If we're working in the same axis space as the stored shape
    # -- then we can simply return the list as it is
    if current_up_axis == up_axis:
        return position

    # -- We now have to wrangle the data
    return [
        position[0],
        position[2] * -1,
        position[1],
    ]


# ------------------------------------------------------------------------------
def find_shape(name):
    """
    Looks for the shape with the given name. This will first look at any
    locations defined along the CRAB_PLUGIN_PATHS environment variable
    before inspecting built in shapes.

    :param name: Name of shape to search for
    :type name: str

    :return: Absolute path to shape 
    """
    for path in shapes():
        shape_name = os.path.basename(path).replace('.json', '')

        if shape_name == name:
            return path

    return None


# ------------------------------------------------------------------------------
def shapes():
    """
    Returns a list of all the available shapes

    :return: list
    """
    # -- Define a list of locations to search for, starting by
    # -- adding in our builtin shape locations
    paths = [
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'shapes',
        ),
    ]

    # -- If we have any paths defined by environment
    # -- variables we should add them here
    if constants.PLUGIN_ENVIRONMENT_VARIABLE in os.environ:
        paths.extend(
            os.environ[constants.PLUGIN_ENVIRONMENT_VARIABLE].split(';'),
        )

    shape_list = list()

    for path in paths:
        for root, _, files in os.walk(path):
            for filename in files:
                if filename.endswith('.json'):
                    shape_list.append(
                        os.path.join(
                            root,
                            filename,
                        ),
                    )

    return shape_list
