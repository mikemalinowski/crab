from ..vendor import Qt


# --------------------------------------------------------------------------------------------------
def expandWidth(size_to_update, size_to_consider):
    return Qt.QSize(
        max(size_to_update.width(), size_to_consider.width()),
        size_to_update.height(),
    )


# --------------------------------------------------------------------------------------------------
def expandHeight(size_to_update, size_to_consider):
    return Qt.QSize(
        size_to_update.width(),
        max(size_to_update.height(), size_to_consider.height()),
    )


# --------------------------------------------------------------------------------------------------
def addWidth(size_to_update, size_to_consider):
    return Qt.QSize(
        size_to_update.width() + size_to_consider.width(),
        size_to_update.height(),
    )


# --------------------------------------------------------------------------------------------------
def addHeight(size_to_update, size_to_consider):
    return Qt.QSize(
        size_to_update.width(),
        size_to_update.height() + size_to_consider.height(),
    )
