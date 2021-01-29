import os


# --------------------------------------------------------------------------------------------------
def get(resource_name):
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'resources',
        'icons',
        resource_name,
    )
