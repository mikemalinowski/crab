import pymel.core as pm


# --------------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class UndoChunk(object):

    # ----------------------------------------------------------------------------------
    def __init__(self):
        self._closed = False

    # ----------------------------------------------------------------------------------
    def __enter__(self):
        pm.undoInfo(openChunk=True)
        return self

    # ----------------------------------------------------------------------------------
    def __exit__(self, *exc_info):
        if not self._closed:
            pm.undoInfo(closeChunk=True)

    # ----------------------------------------------------------------------------------
    def restore(self):
        pm.undoInfo(closeChunk=True)
        self._closed = True

        try:
            pm.undo()

        except StandardError:
            pass


# --------------------------------------------------------------------------------------
class RestoredTime(object):

    # ----------------------------------------------------------------------------------
    def __init__(self):
        # -- Cast to iterable
        self._time = pm.currentTime()

    # ----------------------------------------------------------------------------------
    def __enter__(self):
        pass

    # ----------------------------------------------------------------------------------
    def __exit__(self, *exc_info):
        pm.setCurrentTime(self._time)


# --------------------------------------------------------------------------------------
class RestoredSelection(object):
    """
    Cache selection on entering and re-select on exit
    """

    # ----------------------------------------------------------------------------------
    def __enter__(self):
        self._selection = pm.selected()

    # ----------------------------------------------------------------------------------
    def __exit__(self, *exc_info):
        if self._selection:
            pm.select(self._selection)
