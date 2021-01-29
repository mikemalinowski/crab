"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
FlowLayout
Custom layout that mimics the behaviour of a flow layout (not supported in PyQt by default)
Just added comments on the offical PySide example.
@date 08-2013
@source http://josbalcaen.com/pyqt-flowlayout-maya-python/
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
from ..vendor import Qt



class FlowLayout(Qt.QtWidgets.QLayout):
    """Custom layout that mimics the behaviour of a flow layout"""

    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        self._margin = 0
        # Set margin and spacing
        if parent is not None:
            self.setMargin(margin)

        self.setSpacing(spacing)

        self.itemList = []

    def margin(self):
        return self._margin

    def setMargin(self, value):
        self._margin = value

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def insertWidget(self, index, widget):
        item = Qt.QtWidgets.QWidgetItem(widget)
        self.itemList.insert(index, item)

    def expandingDirections(self):
        return Qt.QtCore.Qt.Orientations(Qt.QtCore.Qt.Horizontal)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(Qt.QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        # Calculate the size
        size = Qt.QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        # Add the margins
        size += Qt.QtCore.QSize(2 * self.margin(), 2 * self.margin())

        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(Qt.QtCore.QRect(Qt.QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
