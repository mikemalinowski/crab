import os
import qute

import pymel.core as pm
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from ... import tools


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
class CrabAnimator(qute.QWidget):
    """
    CrabCreator is a rig building and editing ui which exposes all the
    functionality of crab.Rig
    """

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(CrabAnimator, self).__init__(parent=parent or qute.mainWindow())

        # -- Create the main layout
        self.setLayout(qute.slimify(qute.QVBoxLayout()))

        # -- Load in our ui file
        self.ui = qute.loadUi(get_resource('animator.ui'))
        self.layout().addWidget(self.ui)

        # -- Tracking lists for tools resources
        self.tools_to_show = list()
        self.tools_to_prioritise = list()
        self.tool_option_widgets = list()

        # -- We hook up script jobs to allow the ui to auto refresh
        # -- based on internal maya events
        self.script_job_ids = list()
        self._registerScriptJobs()
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

        # -- Populate the tool list
        self.populateTools()



        # --
        self.ui.toolList.itemDoubleClicked.connect(self.runTool)
        self.ui.toolList.currentRowChanged.connect(self.populateToolOptions)



    # --------------------------------------------------------------------------
    def populateTools(self):
        """
        Populates the tool list. This will show
        :return:
        """

        # -- Clear out the plugin lists
        self.tools_to_show = list()
        self.tools_to_prioritise = list()

        # -- Clear the current tool list
        self.ui.toolList.clear()

        # -- Clear the options
        self.populateToolOptions()

        # -- Check what the user has selected
        node = pm.selected()[0] if pm.selected() else None

        # -- Cycle over the tools
        for tool in tools.animation().plugins():

            # -- Get the viability status of the tool based
            # -- on the given node
            try:
                viability = tool.viable(node)

            except: continue

            if viability == tool.PRIORITY_SHOW:
                self.tools_to_prioritise.append(tool)

            elif viability == tool.ALWAYS_SHOW:
                self.tools_to_show.append(tool)

        # -- Sort the two tools lists alphabetically
        self.tools_to_prioritise.sort(key=lambda t: t.identifier)
        self.tools_to_show.sort(key=lambda t: t.identifier)

        # -- Now we need to add the items to the list
        default_icon = get_resource('crab.png')

        for tool in self.tools_to_prioritise:

            # -- Create the item
            item = qute.QListWidgetItem(
                qute.QIcon(tool.icon or default_icon),
                tool.identifier,
            )

            # -- Assign a reference to the tool
            item.tool = tool

            self.ui.toolList.addItem(item)

        for tool in self.tools_to_show:
            # -- Create the item
            item = qute.QListWidgetItem(
                qute.QIcon(tool.icon or default_icon),
                tool.identifier,
            )

            # -- Assign a reference to the tool
            item.tool = tool

            self.ui.toolList.addItem(item)

    # --------------------------------------------------------------------------
    def populateToolOptions(self):
        """
        Triggered when the user selects a tool in teh tool panel. This
        will dynamically generate ui elements for the options of the tool.

        :return: None
        """
        # -- Clear the current options
        qute.emptyLayout(self.ui.toolOptionsLayout)
        self.tool_option_widgets = list()

        if not self.ui.toolList.currentItem():
            return

        # -- Get the plugin
        tool_plugin = tools.animation().request(
            self.ui.toolList.currentItem().text(),
        )()

        # -- Now create a widget for each option
        for name, value in tool_plugin.options.items():

            # -- Create a widget to represent this value
            widget = qute.deriveWidget(value, '')
            widget.setObjectName(name)

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
        tool_plugin = tools.animation().request(
            self.ui.toolList.currentItem().text(),
        )()

        # -- Update the plugin options with the items from the
        # -- ui
        tool_plugin.options.update(options)

        # -- Execute the tool
        tool_plugin.run()

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
            'SelectionChanged',
        ]

        for event in events:
            self.script_job_ids.append(
                pm.scriptJob(
                    event=[
                        event,
                        self.populateTools,
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
class DockableAnimator(MayaQWidgetDockableMixin, qute.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(DockableAnimator, self).__init__(*args, **kwargs)


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def launch():
    window = DockableAnimator(parent=qute.mainWindow())
    widget = CrabAnimator(parent=window)

    # -- Update the geometry of the window to the last stored
    # -- geometry
    window.setCentralWidget(widget)

    # -- Set the window properties
    window.setWindowTitle('Crab')

    window.show(dockable=True)
