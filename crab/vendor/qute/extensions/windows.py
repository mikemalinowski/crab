from ..vendor import Qt
from ..vendor import scribble


# ------------------------------------------------------------------------------
# noinspection PyPep8Naming,PyUnresolvedReferences
class MemorableWindow(Qt.QtWidgets.QMainWindow):

    # -- How many pixels of a window we expect to see
    # -- before we re-position it
    _SCREEN_BUFFER = 12

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
            try:
                self.restoreSize()
            except:
                pass

            try:
                self.restore()
            except:
                pass

    def restore(self):
        settings = Qt.QtCore.QSettings('quteSettings', self.objectName())
        self.restoreState(settings.value('windowState'))

    def save(self):
        settings = Qt.QtCore.QSettings('quteSettings', self.objectName())
        settings.setValue('windowState', self.saveState())
        self.storeSize()

    def closeEvent(self, event):
        self.save()
        super(MemorableWindow, self).closeEvent(event)

    # --------------------------------------------------------------------------
    def restoreSize(self):
        stored_data = scribble.get(self.objectName())

        # -- Get the screen rect, as we need to make sure
        # -- we're not about to open the window offscreen
        screen_rect = Qt.QtWidgets.QApplication.desktop().availableGeometry()

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

            # -- Ensure the window is not too far off to the left
            # -- side of the screen, and ensure that we see at least
            # -- some of the window
            if geom[0] + (geom[2] - self._SCREEN_BUFFER) < 0:
                geom[0] = 300

            # -- Ensure that its not too far to the right, making
            # -- sure that we see at least some of the window
            if geom[0] + self._SCREEN_BUFFER > screen_rect.width():
                geom[0] = 300

            # -- Check if the window is above the available monitor space
            # -- we dont need to use the buffer on this, because we dont
            # -- want the title bar to go too high
            if geom[1] < 0:
                geom[1] = 300

            # -- Check if the window is below the monitor with at least
            # -- a small amount of the title bar to grab
            if geom[1] + self._SCREEN_BUFFER > screen_rect.height():
                geom[1] = 300

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
