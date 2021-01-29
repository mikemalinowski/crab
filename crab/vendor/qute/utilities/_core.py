from ..vendor import Qt


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

