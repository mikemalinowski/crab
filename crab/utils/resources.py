import os


# --------------------------------------------------------------------------------------------------
def get(resource_name):
    potential_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'resources',
        'icons',
        resource_name,
    )

    if os.path.exists(potential_file):
        return potential_file

    # -- Resolve possible search paths
    search_paths = [
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'plugins',
        ),
    ]

    # -- Now register any paths defined by environment variable
    if 'CRAB_PLUGIN_PATHS' in os.environ:
        search_paths.extend(os.environ['CRAB_PLUGIN_PATHS'].split(';'))

    # -- Cycle all the search paths
    for root_path in search_paths:
        for path in resolve_sub_paths(root_path):

            potential_file = os.path.join(
                path,
                resource_name,
            )

            if os.path.exists(potential_file):
                return potential_file

    return ''


# --------------------------------------------------------------------------------------------------
def resolve_sub_paths(root_path):
    """
    Adds all the paths and subpaths of those given

    :param root_path:
    :return:
    """
    all_paths = [root_path]

    for root, _, __ in os.walk(root_path):
        all_paths.append(root)

    return list(set(all_paths))
