import os
import json
import functools
import traceback

import pymel.core as pm
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


from ... import core
from ... import tools
from ... import utils
from ...vendor import qute


# ------------------------------------------------------------------------------
def get_resource(name):
    """
    This is a convenience function to get files from the resources directory
    and correct handle the slashing.

    :param name: Name of file to pull from the resource directory

    :return: Absolute path to the resource requested.
    """
    return os.path.join(
        os.path.dirname(__file__),
        'resources',
        name,
    ).replace('\\', '/')


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class CrabCreator(qute.QWidget):
    """
    CrabCreator is a rig building and editing ui which exposes all the
    functionality of crab.Rig
    """

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(CrabCreator, self).__init__(parent=parent or qute.mainWindow())

        # -- Create the main layout
        self.setLayout(qute.slimify(qute.QVBoxLayout()))

        # -- Load in our ui file
        self.ui = qute.loadUi(get_resource('creator.ui'))
        self.layout().addWidget(self.ui)

        # -- Apply our styling, defining some differences
        qute.applyStyle(
            [
                'space',
                get_resource('creator.css')
            ],
            self,
            **{
                '_BACKGROUND_': '30, 30, 30',
                '_ALTBACKGROUND_': '70, 70, 70',
                '_FOREGROUND_': '255, 78, 0',
                '_HIGHLIGHT_': '255, 100, 10',
                '_TEXT_': '255, 255, 255',
            }
        )

        # -- We hook up script jobs to allow the ui to auto refresh
        # -- based on internal maya events
        self.script_job_ids = list()
        self._registerScriptJobs()

        # -- When we generate widgets on the fly to show as options
        # -- we need to track them, these lists are used for that purpose
        self.tool_option_widgets = list()
        self.component_option_widgets = list()
        self.behaviour_option_widgets = list()
        self.applied_behaviour_option_widgets = list()

        # -- Resolve any icon paths, this ensures all paths
        # -- will work on any machine
        self._resolveIcons()

        # -- Create an instance of Crab
        self.rig = None

        # -- Populate all our lists - both the lists which allow the user
        # -- to build new components as well as the lists showing what a rig
        # -- is mad up of
        self.refreshAll()

        # -- Hook up the signals and slots for the main build loop buttons
        self.ui.newRig.clicked.connect(self.new)
        self.ui.editRig.clicked.connect(self.edit)
        self.ui.buildRig.clicked.connect(self.build)

        # -- These are the signals for the editing buttons
        self.ui.runTool.clicked.connect(self.runTool)
        self.ui.toolList.itemDoubleClicked.connect(self.runTool)
        self.ui.addComponent.clicked.connect(self.add_component)
        self.ui.addBehaviour.clicked.connect(self.add_behaviour)

        # -- Call backs for the lists which expose components/behaviours
        # -- which can be added to a rig
        self.ui.toolList.currentRowChanged.connect(self.populateToolOptions)
        self.ui.componentList.currentRowChanged.connect(self.populateComponentOptions)
        self.ui.behaviourList.currentRowChanged.connect(self.populateBehaviourOptions)

        # -- Callbacks for the lists which expose what the current
        # -- rig is made up from.
        self.ui.appliedComponentList.currentRowChanged.connect(self.populateAppliedComponentOptions)
        self.ui.appliedBehaviourList.currentRowChanged.connect(self.populateAppliedBehaviourOptions)

        # -- Connections to the behaviour panel buttons
        self.ui.removeBehaviour.clicked.connect(self.remove_behaviour)
        self.ui.moveBehaviourUp.clicked.connect(self.move_behaviour_up)
        self.ui.moveBehaviourDown.clicked.connect(self.move_behaviour_down)

    # --------------------------------------------------------------------------
    # -- This set of functions are all related to the new/edit/build
    # -- iteration workflow.

    # --------------------------------------------------------------------------
    def refreshAll(self):
        self.rig = self.get_rig()

        self.populateTools()
        self.populateComponents()
        self.populateBehaviours()
        self.populateAppliedComponents()
        self.populateAppliedBehaviours()

    # --------------------------------------------------------------------------
    def edit(self):
        """
        Initiates an edit of the currently active crab rig in the scene.

        :return: None
        """
        with utils.contexts.UndoChunk():
            self.rig.edit()

    # --------------------------------------------------------------------------
    def build(self):
        """
        Initiates a build of the currently active crab rig in the scene

        :return:
        """
        with utils.contexts.UndoChunk():
            try:
                result = self.rig.build()

                if not result:
                    raise Exception('Build Failure')

                qute.quick.message(
                    title='Build Success',
                    label='The rig build has been completed successfully',
                    parent=self,
                )

            except:
                traceback.print_exc()
                qute.quick.message(
                    title='Build Failure',
                    label='Something went wrong during the rig build. See the script editor for details',
                    parent=self,
                )

    # --------------------------------------------------------------------------
    def new(self):
        """
        Creates a new crab rig, prompting for a name.

        :return: None
        """
        name, ok = qute.QInputDialog.getText(
            self,
            'Rig Name',
            'Please give a name for the rig'
        )

        if not ok:
            return

        # -- Create the crab rig, passing the result to the
        # -- rig property
        self.rig = core.Rig.create(name=name)

        # -- Re-ppopulate the component lists
        self.refreshAll()

    # --------------------------------------------------------------------------
    # -- This set of functions are focused on component editing
    # -- and adding

    # --------------------------------------------------------------------------
    def add_component(self):
        """
        Triggered when the user wants to add a component.

        :return:
        """
        # -- If there is no selection we cannot do anything
        if not self.ui.componentList.currentItem():
            return

        # -- Get the values from all the option widgets currently
        # -- active
        options = dict()
        for widget in self.component_option_widgets:
            options[widget.objectName()] = qute.deriveValue(widget)

        # -- Add the component passing the type, parent and values
        # -- from all the options
        with utils.contexts.UndoChunk():
            self.rig.add_component(
                component_type=self.ui.componentList.currentItem().text(),
                parent=pm.selected()[0] if pm.selected() else None,
                **options
            )

            # -- Update the applied component list
            self.populateAppliedComponents()

    # --------------------------------------------------------------------------
    def populateComponentOptions(self):
        """
        Triggered when a user changes selection in the component list, this
        will generate widgets representing all the options for the selected
        component.

        :return: None
        """
        # -- If no component is selected we cannot do anything
        if not self.ui.componentList.currentItem():
            return

        # -- Clear out the option list so we do not hold
        # -- references to any old widgets
        self.component_option_widgets = list()

        # -- Clear the current options widgets from the layout
        qute.emptyLayout(self.ui.componentOptionsLayout)

        # -- Get the plugin from the component library
        component_plugin = self.rig.factories.components.request(
            self.ui.componentList.currentItem().text(),
        )()

        # -- Now create a widget for each option
        for name, value in component_plugin.options.items():

            # -- Create a widget to represent this value
            widget = qute.deriveWidget(value, '')
            widget.setObjectName(name)

            # -- Give a minimum width to create consistency
            widget.setMinimumWidth(140)

            # -- Add the widget to the option list
            self.component_option_widgets.append(widget)

            # -- Hook up any helpers for this widget type
            self.hookup_widget_helpers(widget)

            # -- Finally, add it into the layout
            self.ui.componentOptionsLayout.addLayout(
                qute.addLabel(widget, name),
            )

    # --------------------------------------------------------------------------
    def populateComponents(self):
        """
        Populates the component list with all the components available
        from within the component library.

        :return: None
        """
        self.ui.componentList.clear()

        if not self.rig:
            return

        for component_type in sorted(self.rig.factories.components.identifiers()):
            self.ui.componentList.addItem(component_type)

    # --------------------------------------------------------------------------
    def populateAppliedComponents(self):
        """
        Populates the list which shows all the components applied to the
        rig.

        :return: None
        """

        self.ui.appliedComponentList.clear()

        if not self.rig:
            return

        for component_instance in self.rig.components():
            if component_instance:
                self.ui.appliedComponentList.addItem(
                    '%s (%s)' % (
                        component_instance.identifier,
                        component_instance.skeletal_root().name(),
                    )
                )

    # --------------------------------------------------------------------------
    def populateAppliedComponentOptions(self):
        """
        Triggered when the user selected an item from the applied
        component list, this will generate widgets representing all the
        options for the applied component.

        :return:
        """
        # -- Local method used a value-changed callback
        # noinspection PyUnusedLocal
        def storeChange(root_bone, option, qwidget, *args, **kwargs):

            # -- Get the options data
            meta_node = core.Component(pm.PyNode(root_bone)).meta()
            options = json.loads(meta_node.Options.get())

            # -- Update them with the changed value
            options[option] = qute.deriveValue(qwidget)

            # -- Write the data back out
            meta_node.Options.set(
                json.dumps(options),
            )

        item = self.ui.appliedComponentList.currentItem()

        if not item:
            return

        # -- Clear the current options
        qute.emptyLayout(self.ui.appliedComponentOptionsLayout)

        # -- We need to get the root from the name
        root_name = item.text().split('(')[-1][:-1]

        # -- Get the plugin
        component_plugin = core.Component.get(pm.PyNode(root_name))

        # -- Now create a widget for each option
        for name, value in component_plugin.options.items():
            # -- Create a widget to represent this value
            widget = qute.deriveWidget(value, '')
            widget.setObjectName(name)

            # -- Give a minimum width to create consistency
            widget.setMinimumWidth(140)
            # widget.setReadOnly(True)

            qute.connectBlind(
                widget,
                functools.partial(
                    storeChange,
                    root_name,
                    name,
                    widget,
                )
            )

            # -- Hook up any helpers for this widget type
            self.hookup_widget_helpers(widget)

            # -- Finally, add it into the layout
            self.ui.appliedComponentOptionsLayout.addLayout(
                qute.addLabel(widget, name),
            )

    # --------------------------------------------------------------------------
    # -- This set of functions are focused on the setup and editing
    # -- of behaviours

    # --------------------------------------------------------------------------
    def add_behaviour(self):
        """
        Triggered when the user clicks to add a new behaviour, reading the
        option widget values and adding the behaviour to the currently active
        rig.

        :return: None
        """
        if not self.ui.behaviourList.currentItem():
            return

        options = dict()
        for widget in self.behaviour_option_widgets:
            options[widget.objectName()] = qute.deriveValue(widget)

        behaviour_name = self.ui.behaviourList.currentItem().text()

        try:
            self.rig.add_behaviour(
                behaviour_type=self.ui.behaviourList.currentItem().text(),
                **options
            )

            # -- Update the applied behaivours
            self.populateAppliedBehaviours()

            qute.quick.message(
                title='Behaviour Added',
                label='%s has been added to the build recipe.' % behaviour_name,
                parent=self,
            )

        except:
            traceback.print_exc()
            qute.quick.message(
                title='Behaviour Failure',
                label='%s could not be added. Please check the script editor.' % behaviour_name,
                parent=self,
            )

    # --------------------------------------------------------------------------
    def remove_behaviour(self):
        """
        Removes the selected behaviour from the rig.
        
        :return: None 
        """
        if not self.ui.appliedBehaviourList.currentItem():
            return

        self.rig.remove_behaviour(
            self.ui.appliedBehaviourList.currentItem().identifier,
        )

        self.populateAppliedBehaviours()

    # --------------------------------------------------------------------------
    def move_behaviour_up(self):
        """
        Moves the selected behaviour up one in the behaviour list
        
        :return: None 
        """
        if not self.ui.appliedBehaviourList.currentItem():
            return

        # -- Get the current row, so we can reselect it
        current_row = self.ui.appliedBehaviourList.currentRow()

        # -- Update the behaviour stack within crab
        self.rig.shift_behaviour_order(
            self.ui.appliedBehaviourList.currentItem().identifier,
            -1,
        )

        # -- Update the behaviour list
        self.populateAppliedBehaviours()

        self.ui.appliedBehaviourList.setCurrentRow(current_row - 1)

    # --------------------------------------------------------------------------
    def move_behaviour_down(self):
        """
        Moves the selected behaviour down one in the behaviour list
        
        :return: None 
        """
        if not self.ui.appliedBehaviourList.currentItem():
            return

        # -- Get the current row, so we can reselect it
        current_row = self.ui.appliedBehaviourList.currentRow()

        self.rig.shift_behaviour_order(
            self.ui.appliedBehaviourList.currentItem().identifier,
            1,
        )
        self.populateAppliedBehaviours()

        self.ui.appliedBehaviourList.setCurrentRow(current_row + 1)

    # --------------------------------------------------------------------------
    def populateBehaviourOptions(self):
        """
        Triggered when a user selects a behaviour from the behaviour
        list, this will generate a widget for each option relevent to the
        given behaviour.
        
        :return: None 
        """
        if not self.ui.behaviourList.currentItem():
            return

        self.behaviour_option_widgets = list()

        # -- Clear the current options
        qute.emptyLayout(self.ui.behaviourOptionsLayout)

        # -- Get the plugin
        behaviour_plugin = self.rig.factories.behaviours.request(
            self.ui.behaviourList.currentItem().text(),
        )()

        # -- Now create a widget for each option
        for name, value in behaviour_plugin.options.items():

            # -- Create a widget to represent this value
            widget = qute.deriveWidget(value, '')
            widget.setObjectName(name)

            # -- Hook up any helpers for this widget type
            self.hookup_widget_helpers(widget)

            # -- Give a minimum width to create consistency
            widget.setMinimumWidth(140)

            # -- Add the widget to the option list
            self.behaviour_option_widgets.append(widget)

            # -- Finally, add it into the layout
            self.ui.behaviourOptionsLayout.addLayout(
                qute.addLabel(widget, name),
            )

    # --------------------------------------------------------------------------
    def populateBehaviours(self):
        """
        Fill the behaviour list with all the behaviours available
        to the rig
        
        :return: 
        """
        self.ui.behaviourList.clear()

        if not self.rig:
            return

        for behaviour_type in sorted(self.rig.factories.behaviours.identifiers()):
            self.ui.behaviourList.addItem(behaviour_type)

    # --------------------------------------------------------------------------
    def populateAppliedBehaviours(self):
        """
        Looks at all the behaviours in the rig and lists them in the behaviour
        list.
        
        :return:
        """
        self.ui.appliedBehaviourList.clear()

        if not self.rig:
            return

        for behaviour_data in self.rig.assigned_behaviours():

            # -- Create a specific object for this entry so we can
            # -- assign it a hidden id
            widget_item = qute.QListWidgetItem(
                '%s (%s)' % (
                    behaviour_data['type'],
                    behaviour_data['options'].get('description', 'unknown'),
                )
            )

            # -- Assign the id
            widget_item.identifier = behaviour_data['id']

            # -- Add the item
            self.ui.appliedBehaviourList.addItem(widget_item)

    # --------------------------------------------------------------------------
    def populateAppliedBehaviourOptions(self):
        """
        Triggered when an applied behaviour is selected, this will show the 
        options defined for that behaviour.
        
        :return: 
        """

        # -- Local method used a value-changed callback
        # noinspection PyUnusedLocal
        def storeChange(identifier, option, qwidget, *args, **kwargs):
            data_block = self.rig.assigned_behaviours()

            for idx, data in enumerate(data_block):
                if data['id'] == identifier:
                    data['options'][option] = qute.deriveValue(qwidget)

            self.rig.store_behaviour_data(data_block)

        if not self.ui.appliedBehaviourList.currentItem():
            return

        self.applied_behaviour_option_widgets = list()

        # -- Clear the current options
        qute.emptyLayout(self.ui.appliedBehaviourOptionsLayout)

        # -- Read the current item
        item = self.ui.appliedBehaviourList.currentItem()

        # -- Get the plugin
        behaviour_data = None
        all_data = self.rig.assigned_behaviours()

        for potential_data in all_data:
            if potential_data['id'] == item.identifier:
                behaviour_data = potential_data
                break

        if not behaviour_data:
            return

        # -- Get the options from the behaviour, then combine
        # -- them with the stored options (this allows us to
        # -- add new options which were not present when the
        # -- behaviour was added).
        behaviour = self.rig.factories.behaviours.request(behaviour_data['type'])()
        behaviour_options = behaviour.options.copy()
        behaviour_options.update(behaviour_data['options'])

        # -- Now create a widget for each option
        for name, value in behaviour_options.items():

            # -- Create a widget to represent this value
            widget = qute.deriveWidget(value, '')
            widget.setObjectName(name)

            qute.connectBlind(
                widget,
                functools.partial(
                    storeChange,
                    behaviour_data['id'],
                    name,
                    widget,
                )
            )

            # -- Hook up any helpers for this widget type
            self.hookup_widget_helpers(widget)

            # -- Give a minimum width to create consistency
            widget.setMinimumWidth(140)

            # -- Add the widget to the option list
            self.applied_behaviour_option_widgets.append(widget)

            # -- Finally, add it into the layout
            self.ui.appliedBehaviourOptionsLayout.addLayout(
                qute.addLabel(widget, name),
            )

    # --------------------------------------------------------------------------
    # -- Tools
    def populateTools(self):
        """
        Populates the tool list with all the tools available from the
        tool library.

        :return: None
        """
        self.ui.toolList.clear()

        for tool in sorted(tools.rigging().identifiers()):
            self.ui.toolList.addItem(tool)

    # --------------------------------------------------------------------------
    def populateToolOptions(self):
        """
        Triggered when the user selects a tool in teh tool panel. This
        will dynamically generate ui elements for the options of the tool.

        :return: None
        """
        if not self.ui.toolList.currentItem():
            return

        # -- Clear the current options
        qute.emptyLayout(self.ui.toolOptionsLayout)
        self.tool_option_widgets = list()

        # -- Get the plugin
        tool_plugin = tools.rigging().request(
            self.ui.toolList.currentItem().text(),
        )()

        # -- Now create a widget for each option
        for name, value in tool_plugin.options.items():

            # -- Create a widget to represent this value
            widget = qute.deriveWidget(value, '')
            widget.setObjectName(name)

            # -- Hook up any helpers for this widget type
            self.hookup_widget_helpers(widget)

            # -- Give a minimum width to create consistency
            widget.setMinimumWidth(140)

            self.tool_option_widgets.append(widget)

            # -- Finally, add it into the layout
            self.ui.toolOptionsLayout.addLayout(
                qute.addLabel(widget, name),
            )

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def runTool(self, *args, **kwargs):
        """
        Executes the currently selected tool with any options

        :return:
        """
        if not self.ui.toolList.currentItem():
            return None

        # -- Get the values from all the option elements
        options = dict()
        for widget in self.tool_option_widgets:
            options[widget.objectName()] = qute.deriveValue(widget)

        # -- Get the plugin
        tool_plugin = tools.rigging().request(
            self.ui.toolList.currentItem().text(),
        )()

        # -- Update the plugin options with the items from the
        # -- ui
        tool_plugin.options.update(options)

        with utils.contexts.UndoChunk():
            # -- Execute the tool
            tool_plugin.run()

    # --------------------------------------------------------------------------
    # -- These are general convenience functions for the ui

    # --------------------------------------------------------------------------
    # noinspection PyMethodMayBeStatic
    def get_rig(self):
        """
        Looks for the first rig in the scene.
        
        :return: crab.Rig 
        """
        rigs = core.Rig.all()

        if not rigs:
            return None

        return rigs[0]

    # --------------------------------------------------------------------------
    # -- The functions below are UI construction methods

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def _resolveIcons(self):
        """
        Private function which hooks up the icons for the buttons
        
        :return: 
        """
        self.ui.addComponent.setIcon(qute.QIcon(get_resource('add.png')))
        self.ui.addBehaviour.setIcon(qute.QIcon(get_resource('add.png')))

        self.ui.buildRig.setIcon(qute.QIcon(get_resource('build.png')))
        self.ui.editRig.setIcon(qute.QIcon(get_resource('edit.png')))
        self.ui.newRig.setIcon(qute.QIcon(get_resource('new.png')))

        self.ui.removeBehaviour.setIcon(qute.QIcon(get_resource('remove.png')))
        self.ui.moveBehaviourDown.setIcon(qute.QIcon(get_resource('down.png')))
        self.ui.moveBehaviourUp.setIcon(qute.QIcon(get_resource('up.png')))

        self.ui.removeComponent.setIcon(qute.QIcon(get_resource('remove.png')))

    # --------------------------------------------------------------------------
    def _registerScriptJobs(self):
        """
        Registers script jobs for maya events. If the events have already
        been registered they will not be re-registered.
        """
        # -- Only register if they are not already registered
        if self.script_job_ids:
            return

        # -- Define the list of events we will register a refresh
        # -- with
        events = [
            'NewSceneOpened',
            'SceneOpened',
        ]

        for event in events:
            self.script_job_ids.append(
                pm.scriptJob(
                    event=[
                        event,
                        self.refreshAll,
                    ]
                )
            )

    # --------------------------------------------------------------------------
    def _unregisterScriptJobs(self):
        """
        This will unregster all the events tied with this UI. It will
        then clear any registered ID's stored within the class.
        """
        for job_id in self.script_job_ids:
            pm.scriptJob(
                kill=job_id,
                force=True,
            )

        # -- Clear all our job ids
        self.script_job_ids = list()

    # -------------------------------------------------------------------------
    def hookup_widget_helpers(self, widget):
        """
        This function hooks up menu helpers for widgets of certain types

        :return:
        """
        if isinstance(widget, qute.QLineEdit):
            widget.setContextMenuPolicy(qute.Qt.CustomContextMenu)
            widget.customContextMenuRequested.connect(
                functools.partial(
                    self.show_objects_menu,
                    widget,
                ),
            )

    # ------------------------------------------------------------------------------
    # noinspection PyUnusedLocal,PyUnresolvedReferences
    def show_objects_menu(self, widget, *args, **kwargs):
        """
        Creates a custom menu to allow the user to set the value
        of the given widget using a file browser.

        :param widget: Widget to affect
        :type widget: QWidget

        :return: None
        """

        def select_from_widget(widget_):
            text = qute.deriveValue(widget_)

            if pm.objExists(text):
                pm.select(text)

        def set_from_selected(widget_):
            qute.setBlindValue(widget_, ';'.join([n.name() for n in pm.selected()]))

        # -- Generate a menu
        menu = qute.menuFromDictionary(
            {
                'Set From Selection': functools.partial(
                    set_from_selected,
                    widget,
                ),
                'Select': functools.partial(
                    select_from_widget,
                    widget,
                ),
            },
            parent=self
        )
        menu.exec_(qute.QCursor().pos())

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def showEvent(self, event):
        """
        Maya re-uses UI's, so we regsiter our events whenever the ui
        is shown
        """
        self._registerScriptJobs()

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def hideEvent(self, event):
        """
        Maya re-uses UI's, so we unregister the script job events whenever
        the ui is not visible.
        """
        self._unregisterScriptJobs()


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class DockableCreator(MayaQWidgetDockableMixin, qute.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(DockableCreator, self).__init__(*args, **kwargs)


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def launch(*args, **kwargs):
    window = DockableCreator(parent=qute.mainWindow())
    widget = CrabCreator(parent=window)

    # -- Ensure its all up to date
    widget.refreshAll()

    # -- Update the geometry of the window to the last stored
    # -- geometry
    window.setCentralWidget(widget)

    # -- Set the window properties
    window.setWindowTitle('Crab')

    window.show(dockable=True)
