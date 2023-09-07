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

# -- This is called a lot, and rarely changes, so we can cache it
_SHAPE_NAMES = None


# --------------------------------------------------------------------------------------
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

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

    return data


# --------------------------------------------------------------------------------------
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

    # -- Define out output data. Right now we"re only storing
    # -- cv"s, but we wrap it in a dict so we can expand it
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
            knots=shape.getKnots(),
        )

        # -- Collect the positional data to an accuracy that is
        # -- reasonable.
        for cv in shape.getCVs():
            node_data["cvs"].append([round(value, 5) for value in cv])

        data["curves"].append(node_data)

    return data


# --------------------------------------------------------------------------------------
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
        if not os.path.exists(data) or "/" not in data.replace("\\", "/"):
            # -- Look for a filename in the shape dir
            data = find_shape(data)

        # -- If the path still does not exist then we cannot do
        # -- anything with it
        if not data or not os.path.exists(data):
            constants.log.warning("Could not find shape data for %s" % data)
            return None

        with open(data, "r") as f:
            data = json.load(f)

    # -- Define a list which we will collate all the shapes
    # -- in
    shapes = list()

    # -- Cycle over each curve element in the data
    for curve_data in data["curves"]:
        # -- Create a curve with the given cv"s
        transform = pm.curve(
            p=[
                p # refine_from_up_axis(p, up_axis=data.get("up_axis", "z"))
                for p in curve_data["cvs"]
            ],
            d=curve_data["degree"],
            k=curve_data["knots"],
            # per=curve_data["form"],
        )
        print(123131231)
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


# --------------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def refine_from_up_axis(position, up_axis="z"):
    """
    This will take a position vector, and alter it if the up axis is
    set to Z. This is because it is assumed that all shapes are drawn
    within a Y-Up orientation.

    :param position: List of length3

    :return: List of length 3
    """
    return position
    # -- Get the current axis setting
    current_up_axis = pm.upAxis(q=True, axis=True)

    # -- If we"re working in the same axis space as the stored shape
    # -- then we can simply return the list as it is
    if current_up_axis == up_axis:
        return position

    # -- We now have to wrangle the data
    altered_position = [
        position[0],
        position[2],
        position[1] * -1,
    ]

    return altered_position


# --------------------------------------------------------------------------------------
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
        shape_name = os.path.basename(path).replace(".json", "")

        if shape_name == name:
            return path

    return None


# --------------------------------------------------------------------------------------
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
            "resources",
            "shapes",
        ),
    ]

    # -- If we have any paths defined by environment
    # -- variables we should add them here
    if constants.PLUGIN_ENVIRONMENT_VARIABLE in os.environ:
        paths.extend(
            os.environ[constants.PLUGIN_ENVIRONMENT_VARIABLE].split(";"),
        )

    shape_list = list()

    for path in paths:
        for root, _, files in os.walk(path):
            for filename in files:
                if filename.endswith(".json"):
                    shape_list.append(
                        os.path.join(
                            root,
                            filename,
                        ),
                    )

    return shape_list


# --------------------------------------------------------------------------------------
def shape_names(refresh=False):
    """
    Returns a list of all the available shapes

    :return: list
    """

    global _SHAPE_NAMES

    if _SHAPE_NAMES and not refresh:
        return _SHAPE_NAMES

    shape_names = list()

    for shape in shapes():
        shape_names.append(
            os.path.basename(shape).split(".")[0],
        )

    _SHAPE_NAMES = shape_names

    return shape_names


# --------------------------------------------------------------------------------------
def spin(node, x=0.0, y=0.0, z=0.0, pivot=None):
    """
    Spins the shape around by the given x, y, z (local values)

    :param node: The node whose shapes should be spun
    :type node: pm.nt.Transform or shape

    :param x: Amount to spin on the shapes local X axis in degrees
    :type x: float

    :param y: Amount to spin on the shapes local Y axis in degrees
    :type y: float

    :param z: Amount to spin on the shapes local Z axis in degrees
    :type z: float

    :param pivot: Optional alternate pivot to rotate around. This can
        either be a vector (pm.dt.Vector) or an actual object (pm.nt.Transform)
    :type pivot: pm.dt.Vector or pm.nt.Transform

    :return: None
    """
    # -- If we"re not given a pivot, then default
    # -- to a zero vector.
    pivot = pivot or pm.dt.Vector()

    # -- If we"re given a transform as a pivot, then read
    # -- out a worldspace location vector
    if isinstance(pivot, pm.nt.Transform):
        pivot = pivot.getTranslation(space="world")

    # -- Get a list of all the curves we need to modify
    all_curves = list()

    if isinstance(node, pm.nt.Transform):
        all_curves.extend(
            node.getShapes(),
        )

    elif isinstance(node, pm.nt.NurbsCurve):
        all_curves.append(node)

    # -- Validate that all entries are nurbs curves
    all_curves = [curve for curve in all_curves if isinstance(curve, pm.nt.NurbsCurve)]

    for curve in all_curves:
        for cv in range(curve.numCVs()):
            # -- Get the cv in worldspace
            worldspace_cv = pm.dt.Vector(curve.getCV(cv, space="world"))

            # -- Get the relative vector between the cv and pivot
            relative_cv = worldspace_cv - pivot

            # -- Rotate our relative vector by the rotation values
            # -- given to us
            rotated_position = relative_cv.rotateBy(
                [x * 0.017453, y * 0.017453, z * 0.017453]
            )

            # -- Add the worldspace pivot vector onto our rotated vector
            # -- to give ourselves the final vector
            final_position = rotated_position + pivot

            curve.setCV(
                cv,
                final_position,
                space="world",
            )

        curve.updateCurve()


# --------------------------------------------------------------------------------------
def scale(node, x=1, y=1, z=1, uniform=1):
    """
    scales the shape across x, y and z locally

    :param node: The node whose shapes should be scaled
    :type node: pm.nt.Transform or shape

    :param x: What value to scale by
    :type x: float

    :param y: What value to scale by
    :type y: float

    :param z: What value to scale by
    :type z: float

    :param uniform: If given, this will scale all axis by this amount
    :type uniform: float

    :return:
    """

    all_curves = list()

    if isinstance(node, pm.nt.Transform):
        all_curves.extend(
            node.getShapes(),
        )

    elif isinstance(node, pm.nt.NurbsCurve):
        all_curves.append(node)

    # -- Validate that all entries are nurbs curves
    all_curves = [curve for curve in all_curves if isinstance(curve, pm.nt.NurbsCurve)]

    for curve in all_curves:
        print("curve : %s" % curve)
        print(x)
        for cv in range(curve.numCVs()):
            cv_position = curve.getCV(cv)

            curve.setCV(
                cv,
                [
                    cv_position[0] * x * uniform,
                    cv_position[1] * y * uniform,
                    cv_position[2] * z * uniform,
                ],
            )
        curve.updateCurve()
