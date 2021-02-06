
import collections

from ...vendor import qute


# ------------------------------------------------------------------------------
# noinspection PyPep8Naming,PyUnresolvedReferences
class CrabItemListWidget(qute.QListWidget):
    """
    Custom class which represents the list widget in the ui file.
    """

    COPIED_DATA = None

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(CrabItemListWidget, self).__init__(*args, **kwargs)

    # --------------------------------------------------------------------------
    def _getCreator(self):
        """
        Returns the Crab Creator window

        :return:
        """

        p = self.parent()

        while True:
            if hasattr(p, 'ui'):
                return p

            if not p:
                return None

            p = p.parent()

    # --------------------------------------------------------------------------
    def _getOptionsLayout(self, name):
        """
        This function looks for the options layout that represents this
        list widget. This assumes that there is a strict naming convention
        between the list widget and the options layout.

        :param name: Name of the list wideget to search for
        :type name: str

        :return:
        """
        creator = self._getCreator()

        if not creator:
            return None

        return getattr(creator.ui, name + 'OptionsLayout')

    # --------------------------------------------------------------------------
    def _getOptions(self, name):
        """
        Returns a dictionary of the options current presented
        to the user.

        :param name: Name of the list widget to search for
        :type name: str

        :return: dict(option_name: option_value)
        """
        options = dict()
        layout = self._getOptionsLayout(name)

        if not layout:
            return dict()

        for widget in self.getNonLabelWidgets(layout):
            options[widget.objectName()] = qute.utilities.derive.deriveValue(widget)

        return options

    # --------------------------------------------------------------------------
    def mousePressEvent(self, event):
        """
        We use this to implement the context menu

        :param event:
        :return:
        """
        super(CrabItemListWidget, self).mousePressEvent(event)

        if event.button() == qute.Qt.RightButton:
            self.showMenu()
            return

    # --------------------------------------------------------------------------
    @classmethod
    def getNonLabelWidgets(cls, layout):
        """
        Returns all the child widgets (recursively) within this layout

        :param layout: The layout to empty.
        :type layout: QLayout

        :return: None
        """
        results = list()

        for widget in qute.utilities.layouts.widgets(layout):
            if not widget:
                continue

            if isinstance(widget, qute.QLabel):
                continue

            results.append(widget)

        return results

    # --------------------------------------------------------------------------
    def copyOptions(self):
        """
        Copies the options to a class attribute to allow them to be pasted
        later.

        :return:
        """
        CrabItemListWidget.COPIED_DATA = self._getOptions(self.objectName()).copy()

    # --------------------------------------------------------------------------
    def pasteOptions(self):
        """
        If there are any copied attributes then any matching options
        will have the stored values pasted into them.
        :return:
        """
        if not CrabItemListWidget.COPIED_DATA:
            return

        layout = self._getOptionsLayout(self.objectName())

        if not layout:
            return dict()

        for widget in self.getNonLabelWidgets(layout):

            if widget.objectName() in CrabItemListWidget.COPIED_DATA:
                qute.utilities.derive.setBlindValue(
                    widget,
                    CrabItemListWidget.COPIED_DATA[widget.objectName()],
                )

    # --------------------------------------------------------------------------
    def menuItems(self):
        """
        This should be re-implemented if you want specific list widgets to expose
        further right click context functionality.

        :return:
        """
        menu = collections.OrderedDict()

        menu['Copy Options'] = self.copyOptions
        menu['Paste Options'] = self.pasteOptions

        return menu

    # --------------------------------------------------------------------------
    def showMenu(self):
        """
        This will popup the context menu

        :return:
        """
        menu = qute.utilities.menus.menuFromDictionary(self.menuItems(), parent=self)

        menu.popup(qute.QCursor().pos())


# ------------------------------------------------------------------------------
# noinspection PyPep8Naming,PyUnresolvedReferences
class AppliedBehaviourListWidget(CrabItemListWidget):

    # --------------------------------------------------------------------------
    def menuItems(self):
        """
        This should be re-implemented if you want specific list widgets to expose
        further right click context functionality.

        :return:
        """
        menu = super(AppliedBehaviourListWidget, self).menuItems()

        menu['Duplicate'] = self.duplicateBehaviour

        return menu

    # --------------------------------------------------------------------------
    def duplicateBehaviour(self):
        """
        Duplication code for applied behaviours

        :return:
        """

        # -- If there is no current item then we do nothing
        if not self.currentItem():
            return

        # -- Get the active item
        item = self.currentItem()

        # -- Get the main tool window
        creator = self._getCreator()

        # -- We now have to get the options for the current behaviour
        behaviour_data = dict()

        all_data = creator.rig.assigned_behaviours()

        for potential_data in all_data:
            if potential_data['id'] == item.identifier:
                behaviour_data = potential_data
                break

        # -- If we could not find that data, do nothing
        if not behaviour_data:
            return None

        # -- Create a new behaviour
        creator.rig.add_behaviour(
            behaviour_data['type'],
            **behaviour_data['options']
        )

        # -- Refresh the ui
        creator.populateAppliedBehaviours()
