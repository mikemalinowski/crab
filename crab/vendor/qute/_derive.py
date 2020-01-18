"""
This module attempts to access widgets and values in a blind manor - allowing
you to extract the most common forms of data from them. This is particularly
useful when you want to represent values through an interface without hard-
coding what they are.
"""
from .vendor.Qt import QtWidgets
import types


_NUMERIC_UI_MAX = 9*9*9
_NUMERIC_UI_MIN = _NUMERIC_UI_MAX * -1


# ------------------------------------------------------------------------------
def is_string(value):
    """
    Py2/3 compatible string testing

    :param value:
    :return:
    """
    try:
        return isinstance(value, basestring)
    except NameError:
        return isinstance(value, str)


# ------------------------------------------------------------------------------
def deriveWidget(value, label=''):
    """
    Given the data type of the value, this will make a guess at the best
    fit ui element to represent that value.
    
    :param value: The value you want to represent through a widget
    :type value: bool, int, float, str, list or dict.

    :param label: This is how any labelled widget will be displayed as
    :type label: str

    :return: QWidget
    """
    # -- Determine the type of the value coming in
    value_type = type(value)

    if value_type is bool:
        derived = QtWidgets.QCheckBox(label)
        derived.setChecked(value)
        return derived

    if is_string(value):
        derived = QtWidgets.QLineEdit()
        derived.setText(value)
        return derived

    if value_type is float:
        derived = QtWidgets.QDoubleSpinBox()
        derived.setMaximum(_NUMERIC_UI_MAX)
        derived.setMinimum(_NUMERIC_UI_MIN)
        derived.setValue(value)
        return derived

    if value_type is int:
        derived = QtWidgets.QSpinBox()
        derived.setMaximum(_NUMERIC_UI_MAX)
        derived.setMinimum(_NUMERIC_UI_MIN)
        derived.setValue(value)
        return derived

    if value_type in [list, tuple]:
        derived = QtWidgets.QComboBox()

        for item in value:
            derived.addItem(item)

        return derived

    elif value_type is dict:
        widget = QtWidgets.QComboBox()

        for k, v in value.items():
            widget.addItem(k, userData=v)
        return widget

    else:
        return None


# ------------------------------------------------------------------------------
def deriveValue(widget):
    """
    Given a QWidget it will call the widgets specific method to return 
    the likely value represented by that widget.
    
    :param widget: QWidget to derive the value from
    :type widget: QWidget

    :return: dependent on the widget
    """
    if isinstance(widget, QtWidgets.QAbstractSpinBox):
        return widget.value()

    if isinstance(widget, QtWidgets.QLineEdit):
        return widget.text()

    if isinstance(widget, QtWidgets.QComboBox):
        data = widget.itemData(widget.currentIndex())
        return data or widget.currentText()

    if isinstance(widget, QtWidgets.QAbstractButton):
        return widget.isChecked() if widget.isCheckable() else widget.isDown()

    return None


# ------------------------------------------------------------------------------
def setBlindValue(widget, value):
    """
    This is a blind setter method, where the type of widget is unknown and
    will therefore be handled within the function.

    :param widget: The widget you want to set the value for
    :type widget: QWidget

    :param value: The value you want to apply to the widget
    :type value: variable

    :return: True if a value was set 
    """
    if isinstance(widget, QtWidgets.QAbstractSpinBox):
        widget.setValue(float(value))
        return True

    if isinstance(widget, QtWidgets.QLineEdit):
        widget.setText(str(value))
        return True

    if isinstance(widget, QtWidgets.QComboBox):
        for i in range(widget.count()):
            if widget.itemText(i) == str(value):
                widget.setCurrentIndex(i)
                return True

    if isinstance(widget, QtWidgets.QAbstractButton):
        widget.setChecked(bool(value))
        return True

    return False


# ------------------------------------------------------------------------------
def connectBlind(widget, callback):
    """
    This is a blind approach to connecting the most likely value change
    event of a given widget to the given callback.
    
    Note: Because of the nature of signals, they can give a variety of 
    different arguments during the signal call. For that reason it is 
    highly recommended to utilise *args, **kwargs within the callback 
    if you do not know exactly which signal will be connected.
    
    :param widget: The widget expected to emit the change signal
    :type widget: QWidget

    :param callback: The callback/function which should be called upon
        a value changed event
    :type callback: callable object

    :return: True on successful connection, False otherwise.
    """
    if isinstance(widget, QtWidgets.QLineEdit):
        widget.textChanged.connect(callback)
        return True

    if isinstance(widget, QtWidgets.QAbstractSpinBox):
        widget.valueChanged.connect(callback)
        return True

    if isinstance(widget, QtWidgets.QComboBox):
        widget.currentIndexChanged.connect(callback)
        return True

    if isinstance(widget, QtWidgets.QAbstractButton):
        widget.clicked.connect(callback)
        return True

    return False
