from .vendor import Qt
from ._utils import qApp
from ._windows import MemorableWindow
from ._windows import mainWindow


# ------------------------------------------------------------------------------
def quick_app(window_title):
    """
    Decorator to use on a function that is expected to return a widget that
    will be set as the Main Widget in the window that is created.

    :param window_title: App and window title.
    :type window_title: str
    """
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            q_app = qApp()
            
            widget = func(*args, **kwargs)
            
            window = MemorableWindow(
                identifier=window_title,
                parent=mainWindow(),
            )
            
            window.setCentralWidget(widget)
            
            # -- Set the window properties
            window.setWindowTitle(window_title)
            
            # -- Show the ui, and if we're blocking call the exec_
            window.show()
            
            q_app.exec_()
            
            return window
        
        return wrapper
    
    return decorator


# ------------------------------------------------------------------------------
def confirm(title='Text Request', label='', parent=None, **kwargs):
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
def getText(title='Text Request', label='', parent=None, **kwargs):
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
def getFilepath(title='Text Request',
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
def getFolderPath(title='Folder Request', path='', parent=None):
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


# ------------------------------------------------------------------------------
def horizontalDivider(height=2):
    """
    Horizontal divider for use in UIs that require such a widget.
    
    :param height: height in pixels (integer) of the divider. Defaults to 2.
    :type height: int
    
    :return: QFrame Instance, the divider.
    :rtype: QFrame
    """
    result = Qt.QtWidgets.QFrame()
    result.setFrameShape(Qt.QtWidgets.QFrame.HLine)
    result.setFrameShadow(Qt.QtWidgets.QFrame.Sunken)
    result.setStyleSheet("background-color: rgb(20,20,20)")
    result.setFixedHeight(height)
    return result
