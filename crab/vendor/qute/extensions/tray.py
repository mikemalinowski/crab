"""
Holds System Tray utilities and classes
"""
import sys
import functools
import datetime

from ..vendor import scribble
from ..vendor import Qt
from .. import utilities


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class LogWindow(Qt.QtWidgets.QMainWindow):

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(LogWindow, self).__init__(parent=parent)

        # -- Define a title expressing what the window is
        self.setWindowTitle('Logs')

        # -- We only need one widget - a text window
        self.text_edit = Qt.QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(self.text_edit.NoWrap)

        # -- Drop in the logs
        self.text_edit.document().setPlainText(''.join(OutputStream.Logs))
        self.setCentralWidget(self.text_edit)

        # -- Make it pretty and consistent with our styling
        utilities.styling.apply(['space'], self)

        # -- Track the log count
        self.log_count = 0

        # -- To prevent us from having to deal with emissions from
        # -- different threads, and thread safety we simply update
        # -- the view on a timer
        self._timer = Qt.QtCore.QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self.updateEntries)
        self._timer.start()

    # --------------------------------------------------------------------------
    def updateEntries(self):
        """
        Triggers an update of the logs, based on the log stream

        :return:
        """
        # -- If the amount of logs has not changed, we do nothing
        # if self.log_count == len(OutputStream.Logs):
        #     return

        # -- Set the text of the logs
        self.text_edit.document().setPlainText(''.join(OutputStream.Logs))
        self.text_edit.ensureCursorVisible()

        # -- Store how many logs we have dealt with, so we can see
        # -- if anything needs updating next time around
        self.log_count = len(OutputStream.Logs)

    # --------------------------------------------------------------------------
    def hideEvent(self, *args, **kwargs):
        """
        When the window is hidden, we do not need to update the view

        :return:
        """
        self._timer.stop()

    # --------------------------------------------------------------------------
    def showEvent(self, *args, **kwargs):
        """
        When the window is hidden, we do not need to update the view

        :return:
        """
        self._timer.start()


# ------------------------------------------------------------------------------
class OutputStream(object):
    """
    Log class to retrieve log information from
    """
    Logs = list()

    MAX_ENTRIES = 10000

    # --------------------------------------------------------------------------
    def write(self, text_):
        if not text_.strip():
            return
        try:
            text_ = text_.decode('ascii')
        except:
            return
        OutputStream.Logs.append('\n' + str(datetime.datetime.now()) + ' :: ' + text_.strip())
        OutputStream.Logs = OutputStream.Logs[len(OutputStream.Logs) - OutputStream.MAX_ENTRIES:]


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class TimedProcessorTray(Qt.QtWidgets.QSystemTrayIcon):
    """
    This holds a timed processing system tray implementation
    """
    def __init__(self,
                 icon,
                 auto_process=False,
                 interval=5,
                 verbose=False,
                 *args,
                 **kwargs):
        super(TimedProcessorTray, self).__init__(*args, **kwargs)

        self._log_window = None

        # -- Store any options we have been given about how we should
        # -- perform any processing
        self.verbose = verbose
        self._process_on_timer = auto_process
        self._process_interval = float(interval)

        # -- We will use this to hold a thread from
        # -- which we will carry out our processing
        self._process_thread = None

        # -- Define a list of processes we need to call whenever
        # -- we need to process
        self._process_calls = list()

        # -- Define a list of additional menu items which should
        # -- be added to the menu
        self._user_menu_actions = list()

        # -- Define our context menu. We will update this whenever
        # -- the user requests the menu
        self._menu = Qt.QtWidgets.QMenu()
        self.setContextMenu(self._menu)

        # -- Set the icon of the tray item.
        self.setIcon(Qt.QtGui.QIcon(icon))

        # -- Create the timer object which we will use
        # -- to define when a processing run will occur
        self._timer = Qt.QtCore.QTimer()
        self._timer.setInterval(self._process_interval * 1000)

        # -- If we're set to auto scan, then start a scan
        # -- immediately
        if self._process_on_timer:
            self._timer.start()

        # -- Ensure that when the timer trickles down
        # -- we begin a processing run
        self._timer.timeout.connect(self.beginProcessing)

        # -- Hook up signals and slots. We use this signal to generate
        # -- the menu on-demand. This way the data is always correct at
        # -- the point in time when the user requests it
        self.activated.connect(self.onActivate)

    # --------------------------------------------------------------------------
    def onActivate(self, reason):
        if reason == self.DoubleClick:
            self._log_window = LogWindow()
            self._log_window.show()

        if reason == self.Context:
            self.generateMenu()

    # --------------------------------------------------------------------------
    def closeRequest(self):
        """
        Triggered on close. This can be overriden if you want to override this
        behaviour

        :return:
        """
        sys.exit()

    # --------------------------------------------------------------------------
    def addProcessCall(self, callable_item):
        """
        Adds a callable item to the processor

        :param callable_item: callable item. Highly recommended that this is
            a functools.partial object
        :type callable_item: callable

        :return: None
        """
        self._process_calls.append(callable_item)

    # --------------------------------------------------------------------------
    def removeProcessCall(self, callable_item):
        """
        Removes the callable item from the list of callable processes

        :param callable_item: callable item. Highly recommended that this is
            a functools.partial object
        :type callable_item: callable

        :return: None
        """
        if callable_item in self._process_calls:
            self._process_calls.remove(callable_item)

    # --------------------------------------------------------------------------
    def addMenuItem(self, label, icon, action):
        """
        Adds a menu item to the menu which gets displayed when the user
        right clicks the tray.

        :param label: Label to display the item with
        :type label: str

        :param icon: Path to icon to be used
        :type icon: str

        :param action: function callable which should be called when the
            user clicks
        :type action: callable

        :return: None
        """
        self._user_menu_actions.append(
            dict(
                label=label,
                icon=icon,
                action=action,
            ),
        )

    # --------------------------------------------------------------------------
    def removeMenuItem(self, label):
        """
        Adds a menu item to the menu which gets displayed when the user
        right clicks the tray.

        :param label: Label of the item to remove
        :type label: str

        :return: None
        """
        for menu_data in self._user_menu_actions:
            if label == menu_data['label']:
                self._user_menu_actions.remove(menu_data)
                break

    # --------------------------------------------------------------------------
    def beginProcessing(self):
        """
        This will trigger a processing run  providing there is not an
        active processing run already in progress.
        """
        if not self._process_thread:

            if self.verbose:
                self.showMessage(
                    "Processing Tray",
                    "About to process %s task(s)" % len(self._process_calls)
                )

            # -- Create the new scan thread
            self._process_thread = ProcessorThread(self._process_calls, self)

            # -- Ensure it clears itself once its finished, and
            # -- initiate its start.
            self._process_thread.finished.connect(self.onEndOfProcessing)
            self._process_thread.start()

    # --------------------------------------------------------------------------
    def onEndOfProcessing(self):
        """
        This is called whenever a scan is complete. This performs any
        object clean up.
        """
        self._process_thread = None

    # --------------------------------------------------------------------------
    def toggleVerbosity(self):
        self.verbose = not self.verbose

    # --------------------------------------------------------------------------
    def generateMenu(self, styles=None):
        """
        This will update the contents of the menu to be reflective of the
        users current settings.
        """
        # -- Clear the current menu
        self._menu.clear()

        # -- Add an item which is here to show the identifier as well
        # -- as the scan status
        action = Qt.QtWidgets.QAction(
            'Processing' if self._process_thread else 'Idle',
            self._menu,
        )
        self._menu.addAction(action)

        # -- Add our seperator
        self._menu.addSeparator()

        # -- Add actions to enable/disable auto scan
        tag = 'Disable' if self._process_on_timer else 'Enable'

        action = Qt.QtWidgets.QAction(
            '%s Auto Scan' % tag,
            self._menu,
        )

        # -- Connect the signal event
        action.triggered.connect(
            functools.partial(
                self.set_auto_process,
                not self._process_on_timer
            )
        )

        # -- Add the action
        self._menu.addAction(action)

        # -- Add the time between scan item
        action = Qt.QtWidgets.QAction(
            'Set Interval (%s)' % self._process_interval,
            self._menu
        )

        action.triggered.connect(
            functools.partial(
                self.set_time_between_scan,
            )
        )

        # -- Add the item
        self._menu.addAction(action)

        # -- Add our seperator
        self._menu.addSeparator()

        action = Qt.QtWidgets.QAction(
            'Trigger Processing',
            self._menu,
        )
        action.triggered.connect(self.beginProcessing)
        self._menu.addAction(action)

        if self.verbose:
            action = Qt.QtWidgets.QAction(
                'Disable verbose notifications',
                self._menu,
            )
        else:
            action = Qt.QtWidgets.QAction(
                'Enable verbose notifications',
                self._menu,
            )

        action.triggered.connect(self.toggleVerbosity)
        self._menu.addAction(action)

        # -- Add our seperator
        self._menu.addSeparator()

        # -- Add any user assigned items
        for menu_data in self._user_menu_actions:
            action = Qt.QtWidgets.QAction(menu_data['label'], self._menu)

            if menu_data['icon']:
                action.setIcon(Qt.QtGui.QIcon(menu_data['icon']))

            action.triggered.connect(menu_data['action'])
            self._menu.addAction(action)

        # -- Add our seperator
        self._menu.addSeparator()

        # -- Add our exit option
        action = Qt.QtWidgets.QAction('Exit', self._menu)
        action.triggered.connect(self.closeRequest)
        self._menu.addAction(action)

        if styles:
            utilities.styling.apply(
                styles=['space'],
                apply_to=self._menu,
            )

        # -- Regenerate the menu
        self.setContextMenu(self._menu)

    # --------------------------------------------------------------------------
    def set_auto_process(self, value):
        """
        This will change the auto scan setting.

        :param value: The value to switch to
        """
        self._process_on_timer = value

        if self._process_on_timer:
            self._timer.start()

        else:
            self._timer.stop()

    # --------------------------------------------------------------------------
    def set_time_between_scan(self, value=None):
        """
        This allows the user to tailor how long to run between
        scans
        """
        if value is None:
            value, ok = Qt.QtWidgets.QInputDialog.getInt(
                None,
                'Time (in minutes) between scans',
                'This is minimum time between scans',
                self._process_interval,
                minValue=1,
                maxValue=10000,
                step=1,
            )

            if not ok:
                return value

        # -- Update our interval variable and apply it to the
        # -- timer
        self._process_interval = value
        self._timer.stop()
        self._timer.setInterval(self._process_interval * 1000)

        if self._process_on_timer:
            self._timer.start()

        return value


# ------------------------------------------------------------------------------
class MemorableTimedProcessorTray(TimedProcessorTray):
    """
    This is a re-implementation of the timed processor tray which has
    the extended functionality of serialising its user settings
    """

    # --------------------------------------------------------------------------
    def __init__(self, identifier, icon, auto_process=False, interval=5):
        super(MemorableTimedProcessorTray, self).__init__(
            icon=icon,
            auto_process=auto_process,
            interval=interval,
        )

        # -- Store the identifier
        self._identifier = identifier

        # -- Check for stored settings
        settings = scribble.get(self._identifier)

        # -- Apply the settings, using our fall-backs
        self.set_time_between_scan(settings.get('time_between_scan', interval))
        self.set_auto_process(settings.get('auto_process', auto_process))

    # --------------------------------------------------------------------------
    def set_auto_process(self, value):
        super(MemorableTimedProcessorTray, self).set_auto_process(value)

        settings = scribble.get(self._identifier)
        settings['auto_process'] = value
        settings.save()

    # --------------------------------------------------------------------------
    def set_time_between_scan(self, value=None):
        value = super(MemorableTimedProcessorTray, self).set_time_between_scan(value)

        if value is not None:
            settings = scribble.get(self._identifier)
            settings['time_between_scan'] = value
            settings.save()


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class ProcessorThread(Qt.QtCore.QThread):
    """
    All our scanning is handled in a thread to prevent the rest
    of the ui elements from being blocked.
    """

    # --------------------------------------------------------------------------
    def __init__(self, process_calls, tray):
        super(ProcessorThread, self).__init__()
        self._process_calls = process_calls
        self._tray = tray

    # --------------------------------------------------------------------------
    def run(self):
        for callable_process in self._process_calls:
            try:
                callable_process()

            except (Exception, RuntimeError):
                error = str(sys.exc_info())
                print(error)

                if self._tray.verbose:
                    self._tray.showMessage(
                        "Processing Tray",
                        error,
                    )
