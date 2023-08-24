import sys

from PyQt5 import QtCore

import platform
import qtpy
from PyQt5.QtGui import QPalette, QColor
from qtpy.QtCore import Slot
from os.path import join, dirname, abspath
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QLabel, QToolButton
from PyQt5.QtCore import Qt, QMetaObject

from qtmodern.windows import WindowDragger


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return join(sys._MEIPASS, dirname(abspath(__file__)), relative_path)
    return join(dirname(abspath(__file__)), relative_path)


_FL_STYLESHEET = resource_path('resources/frameless.qss')
_STYLESHEET = resource_path('resources/style.qss')
PLATFORM = platform.system()
QT_VERSION = tuple(int(v) for v in qtpy.QT_VERSION.split('.'))


def _apply_base_theme(app):
    app.setStyle('Fusion')
    with open(_STYLESHEET) as stylesheet:
        app.setStyleSheet(stylesheet.read())


class ModernWindow(QWidget):
    global gallery

    def __init__(self, w, parent=None):
        QWidget.__init__(self, parent)

        self.vboxWindow = QVBoxLayout(self)
        self.windowFrame = QWidget(self)
        self.vboxFrame = QVBoxLayout(self.windowFrame)
        self.titleBar = WindowDragger(self, self.windowFrame)
        self.lblTitle = QLabel('Title')

        self.hboxTitle = QHBoxLayout(self.titleBar)
        self.btnMinimize = QToolButton(self.titleBar)
        self.btnRestore = QToolButton(self.titleBar)
        self.windowContent = QWidget(self.windowFrame)
        self._w = w
        self.setupUi()

        contentLayout = QHBoxLayout()
        contentLayout.setContentsMargins(0, 0, 0, 0)
        contentLayout.addWidget(w)

        self.windowContent.setLayout(contentLayout)
        self.setWindowTitle(w.windowTitle())
        self.setGeometry(w.geometry())

        # Adding attribute to clean up the parent window when the child is closed
        self._w.setAttribute(Qt.WA_DeleteOnClose, True)
        self._w.destroyed.connect(self.__child_was_closed)

    def setupUi(self):
        # create title bar, content
        self.vboxWindow.setContentsMargins(0, 0, 0, 0)
        self.windowFrame.setObjectName('windowFrame')
        self.vboxFrame.setContentsMargins(0, 0, 0, 0)
        self.titleBar.setObjectName('titleBar')
        self.titleBar.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.hboxTitle.setContentsMargins(10, 5, 5, 0)
        self.hboxTitle.setSpacing(0)
        self.lblTitle.setObjectName('lblTitle')
        self.lblTitle.setAlignment(Qt.AlignLeft)
        spButtons = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnMinimize.setObjectName('btnMinimize')
        self.btnMinimize.setSizePolicy(spButtons)

        self.btnRestore.setObjectName('btnRestore')
        self.btnRestore.setSizePolicy(spButtons)

        self.btnMaximize = QToolButton(self.titleBar)
        self.btnMaximize.setObjectName('btnMaximize')
        self.btnMaximize.setSizePolicy(spButtons)

        self.btnClose = QToolButton(self.titleBar)
        self.btnClose.setObjectName('btnClose')
        self.btnClose.setSizePolicy(spButtons)

        self.vboxFrame.addWidget(self.titleBar)

        self.vboxFrame.addWidget(self.windowContent)

        self.vboxWindow.addWidget(self.windowFrame)
        self.hboxTitle.addWidget(self.lblTitle)
        self.hboxTitle.addWidget(self.btnMinimize)
        self.hboxTitle.addWidget(self.btnRestore)
        self.hboxTitle.addWidget(self.btnMaximize)
        self.hboxTitle.addWidget(self.btnClose)

        # set window flags
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint |
                            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self.setAttribute(Qt.WA_TranslucentBackground)

        with open(_FL_STYLESHEET) as stylesheet:
            self.setStyleSheet(stylesheet.read())
        QMetaObject.connectSlotsByName(self)

    def __child_was_closed(self):
        self._w = None
        self.close()

    def closeEvent(self, event):
        if not self._w:
            event.accept()
        else:
            self._w.close()
            event.setAccepted(self._w.isHidden())

    def setWindowTitle(self, title):
        super(ModernWindow, self).setWindowTitle(title)
        self.lblTitle.setText(title)

    def _setWindowButtonState(self, hint, state):
        btns = {
            Qt.WindowCloseButtonHint: self.btnClose,
            Qt.WindowMinimizeButtonHint: self.btnMinimize,
            Qt.WindowMaximizeButtonHint: self.btnMaximize
        }
        button = btns.get(hint)

        maximized = bool(self.windowState() & Qt.WindowMaximized)

        if button == self.btnMaximize:  # special rules for max/restore
            self.btnRestore.setEnabled(state)
            self.btnMaximize.setEnabled(state)

            if maximized:
                self.btnRestore.setVisible(state)
                self.btnMaximize.setVisible(False)
            else:
                self.btnMaximize.setVisible(state)
                self.btnRestore.setVisible(False)
        else:
            button.setEnabled(state)

        allButtons = [self.btnClose, self.btnMinimize, self.btnMaximize, self.btnRestore]
        if True in [b.isEnabled() for b in allButtons]:
            for b in allButtons:
                b.setVisible(True)
            if maximized:
                self.btnMaximize.setVisible(False)
            else:
                self.btnRestore.setVisible(False)
            self.lblTitle.setContentsMargins(0, 0, 0, 0)
        else:
            for b in allButtons:
                b.setVisible(False)
            self.lblTitle.setContentsMargins(0, 0, 0, 0)

    def setWindowFlag(self, Qt_WindowType, on=True):
        buttonHints = [Qt.WindowCloseButtonHint, Qt.WindowMinimizeButtonHint, Qt.WindowMaximizeButtonHint]

        if Qt_WindowType in buttonHints:
            self._setWindowButtonState(Qt_WindowType, on)
        else:
            QWidget.setWindowFlag(self, Qt_WindowType, on)

    def setWindowFlags(self, Qt_WindowFlags):
        buttonHints = [Qt.WindowCloseButtonHint, Qt.WindowMinimizeButtonHint, Qt.WindowMaximizeButtonHint]
        for hint in buttonHints:
            self._setWindowButtonState(hint, bool(Qt_WindowFlags & hint))

        QWidget.setWindowFlags(self, Qt_WindowFlags)

    @Slot()
    def on_btnMinimize_clicked(self):
        self.setWindowState(Qt.WindowMinimized)

    @Slot()
    def on_btnRestore_clicked(self):
        if self.btnMaximize.isEnabled() or self.btnRestore.isEnabled():
            self.btnRestore.setVisible(False)
            self.btnRestore.setEnabled(False)
            self.btnMaximize.setVisible(True)
            self.btnMaximize.setEnabled(True)
        self.setWindowState(Qt.WindowNoState)

    @Slot()
    def on_btnMaximize_clicked(self):
        if self.btnMaximize.isEnabled() or self.btnRestore.isEnabled():
            self.btnRestore.setVisible(True)
            self.btnRestore.setEnabled(True)
            self.btnMaximize.setVisible(False)
            self.btnMaximize.setEnabled(False)
        self.setWindowState(Qt.WindowMaximized)
        # gallery.setGridSize(QtCore.QSize(300, 300))

    @Slot()
    def on_btnClose_clicked(self):
        self.close()

    @Slot()
    def on_titleBar_doubleClicked(self):
        if not bool(self.windowState() & Qt.WindowMaximized):
            self.on_btnMaximize_clicked()
        else:
            self.on_btnRestore_clicked()


def dark(app):
    darkPalette = QPalette()
    # base
    darkPalette.setColor(QPalette.WindowText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.Light, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Midlight, QColor(90, 90, 90))
    darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.Text, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.BrightText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Link, QColor(56, 252, 196))
    darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))

    # disabled
    darkPalette.setColor(QPalette.Disabled, QPalette.WindowText,
                         QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Disabled, QPalette.Text,
                         QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText,
                         QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Disabled, QPalette.Highlight,
                         QColor(80, 80, 80))
    darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                         QColor(127, 127, 127))
    app.setPalette(darkPalette)
    _apply_base_theme(app)