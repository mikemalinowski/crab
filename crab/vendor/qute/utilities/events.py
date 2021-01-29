from ..vendor import Qt


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def printEventName(event):
    """
    Prints the name of the event type being given.

    :param event: The event to print the type of
    :type event: QEvent

    :return: None
    """
    if hasattr(Qt.QEvent, 'AccessibilityDescription'):
        if event.type() == Qt.QEvent.AccessibilityDescription:
            print('AccessibilityDescription')
    if hasattr(Qt.QEvent, 'AccessibilityHelp'):
        if event.type() == Qt.QEvent.AccessibilityHelp:
            print('AccessibilityHelp')
    if hasattr(Qt.QEvent, 'AccessibilityPrepare'):
        if event.type() == Qt.QEvent.AccessibilityPrepare:
            print('AccessibilityPrepare')
    if hasattr(Qt.QEvent, 'ActionAdded'):
        if event.type() == Qt.QEvent.ActionAdded:
            print('ActionAdded')
    if hasattr(Qt.QEvent, 'ActionChanged'):
        if event.type() == Qt.QEvent.ActionChanged:
            print('ActionChanged')
    if hasattr(Qt.QEvent, 'ActionRemoved'):
        if event.type() == Qt.QEvent.ActionRemoved:
            print('ActionRemoved')
    if hasattr(Qt.QEvent, 'ActivationChange'):
        if event.type() == Qt.QEvent.ActivationChange:
            print('ActivationChange')
    if hasattr(Qt.QEvent, 'ApplicationActivate'):
        if event.type() == Qt.QEvent.ApplicationActivate:
            print('ApplicationActivate')
    if hasattr(Qt.QEvent, 'ApplicationActivated'):
        if event.type() == Qt.QEvent.ApplicationActivated:
            print('ApplicationActivated')
    if hasattr(Qt.QEvent, 'ApplicationDeactivate'):
        if event.type() == Qt.QEvent.ApplicationDeactivate:
            print('ApplicationDeactivate')
    if hasattr(Qt.QEvent, 'ApplicationFontChange'):
        if event.type() == Qt.QEvent.ApplicationFontChange:
            print('ApplicationFontChange')
    if hasattr(Qt.QEvent, 'ApplicationLayoutDirectionChange'):
        if event.type() == Qt.QEvent.ApplicationLayoutDirectionChange:
            print('ApplicationLayoutDirectionChange')
    if hasattr(Qt.QEvent, 'ApplicationPaletteChange'):
        if event.type() == Qt.QEvent.ApplicationPaletteChange:
            print('ApplicationPaletteChange')
    if hasattr(Qt.QEvent, 'ApplicationWindowIconChange'):
        if event.type() == Qt.QEvent.ApplicationWindowIconChange:
            print('ApplicationWindowIconChange')
    if hasattr(Qt.QEvent, 'ChildAdded'):
        if event.type() == Qt.QEvent.ChildAdded:
            print('ChildAdded')
    if hasattr(Qt.QEvent, 'ChildInserted'):
        if event.type() == Qt.QEvent.ChildInserted:
            print('ChildInserted')
    if hasattr(Qt.QEvent, 'ChildPolished'):
        if event.type() == Qt.QEvent.ChildPolished:
            print('ChildPolished')
    if hasattr(Qt.QEvent, 'ChildRemoved'):
        if event.type() == Qt.QEvent.ChildRemoved:
            print('ChildRemoved')
    if hasattr(Qt.QEvent, 'Clipboard'):
        if event.type() == Qt.QEvent.Clipboard:
            print('Clipboard')
    if hasattr(Qt.QEvent, 'Close'):
        if event.type() == Qt.QEvent.Close:
            print('Close')
    if hasattr(Qt.QEvent, 'CloseSoftwareInputPanel'):
        if event.type() == Qt.QEvent.CloseSoftwareInputPanel:
            print('CloseSoftwareInputPanel')
    if hasattr(Qt.QEvent, 'ContentsRectChange'):
        if event.type() == Qt.QEvent.ContentsRectChange:
            print('ContentsRectChange')
    if hasattr(Qt.QEvent, 'ContextMenu'):
        if event.type() == Qt.QEvent.ContextMenu:
            print('ContextMenu')
    if hasattr(Qt.QEvent, 'CursorChange'):
        if event.type() == Qt.QEvent.CursorChange:
            print('CursorChange')
    if hasattr(Qt.QEvent, 'DeferredDelete'):
        if event.type() == Qt.QEvent.DeferredDelete:
            print('DeferredDelete')
    if hasattr(Qt.QEvent, 'DragEnter'):
        if event.type() == Qt.QEvent.DragEnter:
            print('DragEnter')
    if hasattr(Qt.QEvent, 'DragLeave'):
        if event.type() == Qt.QEvent.DragLeave:
            print('DragLeave')
    if hasattr(Qt.QEvent, 'DragMove'):
        if event.type() == Qt.QEvent.DragMove:
            print('DragMove')
    if hasattr(Qt.QEvent, 'Drop'):
        if event.type() == Qt.QEvent.Drop:
            print('Drop')
    if hasattr(Qt.QEvent, 'EnabledChange'):
        if event.type() == Qt.QEvent.EnabledChange:
            print('EnabledChange')
    if hasattr(Qt.QEvent, 'Enter'):
        if event.type() == Qt.QEvent.Enter:
            print('Enter')
    if hasattr(Qt.QEvent, 'EnterEditFocus'):
        if event.type() == Qt.QEvent.EnterEditFocus:
            print('EnterEditFocus')
    if hasattr(Qt.QEvent, 'EnterWhatsThisMode'):
        if event.type() == Qt.QEvent.EnterWhatsThisMode:
            print('EnterWhatsThisMode')
    if hasattr(Qt.QEvent, 'FileOpen'):
        if event.type() == Qt.QEvent.FileOpen:
            print('FileOpen')
    if hasattr(Qt.QEvent, 'FocusIn'):
        if event.type() == Qt.QEvent.FocusIn:
            print('FocusIn')
    if hasattr(Qt.QEvent, 'FocusOut'):
        if event.type() == Qt.QEvent.FocusOut:
            print('FocusOut')
    if hasattr(Qt.QEvent, 'FontChange'):
        if event.type() == Qt.QEvent.FontChange:
            print('FontChange')
    if hasattr(Qt.QEvent, 'GrabKeyboard'):
        if event.type() == Qt.QEvent.GrabKeyboard:
            print('GrabKeyboard')
    if hasattr(Qt.QEvent, 'GrabMouse'):
        if event.type() == Qt.QEvent.GrabMouse:
            print('GrabMouse')
    if hasattr(Qt.QEvent, 'GraphicsSceneContextMenu'):
        if event.type() == Qt.QEvent.GraphicsSceneContextMenu:
            print('GraphicsSceneContextMenu')
    if hasattr(Qt.QEvent, 'GraphicsSceneDragEnter'):
        if event.type() == Qt.QEvent.GraphicsSceneDragEnter:
            print('GraphicsSceneDragEnter')
    if hasattr(Qt.QEvent, 'GraphicsSceneDragLeave'):
        if event.type() == Qt.QEvent.GraphicsSceneDragLeave:
            print('GraphicsSceneDragLeave')
    if hasattr(Qt.QEvent, 'GraphicsSceneDragMove'):
        if event.type() == Qt.QEvent.GraphicsSceneDragMove:
            print('GraphicsSceneDragMove')
    if hasattr(Qt.QEvent, 'GraphicsSceneDrop'):
        if event.type() == Qt.QEvent.GraphicsSceneDrop:
            print('GraphicsSceneDrop')
    if hasattr(Qt.QEvent, 'GraphicsSceneHelp'):
        if event.type() == Qt.QEvent.GraphicsSceneHelp:
            print('GraphicsSceneHelp')
    if hasattr(Qt.QEvent, 'GraphicsSceneHoverEnter'):
        if event.type() == Qt.QEvent.GraphicsSceneHoverEnter:
            print('GraphicsSceneHoverEnter')
    if hasattr(Qt.QEvent, 'GraphicsSceneHoverLeave'):
        if event.type() == Qt.QEvent.GraphicsSceneHoverLeave:
            print('GraphicsSceneHoverLeave')
    if hasattr(Qt.QEvent, 'GraphicsSceneHoverMove'):
        if event.type() == Qt.QEvent.GraphicsSceneHoverMove:
            print('GraphicsSceneHoverMove')
    if hasattr(Qt.QEvent, 'GraphicsSceneMouseDoubleClick'):
        if event.type() == Qt.QEvent.GraphicsSceneMouseDoubleClick:
            print('GraphicsSceneMouseDoubleClick')
    if hasattr(Qt.QEvent, 'GraphicsSceneMouseMove'):
        if event.type() == Qt.QEvent.GraphicsSceneMouseMove:
            print('GraphicsSceneMouseMove')
    if hasattr(Qt.QEvent, 'GraphicsSceneMousePress'):
        if event.type() == Qt.QEvent.GraphicsSceneMousePress:
            print('GraphicsSceneMousePress')
    if hasattr(Qt.QEvent, 'GraphicsSceneMouseRelease'):
        if event.type() == Qt.QEvent.GraphicsSceneMouseRelease:
            print('GraphicsSceneMouseRelease')
    if hasattr(Qt.QEvent, 'GraphicsSceneMove'):
        if event.type() == Qt.QEvent.GraphicsSceneMove:
            print('GraphicsSceneMove')
    if hasattr(Qt.QEvent, 'GraphicsSceneResize'):
        if event.type() == Qt.QEvent.GraphicsSceneResize:
            print('GraphicsSceneResize')
    if hasattr(Qt.QEvent, 'GraphicsSceneWheel'):
        if event.type() == Qt.QEvent.GraphicsSceneWheel:
            print('GraphicsSceneWheel')
    if hasattr(Qt.QEvent, 'Hide'):
        if event.type() == Qt.QEvent.Hide:
            print('Hide')
    if hasattr(Qt.QEvent, 'HideToParent'):
        if event.type() == Qt.QEvent.HideToParent:
            print('HideToParent')
    if hasattr(Qt.QEvent, 'HoverEnter'):
        if event.type() == Qt.QEvent.HoverEnter:
            print('HoverEnter')
    if hasattr(Qt.QEvent, 'HoverLeave'):
        if event.type() == Qt.QEvent.HoverLeave:
            print('HoverLeave')
    if hasattr(Qt.QEvent, 'HoverMove'):
        if event.type() == Qt.QEvent.HoverMove:
            print('HoverMove')
    if hasattr(Qt.QEvent, 'IconDrag'):
        if event.type() == Qt.QEvent.IconDrag:
            print('IconDrag')
    if hasattr(Qt.QEvent, 'IconTextChange'):
        if event.type() == Qt.QEvent.IconTextChange:
            print('IconTextChange')
    if hasattr(Qt.QEvent, 'InputMethod'):
        if event.type() == Qt.QEvent.InputMethod:
            print('InputMethod')
    if hasattr(Qt.QEvent, 'KeyPress'):
        if event.type() == Qt.QEvent.KeyPress:
            print('KeyPress')
    if hasattr(Qt.QEvent, 'KeyRelease'):
        if event.type() == Qt.QEvent.KeyRelease:
            print('KeyRelease')
    if hasattr(Qt.QEvent, 'LanguageChange'):
        if event.type() == Qt.QEvent.LanguageChange:
            print('LanguageChange')
    if hasattr(Qt.QEvent, 'LayoutDirectionChange'):
        if event.type() == Qt.QEvent.LayoutDirectionChange:
            print('LayoutDirectionChange')
    if hasattr(Qt.QEvent, 'LayoutRequest'):
        if event.type() == Qt.QEvent.LayoutRequest:
            print('LayoutRequest')
    if hasattr(Qt.QEvent, 'Leave'):
        if event.type() == Qt.QEvent.Leave:
            print('Leave')
    if hasattr(Qt.QEvent, 'LeaveEditFocus'):
        if event.type() == Qt.QEvent.LeaveEditFocus:
            print('LeaveEditFocus')
    if hasattr(Qt.QEvent, 'LeaveWhatsThisMode'):
        if event.type() == Qt.QEvent.LeaveWhatsThisMode:
            print('LeaveWhatsThisMode')
    if hasattr(Qt.QEvent, 'LocaleChange'):
        if event.type() == Qt.QEvent.LocaleChange:
            print('LocaleChange')
    if hasattr(Qt.QEvent, 'NonClientAreaMouseButtonDblClick'):
        if event.type() == Qt.QEvent.NonClientAreaMouseButtonDblClick:
            print('NonClientAreaMouseButtonDblClick')
    if hasattr(Qt.QEvent, 'NonClientAreaMouseButtonPress'):
        if event.type() == Qt.QEvent.NonClientAreaMouseButtonPress:
            print('NonClientAreaMouseButtonPress')
    if hasattr(Qt.QEvent, 'NonClientAreaMouseButtonRelease'):
        if event.type() == Qt.QEvent.NonClientAreaMouseButtonRelease:
            print('NonClientAreaMouseButtonRelease')
    if hasattr(Qt.QEvent, 'NonClientAreaMouseMove'):
        if event.type() == Qt.QEvent.NonClientAreaMouseMove:
            print('NonClientAreaMouseMove')
    if hasattr(Qt.QEvent, 'MacSizeChange'):
        if event.type() == Qt.QEvent.MacSizeChange:
            print('MacSizeChange')
    if hasattr(Qt.QEvent, 'MenubarUpdated'):
        if event.type() == Qt.QEvent.MenubarUpdated:
            print('MenubarUpdated')
    if hasattr(Qt.QEvent, 'MetaCall'):
        if event.type() == Qt.QEvent.MetaCall:
            print('MetaCall')
    if hasattr(Qt.QEvent, 'ModifiedChange'):
        if event.type() == Qt.QEvent.ModifiedChange:
            print('ModifiedChange')
    if hasattr(Qt.QEvent, 'MouseButtonDblClick'):
        if event.type() == Qt.QEvent.MouseButtonDblClick:
            print('MouseButtonDblClick')
    if hasattr(Qt.QEvent, 'MouseButtonPress'):
        if event.type() == Qt.QEvent.MouseButtonPress:
            print('MouseButtonPress')
    if hasattr(Qt.QEvent, 'MouseButtonRelease'):
        if event.type() == Qt.QEvent.MouseButtonRelease:
            print('MouseButtonRelease')
    if hasattr(Qt.QEvent, 'MouseMove'):
        if event.type() == Qt.QEvent.MouseMove:
            print('MouseMove')
    if hasattr(Qt.QEvent, 'MouseTrackingChange'):
        if event.type() == Qt.QEvent.MouseTrackingChange:
            print('MouseTrackingChange')
    if hasattr(Qt.QEvent, 'Move'):
        if event.type() == Qt.QEvent.Move:
            print('Move')
    if hasattr(Qt.QEvent, 'Paint'):
        if event.type() == Qt.QEvent.Paint:
            print('Paint')
    if hasattr(Qt.QEvent, 'PaletteChange'):
        if event.type() == Qt.QEvent.PaletteChange:
            print('PaletteChange')
    if hasattr(Qt.QEvent, 'ParentAboutToChange'):
        if event.type() == Qt.QEvent.ParentAboutToChange:
            print('ParentAboutToChange')
    if hasattr(Qt.QEvent, 'ParentChange'):
        if event.type() == Qt.QEvent.ParentChange:
            print('ParentChange')
    if hasattr(Qt.QEvent, 'Polish'):
        if event.type() == Qt.QEvent.Polish:
            print('Polish')
    if hasattr(Qt.QEvent, 'PolishRequest'):
        if event.type() == Qt.QEvent.PolishRequest:
            print('PolishRequest')
    if hasattr(Qt.QEvent, 'QueryWhatsThis'):
        if event.type() == Qt.QEvent.QueryWhatsThis:
            print('QueryWhatsThis')
    if hasattr(Qt.QEvent, 'RequestSoftwareInputPanel'):
        if event.type() == Qt.QEvent.RequestSoftwareInputPanel:
            print('RequestSoftwareInputPanel')
    if hasattr(Qt.QEvent, 'Resize'):
        if event.type() == Qt.QEvent.Resize:
            print('Resize')
    if hasattr(Qt.QEvent, 'Shortcut'):
        if event.type() == Qt.QEvent.Shortcut:
            print('Shortcut')
    if hasattr(Qt.QEvent, 'ShortcutOverride'):
        if event.type() == Qt.QEvent.ShortcutOverride:
            print('ShortcutOverride')
    if hasattr(Qt.QEvent, 'Show'):
        if event.type() == Qt.QEvent.Show:
            print('Show')
    if hasattr(Qt.QEvent, 'ShowToParent'):
        if event.type() == Qt.QEvent.ShowToParent:
            print('ShowToParent')
    if hasattr(Qt.QEvent, 'SockAct'):
        if event.type() == Qt.QEvent.SockAct:
            print('SockAct')
    if hasattr(Qt.QEvent, 'StateMachineSignal'):
        if event.type() == Qt.QEvent.StateMachineSignal:
            print('StateMachineSignal')
    if hasattr(Qt.QEvent, 'StateMachineWrapped'):
        if event.type() == Qt.QEvent.StateMachineWrapped:
            print('StateMachineWrapped')
    if hasattr(Qt.QEvent, 'StatusTip'):
        if event.type() == Qt.QEvent.StatusTip:
            print('StatusTip')
    if hasattr(Qt.QEvent, 'StyleChange'):
        if event.type() == Qt.QEvent.StyleChange:
            print('StyleChange')
    if hasattr(Qt.QEvent, 'TabletMove'):
        if event.type() == Qt.QEvent.TabletMove:
            print('TabletMove')
    if hasattr(Qt.QEvent, 'TabletPress'):
        if event.type() == Qt.QEvent.TabletPress:
            print('TabletPress')
    if hasattr(Qt.QEvent, 'TabletRelease'):
        if event.type() == Qt.QEvent.TabletRelease:
            print('TabletRelease')
    if hasattr(Qt.QEvent, 'OkRequest'):
        if event.type() == Qt.QEvent.OkRequest:
            print('OkRequest')
    if hasattr(Qt.QEvent, 'TabletEnterProximity'):
        if event.type() == Qt.QEvent.TabletEnterProximity:
            print('TabletEnterProximity')
    if hasattr(Qt.QEvent, 'TabletLeaveProximity'):
        if event.type() == Qt.QEvent.TabletLeaveProximity:
            print('TabletLeaveProximity')
    if hasattr(Qt.QEvent, 'Timer'):
        if event.type() == Qt.QEvent.Timer:
            print('Timer')
    if hasattr(Qt.QEvent, 'ToolBarChange'):
        if event.type() == Qt.QEvent.ToolBarChange:
            print('ToolBarChange')
    if hasattr(Qt.QEvent, 'ToolTip'):
        if event.type() == Qt.QEvent.ToolTip:
            print('ToolTip')
    if hasattr(Qt.QEvent, 'ToolTipChange'):
        if event.type() == Qt.QEvent.ToolTipChange:
            print('ToolTipChange')
    if hasattr(Qt.QEvent, 'UngrabKeyboard'):
        if event.type() == Qt.QEvent.UngrabKeyboard:
            print('UngrabKeyboard')
    if hasattr(Qt.QEvent, 'UngrabMouse'):
        if event.type() == Qt.QEvent.UngrabMouse:
            print('UngrabMouse')
    if hasattr(Qt.QEvent, 'UpdateLater'):
        if event.type() == Qt.QEvent.UpdateLater:
            print('UpdateLater')
    if hasattr(Qt.QEvent, 'UpdateRequest'):
        if event.type() == Qt.QEvent.UpdateRequest:
            print('UpdateRequest')
    if hasattr(Qt.QEvent, 'WhatsThis'):
        if event.type() == Qt.QEvent.WhatsThis:
            print('WhatsThis')
    if hasattr(Qt.QEvent, 'WhatsThisClicked'):
        if event.type() == Qt.QEvent.WhatsThisClicked:
            print('WhatsThisClicked')
    if hasattr(Qt.QEvent, 'Wheel'):
        if event.type() == Qt.QEvent.Wheel:
            print('Wheel')
    if hasattr(Qt.QEvent, 'WinEventAct'):
        if event.type() == Qt.QEvent.WinEventAct:
            print('WinEventAct')
    if hasattr(Qt.QEvent, 'WindowActivate'):
        if event.type() == Qt.QEvent.WindowActivate:
            print('WindowActivate')
    if hasattr(Qt.QEvent, 'WindowBlocked'):
        if event.type() == Qt.QEvent.WindowBlocked:
            print('WindowBlocked')
    if hasattr(Qt.QEvent, 'WindowDeactivate'):
        if event.type() == Qt.QEvent.WindowDeactivate:
            print('WindowDeactivate')
    if hasattr(Qt.QEvent, 'WindowIconChange'):
        if event.type() == Qt.QEvent.WindowIconChange:
            print('WindowIconChange')
    if hasattr(Qt.QEvent, 'WindowStateChange'):
        if event.type() == Qt.QEvent.WindowStateChange:
            print('WindowStateChange')
    if hasattr(Qt.QEvent, 'WindowTitleChange'):
        if event.type() == Qt.QEvent.WindowTitleChange:
            print('WindowTitleChange')
    if hasattr(Qt.QEvent, 'WindowUnblocked'):
        if event.type() == Qt.QEvent.WindowUnblocked:
            print('WindowUnblocked')
    if hasattr(Qt.QEvent, 'ZOrderChange'):
        if event.type() == Qt.QEvent.ZOrderChange:
            print('ZOrderChange')
    if hasattr(Qt.QEvent, 'KeyboardLayoutChange'):
        if event.type() == Qt.QEvent.KeyboardLayoutChange:
            print('KeyboardLayoutChange')
    if hasattr(Qt.QEvent, 'DynamicPropertyChange'):
        if event.type() == Qt.QEvent.DynamicPropertyChange:
            print('DynamicPropertyChange')
    if hasattr(Qt.QEvent, 'TouchBegin'):
        if event.type() == Qt.QEvent.TouchBegin:
            print('TouchBegin')
    if hasattr(Qt.QEvent, 'TouchUpdate'):
        if event.type() == Qt.QEvent.TouchUpdate:
            print('TouchUpdate')
    if hasattr(Qt.QEvent, 'TouchEnd'):
        if event.type() == Qt.QEvent.TouchEnd:
            print('TouchEnd')
    if hasattr(Qt.QEvent, 'WinIdChange'):
        if event.type() == Qt.QEvent.WinIdChange:
            print('WinIdChange')
    if hasattr(Qt.QEvent, 'Gesture'):
        if event.type() == Qt.QEvent.Gesture:
            print('Gesture')
    if hasattr(Qt.QEvent, 'GestureOverride'):
        if event.type() == Qt.QEvent.GestureOverride:
            print('GestureOverride')
