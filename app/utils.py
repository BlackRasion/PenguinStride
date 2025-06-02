from qfluentwidgets import MessageBox

from PyQt6.QtCore import QObject, pyqtSignal

class SignalBus(QObject):
    """ 信号总线 """
    micaEnableChanged = pyqtSignal(bool) # 亚克力效果开关信号
    minimizeToTrayChanged = pyqtSignal(bool)  # 最小化到托盘信号

signalBus = SignalBus()
def showHelpMessageBox(window):
        """显示帮助消息框"""
        print("显示帮助消息框")
        w = MessageBox(
            '你好哇🥰',
            '每个人都有自己的人生节奏和选择，没有对错，没有高低，只有是否合适与自洽🐧。愿我们都能做出无愧于心的选择❤️。',
            window,   
        )
        w.yesButton.setText('随性而为')
        w.cancelButton.setText('循心而往')
        if w.exec():
            pass    
