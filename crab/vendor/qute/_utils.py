"""
This holds a set of small helper functions
"""
from .vendor import Qt


# ------------------------------------------------------------------------------
def addLabel(widget, label):
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
    layout = slimify(Qt.QtWidgets.QHBoxLayout())

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


# --------------------------------------------------------------------------
def emptyLayout(layout):
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
            emptyLayout(item.layout())


# ------------------------------------------------------------------------------
def toList(given):
    """
    This will take what is given and wrap it in a list if it is not already
    a list, otherwise it will simply return what it has been given.
     
    :return: list()
    """
    if not isinstance(given, (tuple, list)):
        given = [given]

    return given


# ------------------------------------------------------------------------------
def slimify(layout):
    # -- Apply the formatting
    layout.setContentsMargins(
        *[0, 0, 0, 0]
    )
    layout.setSpacing(0)

    return layout


# --------------------------------------------------------------------------
def toGrayscale(pixmap):
    """
    Creates a new pixmap which is a grayscale version of the given
    pixmap

    :param pixmap: QPixmap

    :return: QPixmap
    """
    # -- Get an image object
    image = pixmap.toImage()

    # -- Cycle the pixels and convert them to grayscale
    for x in range(image.width()):
        for y in range(image.height()):

            # -- Grayscale the pixel
            gray = Qt.QtGui.qGray(
                image.pixel(
                    x,
                    y,
                ),
            )

            # -- Set the pixel back into the image
            image.setPixel(
                x,
                y,
                Qt.QtGui.QColor(
                    gray,
                    gray,
                    gray,
                ).rgb()
            )

    # -- Re-apply the alpha channel
    image.setAlphaChannel(
        pixmap.toImage().alphaChannel()
    )

    # -- Return the pixmap
    return Qt.QtGui.QPixmap.fromImage(image)


# ------------------------------------------------------------------------------
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
def qApp(*args, **kwargs):
    """
    This will return the QApplication instance if one is available, otherwise
    it will create one
    
    :return: QApplication Instance 
    """
    q_app = Qt.QtWidgets.QApplication.instance()

    if not q_app:
        q_app = Qt.QtWidgets.QApplication([])

    return q_app

