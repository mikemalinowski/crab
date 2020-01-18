import os

from .vendor.Qt import QtWidgets
from .vendor.Qt import QtGui
from . import _utils


# ------------------------------------------------------------------------------
def menuFromDictionary(structure, parent=None, name=None, icon_paths=None):
    """
    This will generate a menu based on a dictionary structure, whereby
    the key is the label and the value is a function call. You can optionally
    pass an icon path, and any icon found in that location with the same
    name as a key will be used.
    
    :param structure: Dictionary to generate the menu from. This dictionary
        is built of key value pairs where the key is the label and the value
        can be one of the following:
            * Function : This function will be called when the 
                action is triggered
            
            * Dictionary : If a dictionary is found as a value then a sub
                menu is created. You can have any number of nested dictionaries
            
            * None : If the value is None then a seperator will be added 
                regardless of the key.
    :type structure: dict
    
    :param parent: The parent of the menu.
    :type parent: QWidget/QMenu
    
    :param icon_paths: When adding items to the menu, icons with the same
        name as the keys will be looked for in any of these locations. This
        can either be a single string location or a list of locations.
    :type icon_paths: str or [str, str]
    :return: 
    """
    if isinstance(parent, QtWidgets.QMenu):
        menu = parent

    else:
        menu = QtWidgets.QMenu(name or '', parent)

    for label, target in structure.items():

        # -- Deal with seperators first
        if not target:
            menu.addSeparator()
            continue

        # -- Now check if we have a sub menu
        if isinstance(target, dict):
            sub_menu = QtWidgets.QMenu(label, menu)

            menuFromDictionary(
                structure=target,
                parent=sub_menu,
                name=label,
                icon_paths=icon_paths,
            )

            menu.addMenu(
                sub_menu,
            )

            continue

        # -- Finally, check if the target is callable
        if callable(target):

            icon = _findIcon(label, icon_paths)

            if icon:
                # -- Create the menu action
                action = QtWidgets.QAction(
                    QtGui.QIcon(icon),
                    label,
                    menu,
                )

            else:
                # -- Create the menu action
                action = QtWidgets.QAction(
                    label,
                    menu,
                )

            # -- Connect the menu action signal/slot
            action.triggered.connect(target)

            # -- Finally add the action to the menu
            menu.addAction(action)

    return menu


# ------------------------------------------------------------------------------
def _findIcon(label, icon_paths):
    """
    Private function for finding png icons with the label name
    from any of the given icon paths
    
    :param label: Name of the icon to search for
    :type label: str
    
    :param icon_paths: single path, or list of paths to check along
    :type icon_paths: str or list(str, str)
    
    :return: absolute icon path or None
    """
    # -- Ensure we're working with a list
    icon_paths = _utils.toList(icon_paths)

    for icon_path in icon_paths:

        if not icon_path:
            continue

        for filename in os.listdir(icon_path):
            if filename[:-4] == label:
                return os.path.join(
                    icon_path,
                    filename,
                )

    return None
