from .. import utilities
from .. import extensions
from .. import applyStyle


# ------------------------------------------------------------------------------
def quick_app(window_title, style=None):
    """
    Decorator to use on a function that is expected to return a widget that
    will be set as the Main Widget in the window that is created.

    :param window_title: App and window title.
    :type window_title: str
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            q_app = utilities.qApp()

            widget = func(*args, **kwargs)

            window = extensions.windows.MemorableWindow(
                identifier=window_title,
                parent=utilities.windows.mainWindow(),
            )

            window.setCentralWidget(widget)

            # -- Set the window properties
            window.setWindowTitle(window_title)

            if style:
                applyStyle(
                    style,
                    apply_to=window
                )

            # -- Show the ui, and if we're blocking call the exec_
            window.show()

            q_app.exec_()

            return window

        return wrapper

    return decorator
