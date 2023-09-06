import os


# --------------------------------------------------------------------------------------
def get_resource(name):
    """
    This is a convenience function to get files from the resources directory
    and correct handle the slashing.

    :param name: Name of file to pull from the resource directory

    :return: Absolute path to the resource requested.
    """
    return os.path.join(
        os.path.dirname(__file__),
        "resources",
        name,
    ).replace("\\", "/")
