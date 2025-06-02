import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut, QIcon

from qfluentwidgets import (
    FluentWindow, FluentIcon, 
    NavigationItemPosition, InfoBar, InfoBarPosition, SplashScreen, 
    isDarkTheme, RoundMenu, Action, 
    MenuAnimationType, FluentTranslator
)
from focus_interface import FocusInterface
from stop_watch_interface import StopWatchInterface
from setting_interface import SettingInterface
from config import cfg
from utils import signalBus

from utils import showHelpMessageBox


class MainWindow(FluentWindow):
    def __init__(self, username="游客"):
        super().__init__()

        self._initUI() # 初始化UI
        
        self._initSubInterface() # 初始化子页面

        self.connectSignalToSlot() # 连接信号槽

        self._initNavigation() # 初始化导航栏
        
        self.splashScreen.finish() # 关闭闪屏

        # 显示欢迎消息
        self.username = username  # 存储用户名
        if self.username:
            self.show_welcome_message(self.username)

    def _initUI(self):
        """初始化UI"""
        # 设置大小
        self.resize(911, 807)
        self.setMinimumWidth(807)

        # 设置标题栏
        self.setWindowIcon(QIcon("./resource/images/penguin.ico"))
        self.setWindowTitle("Penguin Stride") 

        # 亚克力效果
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))
        
        # 创建闪屏
        self.splashScreen = SplashScreen(FluentIcon.CARE_RIGHT_SOLID, self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        # 窗口居中
        self.center_window()

        self.show()

        # 立即处理
        QApplication.processEvents()
    
    def center_window(self):
        """窗口居中"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def _initSubInterface(self):
        """初始化子页面"""
        self.focusInterface = FocusInterface(self) # 专注
        self.addSubInterface(self.focusInterface, FluentIcon.RINGER, self.tr('Focus Time'))

        self.stopWatchInterface = StopWatchInterface(self) # 计时
        self.addSubInterface(self.stopWatchInterface, FluentIcon.STOP_WATCH, self.tr('Stop Watch'))

        self.settingInterface = SettingInterface(self) # 设置
        self.addSubInterface(
            self.settingInterface, FluentIcon.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def connectSignalToSlot(self):
        """连接信号槽"""
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def _initNavigation(self):
        """初始化导航栏"""
        self.navigationInterface.addItem( # 帮助 
            routeKey='HelpInterface',
            icon=FluentIcon.HELP,
            text=self.tr('Help'),
            onClick=lambda:showHelpMessageBox(self),
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

    def show_welcome_message(self, username):
        """显示欢迎消息"""
        InfoBar.success(
            title="Welcome",
            content=f"Welcome back, {username}!",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=4000, 
            parent=self
        )
    
    def contextMenuEvent(self, e):
        """右键菜单"""
        menu = RoundMenu(parent=self)

        # NOTE: 隐藏快捷键
        # menu.view.setItemDelegate(MenuItemDelegate())

        # add actions
        menu.addAction(Action(FluentIcon.COPY, 'Copy'))
        menu.addAction(Action(FluentIcon.CUT, 'Cut'))
        menu.actions()[0].setCheckable(True)
        menu.actions()[0].setChecked(True)

        # add sub menu
        submenu = RoundMenu("Add to", self)
        submenu.setIcon(FluentIcon.ADD)
        submenu.addActions([
            Action(FluentIcon.VIDEO, 'Video'),
            Action(FluentIcon.MUSIC, 'Music'),
        ])
        menu.addMenu(submenu)

        # add actions
        menu.addActions([
            Action(FluentIcon.PASTE, 'Paste'),
            Action(FluentIcon.CANCEL, 'Undo')
        ])

        menu.addSeparator() # 添加分隔符

        menu.addAction(Action(f'Select all', shortcut='Ctrl+A'))

        
        helpShortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        helpAction = Action(FluentIcon.HELP, "帮助", self, shortcut="Ctrl+H")
        helpAction.triggered.connect(lambda: showHelpMessageBox(self))
        helpShortcut.activated.connect(lambda: showHelpMessageBox(self))

        # 插入操作
        menu.insertAction(
            menu.actions()[-1], Action(FluentIcon.SETTING, 'Settings', shortcut='Ctrl+S'))
        menu.insertActions(
            menu.actions()[-1],
            [helpAction,
             Action(FluentIcon.FEEDBACK, 'Feedback', shortcut='Ctrl+F')]
        )
        menu.actions()[-2].setCheckable(True)
        menu.actions()[-2].setChecked(True)

        # 显示菜单
        menu.exec(e.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def resizeEvent(self, e):
        """窗口大小改变事件"""
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, e):
        """关闭窗口"""
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        """亚克力主题改变完成"""
        super()._onThemeChangedFinished()

        # 重试
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))

if __name__ == '__main__':
    # 创建应用
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

    # 语言设置
    locale = cfg.get(cfg.language).value
    translator = FluentTranslator(locale)

    app.installTranslator(translator)

    # 创建窗口
    w = MainWindow()
    w.show()

    app.exec()