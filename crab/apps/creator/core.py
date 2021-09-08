import os
import json
import functools
import traceback

import pymel.core as pm
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from ... import core
from ... import tools
from ... import utils
from .. import tooltip
from ...vendor import qute


# ------------------------------------------------------------------------------
def get_help(name):
    """
    This is a convenience function to get files from the resources directory
    and correct handle the slashing.

    :param name: Name of file to pull from the resource directory

    :return: Absolute path to the resource requested.
    """
    possibility = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'help',
        name,
    )

    # -- If the resource could not be found, look at the general crab resources
    if not os.path.exists(possibility):
        possibility = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'resources',
            'help',
            name,
        )

    return possibility.replace('\\', '/')


# ------------------------------------------------------------------------------
def get_resource(name):
    """
    This is a convenience function to get files from the resources directory
    and correct handle the slashing.

    :param name: Name of file to pull from the resource directory

    :return: Absolute path to the resource requested.
    """
    possibility = os.path.join(
        os.path.dirname(__file__),
        'resources',
        name,
    )

    # -- If the resource could not be found, look at the general crab resources
    if not os.path.exists(possibility):
        possibility = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'resources',
            'icons',
            name,
        )

    return possibility.replace('\\', '/')


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming,DuplicatedCode
class CrabCreator(qute.QWidget):
    """
    CrabCreator is a rig building and editing ui which exposes all the
    functionality of crab.Rig
    """

    MIN_LABEL_WIDTH = 100

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(CrabCreator, self).__init__(parent=parent or qute.mainWindow())

        # -- Create the main layout
        self.setLayout(qute.slimify(qute.QVBoxLayout()))

        # -- Load in our ui file
        self.ui = qute.loadUi(get_resource('creator.ui'))
        self.layout().addWidget(self.ui)

        # -- Create a help shortcut for showing the user rich help information
        # -- for any widget that has an exposed 'rich_help' property
        self.short = qute.QShortcut(qute.QKeySequence("F1"), self, self.showHelp)

        # -- Apply our styling, defining some differences
        qute.applyStyle(
            [
                'space',
                get_resource('creator.css'),
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

        self.ui.editTab.tabBar().setStyleSheet('QTabBar::tab{max-height: 30px; min-height: 30px;max-width: 30px; min-width: 30px; padding: 2px;}')

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

        # -- HACK
        self.ui.newRig.rich_help = dict(
            title='Create New Rig',
            description='This allows you to create new crab rig - giving you the abiility to start adding components and behaviours.',
            gif=get_help('help_new_rig.gif')
        )

        # -- Define our progress bar
        self._progressBar = None
        self._actionCount = 0

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

        # -- Connections to the component panel buttons
        self.ui.removeComponent.clicked.connect(self.remove_component)

        # -- Connections to the behaviour panel buttons
        self.ui.removeBehaviour.clicked.connect(self.remove_behaviour)
        self.ui.moveBehaviourUp.clicked.connect(self.move_behaviour_up)
        self.ui.moveBehaviourDown.clicked.connect(self.move_behaviour_down)
        self.ui.validateBehaviour.clicked.connect(self.validateBehaviours)

        # -- Filtering callbacks
        self.ui.toolFilter.textChanged.connect(self.populateTools)
        self.ui.newComponentFilter.textChanged.connect(self.populateComponents)
        self.ui.appliedComponentFilter.textChanged.connect(self.populateAppliedComponents)
        self.ui.newBehaviourFilter.textChanged.connect(self.populateBehaviours)
        self.ui.appliedBehaviourFilter.textChanged.connect(self.populateAppliedBehaviours)

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

        # -- Update the rig connections
        if self.rig:
            self.rig.edit_started.connect(self.showProgressBar)
            self.rig.performing_action.connect(self.updateProgressBar)
            self.rig.edit_complete.connect(self.removeProgressBar)
            self.rig.build_started.connect(self.showProgressBar)
            self.rig.build_complete.connect(self.removeProgressBar)

    # --------------------------------------------------------------------------
    def edit(self):
        """
        Initiates an edit of the currently active crab rig in the scene.

        :return: None
        """
        with utils.contexts.UndoChunk():
            self.rig.edit()

        # -- Ensure our progress bar is always removed
        self.removeProgressBar(True)

    # --------------------------------------------------------------------------
    # noinspection PyBroadException
    def build(self):
        """
        Initiates a build of the currently active crab rig in the scene

        :return:
        """
        with utils.contexts.UndoChunk():
            try:
                result = self.rig.build()

                # -- Ensure our progress bar is always removed
                self.removeProgressBar(True)

                if not result:
                    raise Exception('Build Failure')

                qute.utilities.request.message(
                    title='Build Success',
                    label='The rig build has been completed successfully',
                    parent=self,
                )

            except:
                self.removeProgressBar(False)
                traceback.print_exc()
                qute.utilities.request.message(
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
        qute.emptyLayout(self.ui.componentListOptionsLayout)

        # -- Get the plugin from the component library
        component_plugin = self.rig.factories.components.request(
            self.ui.componentList.currentItem().text(),
        )()

        # -- Now create a widget for each option
        for name, value in sorted(component_plugin.options.items()):
            # -- Create a widget to represent this value
            widget = qute.deriveWidget(
                value,
                '',
                component_plugin.tooltips.get(name),
            )
            widget.setObjectName(name)

            # -- Give a minimum width to create consistency
            widget.setMinimumWidth(140)

            # -- Add the widget to the option list
            self.component_option_widgets.append(widget)

            # -- Hook up any helpers for this widget type
            self.hookup_widget_helpers(widget)

            # -- Finally, add it into the layout
            self.ui.componentListOptionsLayout.addLayout(
                qute.addLabel(widget, self._createDisplayName(name), self.MIN_LABEL_WIDTH),
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
            component = self.rig.factories.components.request(component_type)

            # -- If we do have a filter, then check it against the identifier
            # -- and the display name. Only show the tool if one of them matches
            component_filter = self.ui.newComponentFilter.text()

            if component_filter:

                identifier_match = component_filter.lower() in component.identifier.lower()

                if not identifier_match:
                    continue

            item = qute.QListWidgetItem(
                qute.QIcon(component.icon),
                component_type,
            )

            # -- Assign the rich help data
            item.rich_help = component.rich_help()

            self.ui.componentList.addItem(item)

    # --------------------------------------------------------------------------
    def remove_component(self):
        """
        Triggered when the user wants to remove a component. This will remove
        the component and perform behaviour validation.
        """
        # -- If there is no selection we cannot do anything
        #item = self.ui.appliedComponentList.currentItem()

        for item in self.ui.appliedComponentList.selectedItems():

            if not item:
                continue

            with utils.contexts.UndoChunk():
                # -- We need to get the root from the name
                root_name = item.text().split('(')[-1][:-1]

                # -- Get the plugin
                component_plugin = self.rig.factories.components.find_from_node(pm.PyNode(root_name))

                # -- Remove the component
                was_removed = component_plugin.remove()

                if not was_removed:
                    qute.utilities.request.message(
                        title='Component could not be removed',
                        label='%s could not be removed. Please check the script editor for details' % component_plugin.options.description,
                        parent=self,
                    )
                    continue

                if not self.rig.validate_behaviours():
                    qute.utilities.request.message(
                        title='Behaviour Validation Failure',
                        label='After removing the component one or more behaviours are invalid. Please check the script editor for details',
                        parent=self,
                    )
                    continue
        
        self.populateAppliedComponents()
        
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

            # -- If we do have a filter, then check it against the identifier
            # -- and the display name. Only show the tool if one of them matches
            component_filter = self.ui.appliedComponentFilter.text()

            if component_filter:

                display_match = component_filter.lower() in component_instance.options.get('description', '').lower()
                identifier_match = component_filter.lower() in component_instance.identifier.lower()

                if not identifier_match and not display_match:
                    continue

            if component_instance:
                item = qute.QListWidgetItem(
                    qute.QIcon(component_instance.icon),
                    '%s (%s)' % (
                        component_instance.identifier,
                        component_instance.skeletal_root().name(),
                    )
                )

                # -- Stamp the identifier onto the item
                item.identifier = component_instance.identifier

                self.ui.appliedComponentList.addItem(item)

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
        qute.emptyLayout(self.ui.appliedComponentListOptionsLayout)

        # -- We need to get the root from the name
        root_name = item.text().split('(')[-1][:-1]

        # -- Get the plugin
        component_plugin = self.rig.factories.components.find_from_node(pm.PyNode(root_name))

        # -- Now create a widget for each option
        for name, value in sorted(component_plugin.options.items()):
            # -- Create a widget to represent this value
            widget = qute.deriveWidget(
                value,
                '',
                component_plugin.tooltips.get(name),
            )
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
            self.ui.appliedComponentListOptionsLayout.addLayout(
                qute.addLabel(widget, self._createDisplayName(name), self.MIN_LABEL_WIDTH),
            )

    # --------------------------------------------------------------------------
    # -- This set of functions are focused on the setup and editing
    # -- of behaviours

    # --------------------------------------------------------------------------
    # noinspection PyBroadException
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

            qute.utilities.request.message(
                title='Behaviour Added',
                label='%s has been added to the build recipe.' % behaviour_name,
                parent=self,
            )

        except:
            traceback.print_exc()
            qute.utilities.request.message(
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
        current_item = self.ui.appliedBehaviourList.currentItem()

        if not current_item:
            return

        behaviour = self.rig.behaviours(unique_id=current_item.uuid)
        behaviour.remove()

        self.populateAppliedBehaviours()

    # --------------------------------------------------------------------------
    def move_behaviour_up(self):
        """
        Moves the selected behaviour up one in the behaviour list

        :return: None
        """
        current_item = self.ui.appliedBehaviourList.currentItem()

        if not current_item:
            return

        # -- Get the current row, so we can reselect it
        current_row = self.ui.appliedBehaviourList.currentRow()

        behaviour = self.rig.behaviours(unique_id=current_item.uuid)
        behaviour.shift_order(-1)

        # -- Update the behaviour list
        self.populateAppliedBehaviours()

        self.ui.appliedBehaviourList.setCurrentRow(current_row - 1)

    # --------------------------------------------------------------------------
    def move_behaviour_down(self):
        """
        Moves the selected behaviour down one in the behaviour list

        :return: None
        """
        current_item = self.ui.appliedBehaviourList.currentItem()

        if not current_item:
            return

        # -- Get the current row, so we can reselect it
        current_row = self.ui.appliedBehaviourList.currentRow()

        behaviour = self.rig.behaviours(unique_id=current_item.uuid)
        behaviour.shift_order(1)

        # -- Update the behaviour list
        self.populateAppliedBehaviours()

        self.ui.appliedBehaviourList.setCurrentRow(current_row + 1)

    def validateBehaviours(self):
        """
        Runs validation over the behaviours
        """
        if not self.rig.validate_behaviours():
            qute.utilities.request.message(
                title='Validation Errors',
                label='There were errors when validating. Please check the script editor',
                parent=self,
            )

        else:
            qute.utilities.request.message(
                title='Validation Successful',
                label='No validation errors were found',
                parent=self,
            )

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
        qute.emptyLayout(self.ui.behaviourListOptionsLayout)

        # -- Get the plugin
        behaviour_plugin = self.rig.factories.behaviours.request(
            self.ui.behaviourList.currentItem().text(),
        )()

        custom_ui = behaviour_plugin.ui(parent=self)

        if custom_ui:
            self.ui.behaviourListOptionsLayout.addWidget(
                qute.QLabel('This widget has a custom UI. Please add it, then hop over to the applied behaviours tab to instigate its interface.')
            )

        # -- Now create a widget for each option
        for name, value in sorted(behaviour_plugin.options.items()):

            # -- If we're dealing with an attribute that is to be specifically managed
            # -- by a ui element, then we ignore it
            if custom_ui and name not in custom_ui.unhandled_options():
                continue

            # -- Create a widget to represent this value
            widget = qute.deriveWidget(
                value,
                '',
                behaviour_plugin.tooltips.get(name),
            )
            widget.setObjectName(name)

            # -- Hook up any helpers for this widget type
            self.hookup_widget_helpers(widget)

            # -- Give a minimum width to create consistency
            widget.setMinimumWidth(140)

            # -- Add the widget to the option list
            self.behaviour_option_widgets.append(widget)

            # -- Finally, add it into the layout
            self.ui.behaviourListOptionsLayout.addLayout(
                qute.addLabel(widget, self._createDisplayName(name), self.MIN_LABEL_WIDTH),
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
            behaviour = self.rig.factories.behaviours.request(behaviour_type)

            # -- If we do have a filter, then check it against the identifier
            # -- and the display name. Only show the tool if one of them matches
            behaviour_filter = self.ui.newBehaviourFilter.text()

            if behaviour_filter:

                identifier_match = behaviour_filter.lower() in behaviour.identifier.lower()

                if not identifier_match:
                    continue

            item = qute.QListWidgetItem(
                qute.QIcon(behaviour.icon),
                behaviour_type,
            )
            item.rich_help = behaviour.rich_help()

            self.ui.behaviourList.addItem(item)

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

        for behaviour in self.rig.behaviours():

            # -- If we do have a filter, then check it against the identifier
            # -- and the display name. Only show the tool if one of them matches
            behaviour_filter = self.ui.appliedBehaviourFilter.text()

            if behaviour_filter:

                display_match = behaviour_filter.lower() in behaviour.options.description.lower()
                identifier_match = behaviour_filter.lower() in behaviour.identifier.lower()
                any_options_match = False

                for k, v in behaviour.options.items():
                    if behaviour_filter.lower() in str(v).lower():
                        any_options_match = True
                        break

                if not display_match and not identifier_match and not any_options_match:
                    continue

            # -- Create a specific object for this entry so we can
            # -- assign it a hidden id
            widget_item = qute.QListWidgetItem(
                qute.QIcon(behaviour.icon if behaviour else ''),
                '%s (%s)' % (
                    behaviour.identifier,
                    behaviour.options.get('description', 'unknown'),
                )
            )

            # -- Assign the id
            widget_item.uuid = behaviour.uuid

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

            # -- Get the plugin
            behaviour_ = self.rig.behaviours(unique_id=identifier)

            # -- Update the option value
            behaviour_.options[option] = qute.deriveValue(qwidget)

            # -- Store the change
            behaviour_.save()

        if not self.ui.appliedBehaviourList.currentItem():
            return

        self.applied_behaviour_option_widgets = list()

        # -- Clear the current options
        qute.emptyLayout(self.ui.appliedBehaviourListOptionsLayout)

        # -- Read the current item
        item = self.ui.appliedBehaviourList.currentItem()

        # -- Get the plugin
        behaviour = self.rig.behaviours(unique_id=item.uuid)

        if not behaviour:
            return

        custom_ui = behaviour.ui()

        if custom_ui:
            self.ui.appliedBehaviourListOptionsLayout.addWidget(
                custom_ui(
                    behaviour,
                    parent=self,
                ),
            )

        # -- Now create a widget for each option
        for name, value in sorted(behaviour.options.items()):

            # -- If we're dealing with an attribute that is to be specifically managed
            # -- by a ui element, then we ignore it
            if custom_ui and name not in custom_ui.unhandled_options():
                continue

            # -- Create a widget to represent this value
            widget = qute.deriveWidget(
                value,
                '',
                behaviour.tooltips.get(name),
            )
            widget.setObjectName(name)

            qute.connectBlind(
                widget,
                functools.partial(
                    storeChange,
                    behaviour.uuid,
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
            self.ui.appliedBehaviourListOptionsLayout.addLayout(
                qute.addLabel(
                    widget,
                    self._createDisplayName(name),
                    self.MIN_LABEL_WIDTH,
                ),
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
            tool = tools.rigging().request(tool)

            # -- Check if we have a tool filter
            tool_filter = self.ui.toolFilter.text()

            # -- If we do have a filter, then check it against the identifier
            # -- and the display name. Only show the tool if one of them matches
            if tool_filter:

                display_match = tool_filter.lower() in tool.display_name.lower()
                identifier_match = tool_filter.lower() in tool.identifier.lower()

                if not display_match and not identifier_match:
                    continue

            # -- We are ok to show this item, so build an item
            item = qute.QListWidgetItem(
                qute.QIcon(tool.find_icon()),
                tool.display_name or tool.identifier,
            )

            item.identifier = tool.identifier
            item.rich_help = tool.rich_help()

            self.ui.toolList.addItem(item)

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
        qute.emptyLayout(self.ui.toolListOptionsLayout)
        self.tool_option_widgets = list()

        # -- Get the plugin
        tool_plugin = tools.rigging().request(
            self.ui.toolList.currentItem().identifier,
        )()

        # -- Now create a widget for each option
        for name, value in sorted(tool_plugin.options.iteritems()):

            # -- Create a widget to represent this value
            widget = qute.deriveWidget(
                value,
                '',
                tool_plugin.tooltips.get(name),
            )
            widget.setObjectName(name)

            # -- Hook up any helpers for this widget type
            self.hookup_widget_helpers(widget)

            # -- Give a minimum width to create consistency
            widget.setMinimumWidth(140)

            self.tool_option_widgets.append(widget)

            # -- Finally, add it into the layout
            self.ui.toolListOptionsLayout.addLayout(
                qute.addLabel(
                    widget,
                    self._createDisplayName(name),
                    self.MIN_LABEL_WIDTH,
                ),
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
            self.ui.toolList.currentItem().identifier,
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
    def showProgressBar(self, action_count):
        """
        Create a new progress bar and set the action count

        :param action_count:
        :return:
        """
        gMainProgressBar = pm.mel.eval('$tmp = $gMainProgressBar')
        self._actionCount = action_count
        self._progressBar = pm.progressBar(
            gMainProgressBar,
            edit=True,
            beginProgress=True,
            status='Editing Rig',
            minValue=0,
            maxValue=action_count,

        )

    # --------------------------------------------------------------------------
    # -- These are functions dedicated to progress bars

    # --------------------------------------------------------------------------
    def updateProgressBar(self, label):
        """
        If a progress bar is present, it is incremented and updated with the given
        label.

        :param label:
        :return:
        """

        # -- If there is no progress bar, then there is nothing for us to do
        if not self._progressBar:
            return

        self._progressBar.setStatus(label)
        self._progressBar.step()

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def removeProgressBar(self, result):
        """
        Removes the progress bar from the ui

        :param result:
        :return:
        """
        if self._progressBar:
            self._progressBar.endProgress()
            self._progressBar = None

    # --------------------------------------------------------------------------
    # -- The functions below are UI construction methods

    # --------------------------------------------------------------------------
    @classmethod
    def _createDisplayName(cls, name):
        """
        Convenience function for turning strings into nicer display strings

        :param name: Name to convert
        :type name: str

        :return: str
        """
        name = name.replace('_', ' ')
        return name.title()

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
        self.ui.validateBehaviour.setIcon(qute.QIcon(get_resource('validate.png')))

        self.ui.removeComponent.setIcon(qute.QIcon(get_resource('remove.png')))
        self.ui.editTab.setTabIcon(0, qute.QIcon(get_resource('component.png')))
        self.ui.editTab.setTabIcon(1, qute.QIcon(get_resource('behaviour.png')))
        self.ui.editTab.setTabIcon(2, qute.QIcon(get_resource('search.png')))

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
            if str(widget.text()).startswith('FILELOAD;'):
                widget.setContextMenuPolicy(qute.Qt.CustomContextMenu)
                widget.customContextMenuRequested.connect(
                    functools.partial(
                        self.show_path_menu,
                        widget,
                        write=False
                    ),
                )
                widget.setText(widget.text().split(';')[-1])
            elif str(widget.text()).startswith('FILESAVE;'):
                widget.setContextMenuPolicy(qute.Qt.CustomContextMenu)
                widget.customContextMenuRequested.connect(
                    functools.partial(
                        self.show_path_menu,
                        widget,
                        write=True
                    ),
                )
                widget.setText(widget.text().split(';')[-1])
            else:
                widget.setContextMenuPolicy(qute.Qt.CustomContextMenu)
                widget.customContextMenuRequested.connect(
                    functools.partial(
                        self.show_objects_menu,
                        widget,
                    ),
                )

    # ------------------------------------------------------------------------------
    # noinspection PyUnusedLocal,PyUnresolvedReferences
    def show_path_menu(self, widget, *args, **kwargs):
        """
        Creates a custom menu to allow the user to set the value
        of the given widget using a file browser.

        :param widget: Widget to affect
        :type widget: QWidget

        :return: None
        """

        fileMode = 0
        if 'write' in kwargs:
            if not kwargs['write']:
                fileMode = 1

        def file_browser(widget_):
            text = qute.deriveValue(widget_)

            if pm.util.path(text).dirname().exists():
                starting_directory = pm.util.path(text).dirname()
            else:
                starting_directory = pm.sceneName().dirname()

            new_path = pm.fileDialog2(
                dialogStyle=2,
                fileMode=fileMode,
                startingDirectory=starting_directory,
                caption='Select File'
            )
            if new_path:
                new_path = new_path[0]
            else:
                new_path = text

            qute.setBlindValue(widget_, new_path)

        # -- Generate a menu
        menu = qute.menuFromDictionary(
            {
                'Browse': functools.partial(
                    file_browser,
                    widget,
                ),
            },
            parent=self
        )
        menu.exec_(qute.QCursor().pos())

    # ------------------------------------------------------------------------------
    # noinspection PyUnusedLocal,PyUnresolvedReferences
    def show_objects_menu(self, widget, *args, **kwargs):
        """
        Creates a custom menu to allow the user to set the value
        of the given widget based on scene selection.

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

    # ------------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def showHelp(self, *args, **kwargs):
        """
        This will attempt to show dynamic help for any item the user is focusing on

        :param args:
        :param kwargs:
        :return:
        """

        rich_help = None

        # -- Get all the widgets under the mouse
        for widget in self.findChildren(qute.QWidget):
            if widget.underMouse():

                # -- Prioritise list widgets, and where found look for the item
                # -- under the mouse
                if isinstance(widget, qute.QListWidget):
                    # -- If we have an item under the mouse, lets switch this
                    # -- to be the widget we're looking at
                    widget = widget.itemAt(widget.mapFromGlobal(qute.QCursor().pos()))

                # -- If the widget is valid and it actually has some rich
                # -- help data, we use it
                if widget and hasattr(widget, 'rich_help') and widget.rich_help:
                    rich_help = widget.rich_help
                    break

        # -- If we have rich help for this item the user is hovering over
        # -- then lets display a tool tip
        if rich_help:
            tooltip.show_tooltip(
                rich_help.get('title'),
                rich_help.get('description'),
                rich_help.get('gif'),
                self,
            )

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
# noinspection PyUnresolvedReferences,PyUnusedLocal
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
