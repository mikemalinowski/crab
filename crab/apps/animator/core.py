import sys

import pymel.core as pm
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from . import utils
from . import options
from .. import tooltip
from ... import tools
from ...vendor import qute


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming,DuplicatedCode
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
        self.ui = qute.loadUi(utils.get_resource('animator.ui'))
        self.layout().addWidget(self.ui)

        # -- Give a pointer to our custom widgets
        self.ui.toolList.widget = self

        # -- Tracking lists for tools resources
        self.tools_to_show = list()
        self.tools_to_prioritise = list()
        self.tool_option_widgets = list()

        # -- We hook up script jobs to allow the ui to auto refresh
        # -- based on internal maya events
        # self.script_job_ids = list()
        # self._registerScriptJobs()
        # -- Apply our styling, defining some differences
        qute.applyStyle(
            [
                'space',
                utils.get_resource('animator.css')
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

        # -- Hook up our help shortcut
        self.short = qute.QShortcut(qute.QKeySequence("F1"), self, self.showHelp)

        # -- Populate the tool list
        self.populateTools()

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
        default_icon = utils.get_resource('crab.png')

        sorted_tools = list()
        for tool in self.tools_to_prioritise:
            sorted_tools.append(tool)

        for tool in self.tools_to_show:#
            sorted_tools.append(tool)

        for tool in sorted_tools:

            # -- Create the item
            item = qute.QListWidgetItem(
                qute.QIcon(tool.find_icon() or default_icon),
                tool.display_name,
            )

            # -- Assign a reference to the tool
            item.identifier = tool.identifier
            item.rich_help = tool.rich_help()

            self.ui.toolList.addItem(item)

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def runTool(self, *args, **kwargs):
        """
        Executes the currently selected tool with any options

        :return:
        """
        # -- Get the plugin
        tool_plugin = self._getActivePlugin()

        if not tool_plugin:
            return

        # -- Update the plugin options with the items from the
        # -- ui
        tool_plugin.options.update(
            options.get(tool_plugin.identifier, defaults=tool_plugin.options),
        )

        # -- Execute the tool
        try:
            tool_plugin.run()

        except:
            print(sys.exc_info())

    # ----------------------------------------------------------------------------------------------
    def showOptions(self):
        """
        Shows the options panel for the active tool

        :return:
        """
        # -- Get the plugin
        tool_plugin = self._getActivePlugin()

        if not tool_plugin:
            return

        options.show_options(
            'crabanimator_{}'.format(tool_plugin.identifier),
            tool_plugin.options,
            qute.QCursor().pos() + qute.QPoint(-5, -5),
            parent=self,
        )

    # ------------------------------------------------------------------------------
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
    def _getActivePlugin(self):
        item = self.ui.toolList.currentItem()

        if not item or not hasattr(item, 'identifier'):
            return None

        # -- Get the values from all the option elements
        active_options = dict()

        for widget in self.tool_option_widgets:
            active_options[widget.objectName()] = qute.deriveValue(widget)

        # -- Get the plugin
        tool_plugin = tools.animation().request(
            item.identifier,
        )()
        tool_plugin.options.update(active_options)

        return tool_plugin


# ------------------------------------------------------------------------------
# noinspection PyPep8Naming,PyUnresolvedReferences
class AnimationToolListWidget(qute.QListWidget):
    """
    Custom class which represents the list widget in the ui file.
    """

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(AnimationToolListWidget, self).__init__(*args, **kwargs)
        self.widget = None

    # --------------------------------------------------------------------------
    def mousePressEvent(self, event):
        super(AnimationToolListWidget, self).mousePressEvent(event)

        if not self.widget:
            return

        if event.button() == qute.Qt.LeftButton:
            self.widget.runTool()
            return

        elif event.button() == qute.Qt.RightButton:
            self.widget.showOptions()
            return

        else:
            pass


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class DockableAnimator(MayaQWidgetDockableMixin, qute.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(DockableAnimator, self).__init__(*args, **kwargs)


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyUnusedLocal
def launch(*args, **kwargs):
    window = DockableAnimator(parent=qute.mainWindow())
    widget = CrabAnimator(parent=window)

    # -- Update the geometry of the window to the last stored
    # -- geometry
    window.setCentralWidget(widget)

    # -- Set the window properties
    window.setWindowTitle('Crab')
    window.show(dockable=True)
