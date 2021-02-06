from ..vendor import Qt


# --------------------------------------------------------------------------
def empty(layout):
    """
    Clears the layout of all its children, removing them entirely.

    :param layout: The layout to empty.
    :type layout: QLayout

    :param recurse: If True, clear contents recursively.
        Default True.
    :type recurse: bool

    :return: None
    """
    for i in reversed(range(layout.count())):
        item = layout.takeAt(i)

        if isinstance(item, Qt.QtWidgets.QWidgetItem):
            widget = item.widget()
            widget.setParent(None)
            widget.deleteLater()

        elif isinstance(item, Qt.QtWidgets.QSpacerItem):
            pass

        else:
            empty(item.layout())


# ------------------------------------------------------------------------------
def slimify(layout):
    # -- Apply the formatting
    layout.setContentsMargins(
        *[0, 0, 0, 0]
    )
    layout.setSpacing(0)

    return layout


# --------------------------------------------------------------------------
def widgets(layout):
    """
    Returns all the child widgets (recursively) within this layout

    :param layout: The layout to empty.
    :type layout: QLayout

    :return: None
    """

    results = list()

    def _getWidgets(layout_):

        for idx in range(layout_.count()):
            item = layout_.itemAt(idx)

            if isinstance(item, Qt.QtWidgets.QLayout):
                _getWidgets(item)
                continue

            widget = item.widget()

            if not widget:
                continue

            results.append(widget)

    _getWidgets(layout)

    return results
