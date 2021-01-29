"""
This holds a set of small helper functions
"""
from ..vendor import Qt
from . import layouts


# ------------------------------------------------------------------------------
def addLabel(widget, label, min_label_width=None):
    """
    Adds a label to the widget, returning a layout with the label
    on the left and the widget on the right.

    :param widget: Widget to be given a label
    :type widget: QWidget

    :param label: Label text to show
    :type label: str

    :return: SlimHBoxLayout
    """
    label = Qt.QtWidgets.QLabel(label)
    layout = layouts.slimify(Qt.QtWidgets.QHBoxLayout())

    # -- Apply the min label width if required
    if min_label_width:
        label.setMinimumWidth(min_label_width)

    layout.addWidget(label)
    layout.addSpacerItem(
        Qt.QtWidgets.QSpacerItem(
            10,
            0,
            Qt.QtWidgets.QSizePolicy.Expanding,
            Qt.QtWidgets.QSizePolicy.Fixed,
        ),
    )
    layout.addWidget(widget)

    layout.setStretch(
        2,
        1,
    )

    return layout


# ------------------------------------------------------------------------------
# noinspection PyPep8Naming
def getComboIndex(combo_box, label, ignore_casing=False):
    """
    This will return the index of the first matching label within a combo
    box qwidget.

    If no label is found 0 is returned

    :param combo_box: Widget to iterate through
    :type combo_box: QComboBox

    :param label: The combo label to match against
    :type label: str

    :param ignore_casing: If true, all text matching will be done with no
        consideration of capitalisation. The default is False.
    :type ignore_casing: bool

    :return: int
    """
    # -- Convert the label to lower case if we're ignoring casing
    label = label if not ignore_casing else label.lower()

    # -- Cycling our combo box and test the string
    for i in range(combo_box.count()):

        # -- Get the current item text, and lower the casing if we're
        # -- ignoring the casing. This means we're testing both sides
        # -- of the argument in lower case
        combo_text = combo_box.itemText(i)
        combo_text = combo_text if not ignore_casing else combo_text.lower()

        if combo_text == label:
            return i

    return 0


# ------------------------------------------------------------------------------
def setComboByText(combo_box, label, ignore_casing=False):
    """
    This will return the index of the first matching label within a combo
    box qwidget.

    If no label is found 0 is returned

    :param combo_box: Widget to iterate through
    :type combo_box: QComboBox

    :param label: The combo label to match against
    :type label: str

    :param ignore_casing: If true, all text matching will be done with no
        consideration of capitalisation. The default is False.
    :type ignore_casing: bool

    :return: int
    """
    idx = getComboIndex(combo_box, label, ignore_casing=ignore_casing)
    combo_box.setCurrentIndex(idx)

