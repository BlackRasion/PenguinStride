import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from MainWindow import MainWindow
from Login_page import LoginWindow
from qfluentwidgets import FluentTranslator

from config import cfg

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings) # 禁用Qt的原生窗口
        
        # 语言设置
        self.internationalization()
        
        # 将控制器实例存储在应用属性中
        self.app.setProperty("controller", self)

        self.login_window = LoginWindow()
        self.main_window = None
        
        # 显示登录窗口
        self.login_window.show()


    def show_main_window(self, username):
        """显示主窗口"""
        self.main_window = MainWindow(username)
        self.main_window.show()
        self.login_window.close()

    def run(self):
        sys.exit(self.app.exec())
    
    def internationalization(self):
        """翻译"""
        locale = cfg.get(cfg.language).value
        translator = FluentTranslator(locale)
        self.app.installTranslator(translator)

if __name__ == '__main__':
    controller = AppController()
    controller.run()