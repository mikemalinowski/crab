"""
This module is specifically intended for use when in environments where
you're actively trying to share/develop tools across multiple applications
which support PyQt, PySide or PySide2. 

The premise is that you can request the main application window using 
a common function regardless of the actual application - making it trivial
to implement a tool which works in multiple host applications without any
bespoke code.

The current list of supported applications are:

    * Native Python
    * Maya
    * 3dsmax
    * Motion Builder

"""
import sys

from .vendor import Qt
from .vendor import scribble


# ------------------------------------------------------------------------------
def get_host():

    global HOST

    if HOST:
        return HOST

    if 'maya.exe' in sys.executable or 'mayapy.exe' in sys.executable:
        HOST = 'Maya'
        return HOST

    if 'motionbuilder.exe' in sys.executable:
        HOST = 'Mobu'
        return HOST

    if '3dsmax.exe' in sys.executable:
        HOST = 'Max'
        return HOST

    houdini_execs = [
        'houdini.exe',
        'houdinifx.exe',
        'houdinicore.exe',
    ]
    if any(houdini_exec in sys.executable for houdini_exec in houdini_execs):
        HOST = 'Houdini'
        return HOST

    return 'Pure'


# ------------------------------------------------------------------------------
def mainWindow():
    """
    Returns the main window regardless of what the host is
    
    :return: 
    """
    return HOST_MAPPING[get_host()]()


# ------------------------------------------------------------------------------
def returnNativeWindow():
    for candidate in Qt.QtWidgets.QApplication.topLevelWidgets():
        if isinstance(candidate, Qt.QtWidgets.QMainWindow):
            return candidate


# ------------------------------------------------------------------------------
def _findWindowByTitle(title):
    # -- Find the main application window
    for candidate in Qt.QtWidgets.QApplication.topLevelWidgets():
        try:
            if title in candidate.windowTitle():
                return candidate
        except: pass

# ------------------------------------------------------------------------------
def returnModoMainWindow():
    pass


# ------------------------------------------------------------------------------
def returnMaxMainWindow():
    return _findWindowByTitle('Autodesk 3ds Max')


# ------------------------------------------------------------------------------
def returnMayaMainWindow():
    from maya import OpenMayaUI as omui
    from shiboken2 import wrapInstance

    try:
        return wrapInstance(
            long(omui.MQtUtil.mainWindow()),
            Qt.QtWidgets.QWidget,
        )

    except:
        return None


# ------------------------------------------------------------------------------
def returnHoudiniMainWindow():
    import hou
    return hou.qt.mainWindow()


# ------------------------------------------------------------------------------
def returnMobuMainWindow():
    return _findWindowByTitle('MotionBuilder 20')


# ------------------------------------------------------------------------------
# noinspection PyPep8Naming
class MemorableWindow(Qt.QtWidgets.QMainWindow):

    # --------------------------------------------------------------------------
    def __init__(self, identifier=None, offsetX=7, offsetY=32, *args, **kwargs):
        super(MemorableWindow, self).__init__(*args, **kwargs)

        self._offsetX = offsetX
        self._offsetY = offsetY

        # -- If we're given an id, set this object name
        if identifier:
            self.setObjectName(identifier)

            # -- If there is any scribble data for this id we should
            # -- update this windows geometry accordingly.
            self.restoreSize()

    # --------------------------------------------------------------------------
    def restoreSize(self):
        stored_data = scribble.get(self.objectName())

        if 'geometry' in stored_data:
            geom = stored_data.get(
                'geometry',
                [
                    300,
                    300,
                    400,
                    400,
                ],
            )

            self.setGeometry(
                geom[0],
                geom[1],
                geom[2],
                geom[3],
            )

    # --------------------------------------------------------------------------
    def storeSize(self):
        stored_data = scribble.get(self.objectName())
        stored_data['geometry'] = [
            self.pos().x() + self._offsetX,
            self.pos().y() + self._offsetY,
            self.width(),
            self.height(),
        ]
        stored_data.save()

    # --------------------------------------------------------------------------
    def resizeEvent(self, event):
        self.storeSize()
        super(MemorableWindow, self).resizeEvent(event)

    # --------------------------------------------------------------------------
    def moveEvent(self, event):
        self.storeSize()
        super(MemorableWindow, self).moveEvent(event)

    # --------------------------------------------------------------------------
    def hideEvent(self, event):
        self.storeSize()
        super(MemorableWindow, self).hideEvent(event)


# ------------------------------------------------------------------------------
HOST = None
HOST_MAPPING = dict(
    Maya=returnMayaMainWindow,
    Max=returnMaxMainWindow,
    Modo=returnModoMainWindow,
    Mobu=returnMobuMainWindow,
    Pure=returnNativeWindow,
    Houdini=returnHoudiniMainWindow,
)
