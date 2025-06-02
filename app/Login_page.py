import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from interfaces.login_ui import Ui_Form
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import setThemeColor, FluentIcon, FluentIconBase, Theme, InfoBar, InfoBarPosition, setTheme

from config import cfg

class CustomTitleBar(StandardTitleBar):
    """ Custom title bar without maximize button and double click maximize """
    
    def __init__(self, parent):
        super().__init__(parent)

        # Remove maximize button
        self.maxBtn.hide()
        self.maxBtn.deleteLater()
        
        # Disable double click maximize
        self.setDoubleClickEnabled(False)


class LoginWindow(FramelessWindow, Ui_Form):
    """登录窗口"""
    def __init__(self):
        super().__init__()
        self._initUI() # 初始化UI
        self._initSignal()  # 连接信号和槽

    def _initUI(self):
        """初始化UI"""
        self.setupUi(self) # 加载UI文件

        setThemeColor(cfg.get(cfg.themeColor)) # 设置主题色

        # 设置标题栏
        TitleBar = CustomTitleBar(self) # 无放大缩小按钮
        TitleBar.setTitle("Penguin Stride")
        TitleBar.setIcon(FluentIconBase.icon((FluentIcon.APPLICATION), theme=Theme.AUTO, color=QColor(255, 255, 255)))
        self.setTitleBar(TitleBar)
        
        # 窗口居中
        self.center_window()

        # 设置预定义的用户名和密码
        self.valid_username = "jojo"
        self.valid_password = "123456"

    def center_window(self):
        """窗口居中"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def _initSignal(self):
        """初始化信号"""
        self.pushButton.clicked.connect(self.login)  # 登录按钮
        self.pushButton_2.toggled.connect(self.toggle_guest_mode)  # Guest Mode按钮
        self.lineEdit.returnPressed.connect(self.focus_password)  # 用户名输入完成后按回车跳转到密码
        self.lineEdit_2.returnPressed.connect(self.login)  # 密码输入完成后按回车登录

    def focus_password(self):
        """用户名输入完成后，焦点转移到密码输入框"""
        self.lineEdit_2.setFocus()
        
    def toggle_guest_mode(self, checked):
        """切换访客模式"""
        if checked:
            # 禁用用户名和密码输入
            self.lineEdit.setEnabled(False)
            self.lineEdit_2.setEnabled(False)
        else:
            # 启用用户名和密码输入
            self.lineEdit.setEnabled(True)
            self.lineEdit_2.setEnabled(True)
            
    def login(self):
        """登录验证"""
        # 如果是访客模式，直接登录
        if self.pushButton_2.isChecked():
            self.login_success("访客")
            return
            
        # 获取用户名和密码
        username = self.lineEdit.text().strip()
        password = self.lineEdit_2.text()
        
        # 验证用户名和密码
        if not username:
            self.show_error_message("请输入用户名")
            return
            
        if not password:
            self.show_error_message("请输入密码")
            return
            
        # 验证用户名和密码是否正确
        if username == self.valid_username and password == self.valid_password:
            self.login_success(username)
        else:
            self.show_error_message("用户名或密码错误")
            
    def show_error_message(self, message):
        """显示错误消息"""
        InfoBar.error(
            title="登录失败",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
            
    def login_success(self, username):
        """登录成功后的操作"""
        # 获取应用控制器实例
        controller = QApplication.instance().property("controller")
        if controller:
            controller.show_main_window(username)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    setTheme(Theme.AUTO) # 设置主题
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())



