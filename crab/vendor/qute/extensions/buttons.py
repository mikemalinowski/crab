from ..vendor import Qt

from .. import utilities
from .. import resources


# --------------------------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class CopyToClipboardButton(Qt.QtWidgets.QPushButton):

    def __init__(self, value, size, tooltip='Copy to clipboard', fixed_size=True, parent=None):
        super(CopyToClipboardButton, self).__init__(parent=parent)

        # -- Store the value to copy
        self._value = value

        # -- Set an icon
        self.setIcon(
            Qt.QtGui.QIcon(
                resources.get('copy_to_clipboard.png'),
            )
        )

        # -- Fix the size of the button if requested
        if fixed_size:
            self.setFixedSize(size)

        # -- Assign the tooltip
        self.setToolTip(tooltip)

        # -- Hook up the callback
        self.clicked.connect(self._callback)

    # ----------------------------------------------------------------------------------------------
    def setCopyValue(self, value):
        self._value = value

    # ----------------------------------------------------------------------------------------------
    def copyValue(self):
        return self._value

    # ----------------------------------------------------------------------------------------------
    def _callback(self):
        utilities.qApp().clipboard().setText(self._value)
