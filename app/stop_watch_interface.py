import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from qfluentwidgets import (
    FluentIcon, InfoBar, InfoBarPosition, SingleDirectionScrollArea, 
    Flyout, CaptionLabel, FlyoutView
)
from interfaces.StopWatchInterface_ui import Ui_StopWatchInterface


class StopWatchInterface(QWidget, Ui_StopWatchInterface):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._initUI()
        self._initVariables()
        self._connectSignals()
    
    def _initUI(self):
        """初始化UI元素"""
        # 设置窗口属性
        self.setWindowIcon(QIcon())
        self.setWindowTitle("StopWatch")

        # 设置按钮图标
        self.startButton.setIcon(FluentIcon.POWER_BUTTON)
        self.flagButton.setIcon(FluentIcon.FLAG)
        self.restartButton.setIcon(FluentIcon.CANCEL)
        self.RecordingButton.setIcon(FluentIcon.ALIGNMENT)
        self.RecordingButton.setText("Recordings")

        # 设置按钮属性
        self.flagButton.setCheckable(False)
        self.restartButton.setCheckable(False)
        self.RecordingButton.setCheckable(False)

        # 初始禁用按钮
        self.flagButton.setEnabled(False)
        self.restartButton.setEnabled(False)
        self.RecordingButton.setEnabled(False)
    
    def _initVariables(self):
        """初始化变量"""
        self.isRunning = False  # 是否正在计时
        self.elapsedTime = 0    # 已经过的时间（毫秒）
        self.flagCount = 0      # 标记计数
        self.flagRecords = []   # 标记记录列表
        
        # 创建计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.setInterval(10)  # 10毫秒更新一次
    
    def _connectSignals(self):
        """连接信号和槽"""
        self.startButton.clicked.connect(self.toggleTimer)
        self.flagButton.clicked.connect(self.recordFlag)
        self.restartButton.clicked.connect(self.resetTimer)
        self.RecordingButton.clicked.connect(self.showRecordings)
    
    def toggleTimer(self):
        """切换计时器状态（开始/暂停）"""
        if not self.isRunning:
            self._startTimer()
        else:
            self._pauseTimer()
    
    def _startTimer(self):
        """开始计时"""
        self.isRunning = True
        self.startButton.setIcon(FluentIcon.PAUSE)
        self.flagButton.setEnabled(True)
        self.restartButton.setEnabled(False)
        self.RecordingButton.setEnabled(False)
        self.timer.start()
    
    def _pauseTimer(self):
        """暂停计时"""
        self.isRunning = False
        self.startButton.setIcon(FluentIcon.POWER_BUTTON)
        self.flagButton.setEnabled(False)
        self.restartButton.setEnabled(True)
        
        # 只有在有记录时才启用记录按钮
        if self.flagRecords:
            self.RecordingButton.setEnabled(True)
            
        self.timer.stop()
    
    def updateTime(self):
        """更新显示的时间"""
        self.elapsedTime += 10  # 增加10毫秒
        
        # 计算时、分、秒
        hours, remainder = divmod(self.elapsedTime, 3600000)
        minutes, remainder = divmod(remainder, 60000)
        seconds, _ = divmod(remainder, 1000)
        
        # 更新显示
        self.timeLabel.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def recordFlag(self):
        """记录当前时间点"""
        if not self.isRunning:
            return
            
        self.flagCount += 1
        
        # 计算时间
        hours, remainder = divmod(self.elapsedTime, 3600000)
        minutes, remainder = divmod(remainder, 60000)
        seconds, remainder = divmod(remainder, 1000)
        milliseconds = remainder // 10
        
        # 格式化时间字符串
        timeStr = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        
        # 保存记录
        self.flagRecords.append({
            'index': self.flagCount,
            'time': timeStr,
            'milliseconds': self.elapsedTime
        })

        # 显示标记信息
        self._showFlagInfo(timeStr)
    
    def _showFlagInfo(self, timeStr):
        """显示标记信息提示"""
        InfoBar.success(
            title=f"标记 #{self.flagCount}",
            content=timeStr,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self
        )
    
    def resetTimer(self):
        """重置计时器"""
        self.timer.stop()
        self.isRunning = False
        self.elapsedTime = 0
        self.flagCount = 0
        self.flagRecords.clear()
        
        self._resetUI()
        self._showResetInfo()
    
    def _resetUI(self):
        """重置UI状态"""
        self.timeLabel.setText("00:00:00")
        self.startButton.setIcon(FluentIcon.POWER_BUTTON)
        self.startButton.setChecked(True)
        self.flagButton.setEnabled(False)
        self.restartButton.setEnabled(False)
        self.RecordingButton.setEnabled(False)
    
    def _showResetInfo(self):
        """显示重置信息提示"""
        InfoBar.info(
            title="计时器已重置",
            content="计时器已重置为零",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    
    def showRecordings(self):
        """显示记录的时间点"""
        if not self.flagRecords:
            return

        # 创建滚动区域和内容视图
        scrollArea, view = self._createRecordingsView()
        
        # 创建并显示弹出窗口
        flyout_view = self._createFlyoutView(scrollArea)
        w = Flyout.make(flyout_view, self.RecordingButton, self)
        flyout_view.closed.connect(w.close)
    
    def _createRecordingsView(self):
        """创建记录显示视图"""
        scrollArea = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        scrollArea.resize(300, 400)  # 设置合适的大小

        view = QWidget()
        layout = QVBoxLayout(view)
        
        # 添加记录标签
        for record in self.flagRecords:
            label = CaptionLabel(f"{record['index']}. {record['time']}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

        scrollArea.setWidget(view)
        
        # 设置样式
        scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")
        view.setStyleSheet("QWidget{background: transparent}")
        
        return scrollArea, view
    
    def _createFlyoutView(self, content_widget):
        """创建弹出视图"""
        flyout_view = FlyoutView(
            title='时间记录',
            content="记录的时间点列表",
            isClosable=True,
        )
        
        # 设置布局属性
        flyout_view.vBoxLayout.setSpacing(12)
        flyout_view.vBoxLayout.setContentsMargins(20, 16, 20, 16)
        flyout_view.vBoxLayout.addWidget(content_widget)
        flyout_view.widgetLayout.addSpacing(5)
        
        return flyout_view


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = StopWatchInterface()
    w.show()
    sys.exit(app.exec())