from ..vendor import Qt


# ------------------------------------------------------------------------------
class HorizontalDivider(Qt.QtWidgets.QFrame):

    # ------------------------------------------------------------------------------
    def __init__(self, height=2):
        super(HorizontalDivider, self).__init__()
        self.setFrameShape(Qt.QtWidgets.QFrame.HLine)
        self.setFrameShadow(Qt.QtWidgets.QFrame.Sunken)
        self.setStyleSheet("background-color: rgb(20,20,20)")
        self.setFixedHeight(height)
