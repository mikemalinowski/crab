"""
This module contains the ui elements relating to the setting and storing
of tool settings.
"""
import sys
import functools

from ...vendor import qute
from ...vendor import scribble

_SCRIBBLE_PREFIX = 'crabanimator_'


# --------------------------------------------------------------------------------------------------
def get(tool_identifier, defaults=None):
    """
    Returns the settings stored for a given tool
    
    :param tool_identifier: Unique identifier for the tool
    :type tool_identifier: str
    
    :param defaults: A dictionary of settings to use as defaults if no values are stored
    :type defaults: dict
     
    :return: dict 
    """
    
    # -- Construct our scribble key
    scribble_key = _SCRIBBLE_PREFIX + tool_identifier
    
    # -- Get the stored options. This will be an empty dictionary if there
    # -- were not stored options
    stored_options = scribble.get(scribble_key)
    
    # -- If we have been given defaults, we use them as a base, and then layer
    # -- the stored options over the top
    if defaults:
        copied_defaults = defaults.copy()
        copied_defaults.update(stored_options)
        stored_options = copied_defaults

    return stored_options


# --------------------------------------------------------------------------------------------------
def show_options(tool_identifier, defaults=None, pos=None, parent=None):
    """
    This function will show the options panel for the given scribble key.

    :param tool_identifier: Unique identifier for the tool
    :type tool_identifier: str
    
    :param defaults: Any default values which need to be shown if there are
        no saved settings for values
    :type defaults: dict

    :return: _OptionsWindow instance
    """
    # -- If we have an active instance, we strive to re-utilise it as we dont
    # -- want to be generating lots of windows
    if _OptionsWindow.ACTIVE_INSTANCE:
        try:
            _OptionsWindow.ACTIVE_INSTANCE.buildOptions(tool_identifier, defaults=defaults)

            if pos:
                _OptionsWindow.ACTIVE_INSTANCE.setGeometry(
                    pos.x(),
                    pos.y(),
                    1,
                    1,
                )

            _OptionsWindow.ACTIVE_INSTANCE.show()
            _OptionsWindow.ACTIVE_INSTANCE.raise_()
            return _OptionsWindow.ACTIVE_INSTANCE

        except:
            # -- If anything goes wrong during the window re-use code we simply
            # -- log it and create a new window
            print('Could not re-use window. Creating new window.')
            print(sys.exc_info())
            pass

    # -- In this scenario we could not re-use an existing
    # -- instance, so we shall create a new one
    _OptionsWindow.ACTIVE_INSTANCE = _OptionsWindow(
        tool_identifier,
        defaults=defaults,
        parent=parent
    )
    
    # -- If we're given a specific location to place the window, we do that now
    if pos:
        _OptionsWindow.ACTIVE_INSTANCE.setGeometry(
            pos.x(),
            pos.y(),
            1,
            1,
        )
    
    # -- Ensure the window is visible
    _OptionsWindow.ACTIVE_INSTANCE.show()
    _OptionsWindow.ACTIVE_INSTANCE.raise_()
    return _OptionsWindow.ACTIVE_INSTANCE


# --------------------------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class _OptionsWidget(qute.QWidget):
    """
    This window is responsible for the layout of the option elements

    :param tool_identifier: Unique identifier for the tool
    :type tool_identifier: str

    :param defaults: Any default values which need to be shown if there are
        no saved settings for values
    :type defaults: dict

    """

    # ----------------------------------------------------------------------------------------------
    def __init__(self, tool_identifier, defaults=None, parent=True):
        super(_OptionsWidget, self).__init__(parent=parent)

        # -- Store the tool identifier
        self._tool_identifier = tool_identifier

        # -- We keep track of the widgets we generate to make it easy
        # -- to query and clean later
        self._widgets = dict()

        # -- Create our base layout
        self.setLayout(
            qute.QVBoxLayout(),
        )

        # -- Add our title and separator - so we can distinguish between
        # -- the title and the options
        self.main_label = qute.QLabel('Tool Options')
        self.layout().addWidget(self.main_label)

        self.line = qute.QFrame()
        self.line.setFrameShape(qute.QFrame.HLine)
        self.line.setFrameShadow(qute.QFrame.Sunken)
        self.layout().addWidget(self.line)

        # -- Now create the options layout
        self.options_layout = qute.QVBoxLayout()
        self.layout().addLayout(self.options_layout)

        # -- Set the key, which triggers a rebuild of the dynamic properties
        self.buildOptions(
            tool_identifier=tool_identifier,
            defaults=defaults,
        )

    # ----------------------------------------------------------------------------------------------
    def buildOptions(self, tool_identifier, defaults=None):
        """
        This triggers a rebuild of all the options, based on the given tool
        identifier

        :param tool_identifier: Unique identifier for the tool
        :type tool_identifier: str

        :param defaults: Any default values which need to be shown if there are
            no saved settings for values
        :type defaults: dict

        :return:
        """
        # -- Update the identifier
        self._tool_identifier = tool_identifier

        # -- Clear out our cache
        self._widgets = dict()

        # -- Clear out the layout so we can start rebuilding it
        qute.utilities.layouts.empty(self.options_layout)

        # -- Merge the data, starting with the defaults as a base, then
        # -- overlaying with any stored preferences
        settings = defaults or dict()
        settings.update(get(self._tool_identifier))

        # -- We can now start building our widgets to represent
        # -- the scribble data
        for key in sorted(settings.keys()):

            # -- If any setting starts with an underscore we assume
            # -- it is a visual hint or private
            if key.startswith('_'):
                continue

            # -- Get the current value
            value = settings[key]

            # -- Check if this key has a visual hint, if it does then we assign
            # -- a visual override. This allows for strings to be displayed as
            # -- lists etc.
            visual_override = None
            if '_' + key in settings:
                visual_override = settings['_' + key]

            # -- Generate a widget to represent this value
            _widget = qute.utilities.derive.deriveWidget(
                visual_override or value,
            )

            # -- Add a label against each option so the user understands
            # -- what each setting does
            label_layout = qute.utilities.widgets.addLabel(
                _widget,
                self._createDisplayName(key),
                min_label_width=150,
            )

            # -- Add the widget to our layout
            self.options_layout.addLayout(label_layout)

            # -- Hook up the change event
            _widget.setObjectName(key)

            # -- Store the widget in our scribble map
            self._widgets[key] = _widget

            qute.utilities.derive.connectBlind(
                _widget,
                functools.partial(
                    self._storeChange,
                    key,
                    _widget,
                )
            )

    # --------------------------------------------------------------------------
    def _createDisplayName(self, name):
        """
        Convenience function for turning strings into nicer display strings

        :param name: Name to convert
        :type name: str

        :return: str
        """
        resolved_name = list()

        for idx, letter in enumerate(name):
            if letter.isupper():
                if idx != len(name):
                    resolved_name.append(' ')

            resolved_name.append(letter)

        resolved_name = ''.join(resolved_name)
        resolved_name = resolved_name.replace('_', ' ')
        resolved_name = resolved_name.title()

        return resolved_name

    # ----------------------------------------------------------------------------------------------
    def _storeChange(self, key, widget, *args, **kwargs):
        """
        This is used to trigger a save of settings values.

        :param key: The name of the setting to store the change for
        :type key: str

        :param widget: The widget that has been changed by the user
        :type widget: qute.QWidget

        :return:
        """
        # -- Access the stored settings
        options = scribble.get(_SCRIBBLE_PREFIX + self._tool_identifier)

        # -- Update the changed key with the value from the ui
        options[key] = qute.utilities.derive.deriveValue(widget)

        # -- Save the changes
        options.save()

    # ----------------------------------------------------------------------------------------------
    def leaveEvent(self, event):
        """
        Whenever we leave this widgets area we want to hide the window

        :param event:
        :return:
        """
        # -- Map the geometry of the window to worldspace. We do this because
        # -- some widgets trigger a leaveEvent call (such as combo boxes) and we
        # -- do not want to hide the window when the user clicks one of these.
        rect = self.geometry()
        global_rect = qute.QRect(self.mapToGlobal(rect.topLeft()), rect.size())

        if not global_rect.contains(qute.QCursor().pos()):
            self.window().hide()


# --------------------------------------------------------------------------------------------------
class _OptionsWindow(qute.QMainWindow):
    """
    Main window which shows the options information
    """
    # -- We used this to track the active instance to allow us
    # -- to re-use it where possible
    ACTIVE_INSTANCE = None

    # -- Define class variables so we do not have to reinitialise them
    # -- as these are considered constants.
    BACKGROUND_COLOR = qute.QColor(46, 46, 46, a=200)
    PEN = qute.QPen(qute.Qt.black, 1)
    ROUNDING = 8

    # ----------------------------------------------------------------------------------------------
    def __init__(self, tool_identifier, defaults=None, parent=None):
        super(_OptionsWindow, self).__init__(parent=parent)

        # -- Set the window to not have a title bar and have the background
        # -- be transparent
        self.setWindowFlags(qute.Qt.Window | qute.Qt.FramelessWindowHint)
        self.setAttribute(qute.Qt.WA_TranslucentBackground)

        # -- Assign the central widget
        self.setCentralWidget(
            _OptionsWidget(
                tool_identifier=tool_identifier,
                defaults=defaults,
                parent=self,
            ),
        )

    # ----------------------------------------------------------------------------------------------
    def buildOptions(self, tool_identifier, defaults=None):
        self.centralWidget().buildOptions(tool_identifier, defaults=defaults)

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
        gradient.setColorAt(0, qute.QColor(150, 150, 150, a=150))
        gradient.setColorAt(1, qute.QColor(50, 50, 50, a=150))

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
