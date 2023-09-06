import os

from ...vendor import qute


# --------------------------------------------------------------------------------------------------
def get_resource(name):
    return os.path.join(
        os.path.dirname(__file__),
        "resources",
        name,
    )


# --------------------------------------------------------------------------------------------------
def show_tooltip(title=None, descriptive=None, graphic=None, instigator=None):
    """
    For the sake of optimisation we only ever instance a single tooltip if
    we can. Therefore this function handles the concept of a singleton.

    :param title: Title to show in the tooltip
    :type title: str

    :param descriptive: A descriptive breakdown for the user
    :type descriptive: str

    :param graphic: An absolute path to a gif demonstrating the behaviour
    :type graphic: str

    :return: carapace.ui.widgets.Tooltip instance
    """
    # -- TODO: This should be removed, its here only whilst
    # -- debugging
    title = title or "Test"
    descriptive = descriptive or "this is a demonstration of a tooltip"
    graphic = graphic or get_resource("crab.gif")
    pos = qute.QCursor.pos()

    # -- Ensure we have a parent - we use the maya window
    parent = qute.utilities.windows.mainWindow()

    # -- If we have an active instance, we strive to re-utilise it
    if TooltipWindow.ACTIVE_INSTANCE:
        try:
            TooltipWindow.ACTIVE_INSTANCE.setData(
                title,
                descriptive,
                graphic,
            )

            TooltipWindow.ACTIVE_INSTANCE.setGeometry(
                pos.x(),
                pos.y(),
                TooltipWindow.ACTIVE_INSTANCE.size().width(),
                TooltipWindow.ACTIVE_INSTANCE.size().height(),
            )

            TooltipWindow.ACTIVE_INSTANCE.show()
            return TooltipWindow.ACTIVE_INSTANCE
        except:
            pass

    # -- In this scenario we could not re-use an existing
    # -- instance, so we shall create a new one
    TooltipWindow.ACTIVE_INSTANCE = TooltipWindow(
        title,
        descriptive,
        graphic,
        instigator,
        parent=parent
    )

    TooltipWindow.ACTIVE_INSTANCE.setGeometry(
        pos.x() - 20,
        pos.y() - 20,
        TooltipWindow.ACTIVE_INSTANCE.size().width(),
        TooltipWindow.ACTIVE_INSTANCE.size().height(),
    )

    TooltipWindow.ACTIVE_INSTANCE.show()

    return TooltipWindow.ACTIVE_INSTANCE


# --------------------------------------------------------------------------------------------------
class ToolTip(qute.QWidget):
    """
    This is the central area  of a tool tip, and the area responsible for showing the
    information to the user
    """

    # ----------------------------------------------------------------------------------------------
    def __init__(self, title, descriptive, graphic, instigator, parent=None):
        super(ToolTip, self).__init__(parent=parent)

        # -- We store the movie as a variable to allow us to stop it
        # -- whenever the widget is not visible
        self._movie = None
        self.instigator = instigator

        # --- Set the default layout
        self.setLayout(
            qute.utilities.layouts.slimify(
                qute.QVBoxLayout(),
            ),
        )

        # -- Define the styling based on the css data
        qute.utilities.styling.apply(
            [
                get_resource("tooltip.css")
            ],
            apply_to=self,
        )

        # -- Load in the ui file
        self.ui = qute.utilities.designer.load(
            get_resource("tooltip.ui"),
        )
        self.layout().addWidget(self.ui)

        # -- Finally apply the data to show in the tooltip
        self.setData(
            title,
            descriptive,
            graphic,
            instigator,
        )

    # ----------------------------------------------------------------------------------------------
    def optimize(self):
        if self._movie:
            self._movie.stop()

    # ----------------------------------------------------------------------------------------------
    def hideEvent(self, *args, **kwargs):
        """
        Whenever this widget is hidden we explicitly stop the movie to ensure
        we"re being as optimal as possible.

        :return:
        """
        self.optimize()

    # ----------------------------------------------------------------------------------------------
    def leaveEvent(self, event):
        """
        Whenever we leave this widgets area we want to hide the window

        :param event:
        :return:
        """
        self.window().hide()

        # -- When we leave, attempt to give the focus back to the window
        # -- that instigated us
        if self.instigator:
            self.instigator.activateWindow()

    # ----------------------------------------------------------------------------------------------
    def setData(self, title, descriptive, graphic, instigator):
        """
        Allows the setting of data within the tooltip

        :param title: Title to show in the tooltip
        :type title: str

        :param descriptive: A descriptive breakdown for the user
        :type descriptive: str

        :param graphic: An absolute path to a gif demonstrating the behaviour
        :type graphic: str

        :return:
        """
        # -- Update the instigator
        self.instigator = instigator

        # -- Apply the data textural data
        self.ui.title.setText(title)
        self.ui.descriptive.setText(descriptive)

        # -- Now we assign the movie and play it
        self._movie = qute.QMovie(graphic)

        # -- Get the default size
        default_size = qute.QImage(graphic).size()

        # -- Get how much we need to scale this by to fit a 400 width
        factor = 400.0 / (default_size.width() or 1.0)

        # -- Scale the movie
        self._movie.setScaledSize(
            qute.QSize(
                default_size.width() * factor,
                default_size.height() * factor,
            ),
        )
        self.ui.graphic.setMovie(self._movie)
        self._movie.start()


# --------------------------------------------------------------------------------------------------
class TooltipWindow(qute.QMainWindow):

    # -- Define class variables so we do not have to reinitialise them
    # -- as these are considered constants.
    BACKGROUND_COLOR = qute.QColor(46, 46, 46, a=200)
    PEN = qute.QPen(qute.Qt.black, 3)
    ROUNDING = 5
    ACTIVE_INSTANCE = None

    # ----------------------------------------------------------------------------------------------
    def __init__(self, title, descriptive, graphic, instigator, parent=None):
        super(TooltipWindow, self).__init__(parent=parent)

        # -- Set the window to not have a title bar and have the background
        # -- be transparent
        self.setWindowFlags(qute.Qt.Window | qute.Qt.FramelessWindowHint)
        self.setAttribute(qute.Qt.WA_TranslucentBackground)

        # -- Assign the central widget
        self.setCentralWidget(
            ToolTip(
                title,
                descriptive,
                graphic,
                instigator,
                parent=self,
            ),
        )

    # ----------------------------------------------------------------------------------------------
    def paintEvent(self, event):
        """
        We override the paint event to allow us to draw with nice rounded edges

        :param event:
        :return:
        """
        qp = qute.QPainter()
        qp.begin(self)
        qp.setRenderHint(
            qute.QPainter.Antialiasing,
            True,
        )

        qsize = self.size()

        gradient = qute.QLinearGradient(0, 0, 0, qsize.height())
        gradient.setColorAt(0, qute.QColor(100, 20, 0, a=175))
        gradient.setColorAt(1, qute.QColor(50, 50, 50, a=175))

        qp.setPen(self.PEN)
        qp.setBrush(gradient) # self.BACKGROUND_COLOR)

        qp.drawRoundedRect(
            0,
            0,
            qsize.width(),
            qsize.height(),
            self.ROUNDING,
            self.ROUNDING,
        )
        qp.end()

    # ----------------------------------------------------------------------------------------------
    def setData(self, title, descriptive, graphic):
        """
        Allows the setting of data within the tooltip

        :param title: Title to show in the tooltip
        :type title: str

        :param descriptive: A descriptive breakdown for the user
        :type descriptive: str

        :param graphic: An absolute path to a gif demonstrating the behaviour
        :type graphic: str
        :return:
        """
        self.centralWidget().setData(title, descriptive, graphic)
