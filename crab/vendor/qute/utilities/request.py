from ..vendor import Qt
from . import qApp


# ------------------------------------------------------------------------------
def message(title='Text Request', label='', parent=None, **kwargs):
    """
    Quick and easy access for getting text input. You do not have to have a
    QApplication instance, as this will look for one.

    :return: str, or None
    """
    # -- Ensure we have a QApplication instance
    q_app = qApp()

    answer = Qt.QtWidgets.QMessageBox.information(
        parent,
        title,
        label,
    )

    return True


# ------------------------------------------------------------------------------
def confirmation(title='Text Request', label='', parent=None, **kwargs):
    """
    Quick and easy access for getting text input. You do not have to have a
    QApplication instance, as this will look for one.

    :return: str, or None
    """
    # -- Ensure we have a QApplication instance
    q_app = qApp()

    answer = Qt.QtWidgets.QMessageBox.warning(
        parent,
        title,
        label,
        Qt.QtWidgets.QMessageBox.Yes,
        Qt.QtWidgets.QMessageBox.No,
    )

    if answer == Qt.QtWidgets.QMessageBox.Yes:
        return True

    return False


# ------------------------------------------------------------------------------
def text(title='Text Request', label='', parent=None, **kwargs):
    """
    Quick and easy access for getting text input. You do not have to have a
    QApplication instance, as this will look for one.

    :return: str, or None
    """
    # -- Ensure we have a QApplication instance
    q_app = qApp()

    # -- Get the text
    name, ok = Qt.QtWidgets.QInputDialog.getText(
        parent,
        title,
        label,
        **kwargs
    )

    if not ok:
        return None

    return name


# ------------------------------------------------------------------------------
def filepath(title='Text Request',
                save=True,
                path='',
                filter_='* (*.*)',
                parent=None,
                **kwargs):
    """
    Quick and easy access for getting text input. You do not have to have a
    QApplication instance, as this will look for one.

    :return: str, or None
    """

    # -- Ensure we have a q application instance
    q_app = qApp()

    # -- Ask for the editor location
    func = Qt.QtWidgets.QFileDialog.getOpenFileName

    if save:
        func = Qt.QtWidgets.QFileDialog.getSaveFileName

    value, _ = func(
        parent,
        title,
        path,
        filter_,
    )

    return value


# ------------------------------------------------------------------------------
def folderpath(title='Folder Request', path='', parent=None):
    """
    Quick function for requesting a folder path

    :param title:
    :param path:
    :return:
    """
    q_app = qApp()

    return Qt.QtWidgets.QFileDialog.getExistingDirectory(
        parent,
        title,
        path,
        Qt.QtWidgets.QFileDialog.ShowDirsOnly,
    )

