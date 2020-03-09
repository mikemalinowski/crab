import crab
import webbrowser
import pymel.core as pm

from crab.vendor import blackout

CRAB_MENU_NAME = 'Crab'
CRAB_MENU_OBJ = 'CrabMenuRoot'


# ------------------------------------------------------------------------------
def _menu_edit_rig(*args, **kwargs):
    for rig in crab.Rig.all():
        rig.edit()


# ------------------------------------------------------------------------------
def _menu_build_rig(*args, **kwargs):
    for rig in crab.Rig.all():
        rig.build()


# ------------------------------------------------------------------------------
def _menu_goto_website(*args, **kwargs):
    webbrowser.open('https://github.com/mikemalinowski/crab')


# ------------------------------------------------------------------------------
def _menu_reload(*args, **kwargs):
    blackout.drop('crab')
    pm.evalDeferred('import crab;crab.menu.initialize()')
    

# ------------------------------------------------------------------------------
def initialize():
    """
    This will setup the menu and interface mechanisms for the Crab Rigging
    Tool.

    :return: 
    """

    # -- If the menu already exists, we will delete it to allow
    # -- us to rebuild it
    if pm.menu(CRAB_MENU_OBJ, exists=True):
        pm.deleteUI(CRAB_MENU_OBJ)

    # -- Create the new menu for Crab
    new_menu = pm.menu(
        CRAB_MENU_OBJ,
        label=CRAB_MENU_NAME,
        tearOff=True,
        parent=pm.language.melGlobals['gMainWindow'],
    )

    add_menu_item('Creator', crab.creator.launch)
    add_menu_item('Animator', crab.animator.launch)

    pm.menuItem(divider=True, parent=new_menu)
    add_menu_item('Edit', _menu_edit_rig)
    add_menu_item('Build', _menu_build_rig)

    pm.menuItem(divider=True, parent=new_menu)
    add_menu_item('Website', _menu_goto_website)
    
    pm.menuItem(divider=True, parent=new_menu)
    add_menu_item('Reload', _menu_reload)

    # -- We specifically only want this menu to be visibile
    # -- in the rigging menu
    cached_menu_set = pm.menuSet(query=True, currentMenuSet=True)
    rigging_menu_set = pm.mel.findMenuSetFromLabel("Rigging")

    # -- Set our menu to the rigging menu and add it to
    # -- the menu set
    pm.menuSet(currentMenuSet=rigging_menu_set)
    pm.menuSet(addMenu=new_menu)

    # -- Restore the users cached menu set
    pm.menuSet(currentMenuSet=cached_menu_set)


# ------------------------------------------------------------------------------
def add_menu_item(label, callable_func, parent=CRAB_MENU_OBJ):
    """

    :param label: 
    :param icon: 
    :param command: 
    :return: 
    """

    return pm.menuItem(
        CRAB_MENU_OBJ + label.replace(' ', '_'),
        label=label,
        command=callable_func,
        parent=parent,
    )
