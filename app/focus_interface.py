# 标准库导入
import sys
import time
from datetime import datetime, timedelta

# 第三方库导入
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QTime, pyqtSignal
from PyQt6.QtGui import QIntValidator, QCursor, QKeySequence, QShortcut, QPixmap, QMovie

# 本地模块导入
from interfaces.FocusInterface_ui import Ui_FocusInterface
from qfluentwidgets import (
    FluentIcon, InfoBarIcon, InfoBar, InfoBarPosition, MessageBox, 
    StateToolTip, LineEdit, MessageBoxBase, SubtitleLabel,
    RoundMenu, Action,
    )
from utils import showHelpMessageBox

from paths import jpg_path, gif_path


class EditDailyTargetMB(MessageBox):
    """ 编辑每日目标时间对话框 """
    def __init__(self, title, content, parent=None):
        super().__init__(title, content, parent)
        self.LineEdit = LineEdit(self)
        self.LineEdit.setPlaceholderText("每日目标分钟数")
        self.LineEdit.setValidator(QIntValidator(0, 10000))
        self.LineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 添加输入框到按钮上方
        self.vBoxLayout.insertWidget(1, self.LineEdit)
        self.yesButton.setText("确定")
        self.cancelButton.setText("取消")
        self.widget.setMinimumWidth(300)
        # 添加回车键响应
        self.LineEdit.returnPressed.connect(self.accept)

class AddTaskMessageBox(MessageBoxBase):
    """ 添加任务对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('添加任务', self)
        self.LineEdit = LineEdit()
        self.LineEdit.setPlaceholderText('输入任务名称')
        self.LineEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.LineEdit)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)
        # 添加回车键响应
        self.LineEdit.returnPressed.connect(self.accept)

class EditTaskMessageBox(MessageBoxBase):
    """ 编辑任务对话框 """
    def __init__(self, task_name, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('编辑任务', self)
        self.LineEdit = LineEdit()
        self.LineEdit.setPlaceholderText(f'{task_name}')
        self.LineEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.LineEdit)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)
        # 添加回车键响应
        self.LineEdit.returnPressed.connect(self.accept)

class Task:
    """ 任务类 """
    def __init__(self, name, is_completed=False):
        self.name = name
        self.is_completed = is_completed
        self.created_time = datetime.now()

class FocusInterface(QWidget, Ui_FocusInterface):
    # 定义信号
    focusStarted = pyqtSignal(int)  # 专注开始信号，参数为专注时长(秒)
    focusEnded = pyqtSignal(int)    # 专注结束信号，参数为实际专注时长(秒)
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self) # 初始化界面
        
        # 初始化界面和变量
        self._initVariables()
        self._initUI()
        self.connectSignalsToSlots()
    
    def _initVariables(self):
        """初始化所有变量"""
        # 专注相关变量
        self.isFocusing = False  # 是否正在专注
        self.focusStartTime = None  # 专注开始时间
        self.focusTimer = QTimer(self)  # 专注计时器
        self.focusTimer.timeout.connect(self.updateFocusTime) 
        self.breakTimer = QTimer(self)  # 休息计时器
        self.breakTimer.timeout.connect(self.updateBreakTime)
        self.stateTooltip = None  # 状态提示
        
        # 每日进度相关变量
        self.dailyTarget = 120  # 每日目标专注分钟数
        self.dailyCompleted = 5  # 已完成分钟数
        self.continuousDays = 6  # 连续达标天数
        self.yesterdayMinutes = 30  # 昨天专注分钟数
        
        # 任务相关变量
        self.tasks = []  # 任务列表
    
    def _initUI(self):
        """初始化所有UI元素"""
        # 设置图标
        self.setIcons()
        
        # 设置默认时间
        self.timePicker.setTime(QTime(0, 25, 0))  # 默认25分钟
        
        # 初始化休息提示
        self.updateBreakHint()
        
        # 初始化进度界面
        self.initProgressUI()
        
        # 初始化任务界面
        self.initTaskUI()

        # 初始化图片卡片
        self.initImageCard()

    def setIcons(self):
        self.pinButton.setIcon(FluentIcon.PIN)
        self.moreButton.setIcon(FluentIcon.MORE)
        self.editButton.setIcon(FluentIcon.EDIT)
        self.addTaskButton.setIcon(FluentIcon.ADD)
        self.moreTaskButton.setIcon(FluentIcon.MORE)
        self.taskIcon1.setIcon(InfoBarIcon.SUCCESS)
        self.taskIcon2.setIcon(InfoBarIcon.WARNING)
        self.taskIcon3.setIcon(InfoBarIcon.WARNING)
        self.startFocusButton.setIcon(FluentIcon.POWER_BUTTON)   

    def initProgressUI(self):
        """初始化进度界面"""
        # 设置进度环
        self.progressRing.setMaximum(self.dailyTarget)
        self.progressRing.setValue(self.dailyCompleted)
        
        # 设置文本
        self.yesterdayTimeLabel.setText(str(self.yesterdayMinutes))
        self.compianceDayLabel.setText(str(self.continuousDays))
        self.finishTimeLabel.setText(f"已完成：{self.dailyCompleted} 分钟")

    def initTaskUI(self):
        """初始化任务界面"""
        self.addTask("完成专注功能开发")
        self.addTask("阅读《深度工作》一章")
        self.addTask("整理今日笔记")

    def initImageCard(self):
        """初始化图片卡片"""
        self.ImageLabel.setFixedSize(285, 285)
        self.ImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ImageLabel.setBorderRadius(8, 8, 8, 8)
        self.ImageLabel.setPixmap(QPixmap(jpg_path))
        self.ImageLabel.mousePressEvent = self.onImageClicked # 绑定鼠标点击事件

    def connectSignalsToSlots(self):
        """连接信号和槽"""
        # 专注时段部分
        self.startFocusButton.clicked.connect(self.toggleFocus)
        self.skipRelaxCheckBox.toggled.connect(self.updateBreakHint)
        self.timePicker.timeChanged.connect(self.updateBreakHint)
        
        # 每日进度部分
        self.editButton.clicked.connect(self.editDailyTarget)

        # 任务部分
        self.addTaskButton.clicked.connect(self.showAddTaskDialog)
        self.moreTaskButton.clicked.connect(self.showTaskMenu)
        
    # ================ 专注功能相关方法 ================    
    def updateBreakHint(self):
        """更新休息提示"""
        focusTime = self.timePicker.time
        minutes = focusTime.minute()
        seconds = focusTime.second()

        if self.skipRelaxCheckBox.isChecked():
            self.bottomHintLabel.setText("你将没有休息时间。")
        else:
            if minutes >= 25:
                breakTime = 5
            else:
                breakTime = 3
            self.bottomHintLabel.setText(f"每 {minutes} 分钟 {seconds} 秒 休息 {breakTime} 分钟。")
    
    def toggleFocus(self):
        """切换专注状态"""
        if not self.isFocusing:
            self.startFocus()
        else:
            self.confirmEndFocus()
    
    def startFocus(self):
        """开始专注"""
        focusTime = self.timePicker.time
        totalSeconds = focusTime.hour() * 3600 + focusTime.minute() * 60 + focusTime.second()
        
        if totalSeconds <= 0:
            InfoBar.error(
                title="错误",
                content="请设置有效的专注时间",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        # 更新UI状态
        self.isFocusing = True
        self.focusStartTime = datetime.now()
        self.startFocusButton.setText("结束专注")
        self.startFocusButton.setIcon(FluentIcon.CANCEL)

        self.ImageLabel.setMovie(QMovie(gif_path))
        self.ImageLabel.movie().start()
        
        # 禁用控件
        self.timePicker.setEnabled(False)
        self.skipRelaxCheckBox.setEnabled(False)
        
        # 显示状态提示
        self.stateTooltip = StateToolTip("专注进行中", "保持专注，不要分心", self.window())
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()
        
        # 启动定时器
        self.focusTimer.start(1000)  # 每秒更新一次
        
        # 发送信号
        self.focusStarted.emit(totalSeconds)
    
    def updateFocusTime(self):
        """更新专注时间"""
        if not self.focusStartTime:
            return
        
        elapsed = datetime.now() - self.focusStartTime
        elapsed_seconds = int(elapsed.total_seconds())
        
        # 更新状态提示
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.stateTooltip.setContent(f"已专注: {time_str}")
        
        # 检查是否需要休息
        if not self.skipRelaxCheckBox.isChecked():
            focusTime = self.timePicker.time
            focus_minutes = focusTime.minute()
            
            if focus_minutes > 0 and elapsed_seconds > 0 and elapsed_seconds % (focus_minutes * 60) < 1:
                self.startBreak()
    
    def startBreak(self):
        """开始休息"""
        # 暂停专注计时器
        self.focusTimer.stop()
        
        # 计算休息时间
        focusTime = self.timePicker.time
        minutes = focusTime.minute()
        if minutes >= 25:
            breakTime = 5 * 60  # 5分钟休息
        else:
            breakTime = 3 * 60  # 3分钟休息
        
        # 显示休息提示
        if self.stateTooltip:
            self.stateTooltip.close()
        
        self.stateTooltip = StateToolTip("休息时间", "站起来活动一下，放松眼睛", self.window())
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()
        
        # 设置休息结束时间
        self.breakEndTime = datetime.now() + timedelta(seconds=breakTime)
        
        # 启动休息计时器
        self.breakTimer.start(1000)  # 每秒更新一次
    
    def updateBreakTime(self):
        """更新休息时间"""
        remaining = self.breakEndTime - datetime.now()
        remaining_seconds = int(remaining.total_seconds())
        
        if remaining_seconds <= 0:
            # 休息结束
            self.breakTimer.stop()
            
            # 更新状态提示
            if self.stateTooltip:
                self.stateTooltip.close()
            
            self.stateTooltip = StateToolTip("专注进行中", "休息结束，继续专注", self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
            
            # 重新启动专注计时器
            self.focusTimer.start(1000)
        else:
            # 更新休息倒计时
            minutes, seconds = divmod(remaining_seconds, 60)
            self.stateTooltip.setContent(f"剩余休息时间: {minutes:02d}:{seconds:02d}")
    
    def confirmEndFocus(self):
        """确认结束专注"""
        dialog = MessageBox(
            "结束专注",
            "确定要结束当前的专注吗？",
            self.window()
        )
        dialog.yesButton.setText("是，结束专注")
        dialog.cancelButton.setText("不，继续专注")

        if dialog.exec():
            self.endFocus()
    
    def endFocus(self):
        """结束专注"""
        if not self.isFocusing or not self.focusStartTime:
            return
        
        # 停止计时器
        self.focusTimer.stop()
        self.breakTimer.stop()
        
        # 计算专注时间
        elapsed = datetime.now() - self.focusStartTime
        elapsed_seconds = int(elapsed.total_seconds())
        elapsed_minutes = elapsed_seconds // 60
        
        # 更新UI
        self.isFocusing = False
        self.startFocusButton.setText("启动专注时段")
        self.startFocusButton.setIcon(FluentIcon.POWER_BUTTON)
        self.ImageLabel.movie().stop()
        self.ImageLabel.setPixmap(QPixmap(jpg_path))
        
        # 启用控件
        self.timePicker.setEnabled(True)
        self.skipRelaxCheckBox.setEnabled(True)
        
        # 关闭状态提示
        if self.stateTooltip:
            self.stateTooltip.close()
            self.stateTooltip = None
        
        # 更新进度
        self.updateProgress(elapsed_minutes)
        
        # 显示完成提示
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        InfoBar.success(
            title="专注完成",
            content=f"本次专注时长: {time_str}",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )
        
        # 发送信号
        self.focusEnded.emit(elapsed_seconds)
    
    # ================ 每日进度相关方法 ================
    def updateProgress(self, minutes=0):
        """更新进度"""
        self.dailyCompleted += minutes
        
        # 更新进度环
        self.progressRing.setValue(min(self.dailyCompleted, self.dailyTarget))
        
        # 更新完成时间文本
        self.finishTimeLabel.setText(f"已完成：{self.dailyCompleted} 分钟")
        
        # 检查是否达标
        if self.dailyCompleted >= self.dailyTarget and self.dailyCompleted - minutes < self.dailyTarget:
            InfoBar.success(
                title="目标达成",
                content=f"恭喜你完成了今日 {self.dailyTarget} 分钟的专注目标！",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
    
    def editDailyTarget(self):
        """编辑每日目标"""
        dialog = EditDailyTargetMB(
            "设置每日目标",
            f"当前目标为 {self.dailyTarget} 分钟，请输入新的每日专注目标分钟数",
            self.window()
        )
        
        if dialog.exec():
            new_target = int(dialog.LineEdit.text())
            self.dailyTarget = new_target
            self.progressRing.setFormat(f"目标 {new_target} 分钟")
            self.progressRing.setMaximum(self.dailyTarget)
            self.progressRing.setValue(min(self.dailyCompleted, self.dailyTarget))
            
            InfoBar.success(
                title="目标已更新",
                content=f"每日目标已设置为 {self.dailyTarget} 分钟",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )

    # ================ 任务相关方法 ================
    def onTaskClicked(self, event, index):
        """任务被点击时触发的槽函数"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggleTaskStatus(index)
        elif event.button() == Qt.MouseButton.RightButton:
            self.showRoundTaskMenu(index)

    def toggleTaskStatus(self, index):
            """切换任务状态"""
            if 0 <= index < len(self.tasks):
                task = self.tasks[index]
                task.is_completed = not task.is_completed
                self.updateTaskList()
                
                status = "已完成" if task.is_completed else "未完成"
                #延迟一段时间再显示消息框
                QTimer.singleShot(100, lambda: self.showTaskStatusMessage(status, task))
                
    def showTaskStatusMessage(self, status, task):
        """显示任务状态消息框"""
        if status == "已完成":
            InfoBar.success(
                title=f"任务已完成",
                content=f"{task.name}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
        else:
            InfoBar.warning(
                title=f"任务未完成", 
                content=f"{task.name}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self

            )

    def showRoundTaskMenu(self, index):
        """显示任务卡片右键菜单"""
        if 0 <= index < len(self.tasks):
            menu = RoundMenu()
            
            editAction = Action(FluentIcon.EDIT, "修改")
            editAction.triggered.connect(lambda: self.editTask(index))
            
            deleteAction = Action(FluentIcon.DELETE, "删除")
            deleteAction.triggered.connect(lambda: self.deleteTask(index))

            helpShortcut = QShortcut(QKeySequence("Ctrl+H"), self)
            helpAction = Action(FluentIcon.HELP, "帮助", self, shortcut="Ctrl+H")
            helpAction.triggered.connect(lambda: showHelpMessageBox(self))
            helpShortcut.activated.connect(lambda: helpAction.triggered.emit())
            
            menu.addAction(editAction)
            menu.addAction(deleteAction)
            menu.addSeparator()
            menu.addAction(helpAction)
            
            # 显示菜单在右击位置  
            menu.exec(QCursor.pos())            

    def editTask(self, index):
        """编辑任务"""
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            dialog = EditTaskMessageBox(task.name, self.window())
            if dialog.exec():
                new_name = dialog.LineEdit.text()
                if new_name and new_name.strip():
                    task.name = new_name.strip()  # 直接修改任务名称
                    self.updateTaskList()  # 更新任务列表显示
                    
                    InfoBar.success(
                        title="修改成功",
                        content=f"任务已修改为：{new_name.strip()}",
                        orient=Qt.Orientation.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=2000,
                        parent=self
                    )

    def deleteTask(self, index):
        """删除任务"""
        if 0 <= index < len(self.tasks):
            task_name = self.tasks[index].name
            del self.tasks[index]
            self.updateTaskList()
            
            InfoBar.success(
                title="删除成功",
                content=f"已删除任务：{task_name}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )

    def showAddTaskDialog(self):
        """显示添加任务对话框"""
        messagebox = AddTaskMessageBox(self.window())
        if messagebox.exec():
            task_name = messagebox.LineEdit.text()
            if self.addTask(task_name):
                InfoBar.success(
                title="任务已添加",
                content=f"已添加任务：{task_name}",                
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
                )

    def addTask(self, task_name):
        """添加任务"""
        if task_name and task_name.strip():
            task = Task(task_name.strip())
            self.tasks.append(task)
            self.updateTaskList()
            return True
        return False
    
    def showTaskMenu(self):
        """显示任务菜单"""
        menu = RoundMenu()
        
        # 添加菜单项
        clearCompletedAction = Action(FluentIcon.BROOM, "清除已完成任务", self)
        clearCompletedAction.triggered.connect(self.clearCompletedTasks)
        
        clearAllAction = Action(FluentIcon.DELETE, "清除所有任务", self)
        clearAllAction.triggered.connect(self.clearAllTasks)
        
        menu.addAction(clearCompletedAction)
        menu.addAction(clearAllAction)
        
        # 显示菜单
        menu.exec(self.moreTaskButton.mapToGlobal(self.moreTaskButton.rect().bottomRight()))

    def clearCompletedTasks(self):
        """清除已完成任务"""
        completed_count = sum(1 for task in self.tasks if task.is_completed)
        if completed_count == 0:
            InfoBar.info(
                title="提示",
                content="没有已完成的任务",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            return
            
        self.tasks = [task for task in self.tasks if not task.is_completed]
        self.updateTaskList()
        
        InfoBar.success(
            title="清理成功",
            content=f"已清除 {completed_count} 个已完成任务",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self
        )
    
    def clearAllTasks(self):
        """清除所有任务"""
        if not self.tasks:
            InfoBar.information(
                title="提示",
                content="任务列表为空",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            return
            
        dialog = MessageBox(
            "清除所有任务",
            "确定要清除所有任务吗？此操作不可撤销。",
            self.window()
        )
        
        if dialog.exec():
            task_count = len(self.tasks)
            self.tasks.clear()
            self.updateTaskList()
            
            InfoBar.success(
                title="清理成功",
                content=f"已清除所有 {task_count} 个任务",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
    
    def updateTaskList(self):
        """更新任务列表显示"""
        # 清空任务区域
        self._clearTaskArea()
        
        # 重新创建任务卡片
        self._createTaskCards()
        
        # 更新提示文本
        self._updateTaskHint()
    
    def _clearTaskArea(self):
        """清空任务区域"""
        # 获取滚动区域的内容布局
        layout = self.scrollAreaWidgetContents.layout()
        
        # 移除所有卡片组件
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 确保弹性空间也被移除
        layout.removeItem(layout.itemAt(0) if layout.count() > 0 else None)
            
    def _createTaskCards(self):
        """创建所有任务卡片"""
        from qfluentwidgets import ElevatedCardWidget, BodyLabel, IconWidget
        from PyQt6.QtWidgets import QHBoxLayout
        
        # 倒序创建
        for i, task in reversed(list(enumerate(self.tasks))):
            # 创建任务卡片
            card = self._createTaskCard(i, task)
            # 添加到滚动区域
            self.scrollAreaWidgetContents.layout().addWidget(card)
        
        # 添加弹性空间
        self.scrollAreaWidgetContents.layout().addStretch(1)
    
    def _createTaskCard(self, index, task):
        """创建单个任务卡片"""
        from qfluentwidgets import ElevatedCardWidget, BodyLabel, IconWidget
        from PyQt6.QtWidgets import QHBoxLayout
        
        card = ElevatedCardWidget(self.scrollAreaWidgetContents)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(10)
        
        # 创建任务图标
        icon = IconWidget(card)
        icon.setMinimumSize(16, 16)
        icon.setMaximumSize(16, 16)
        
        # 根据任务状态设置图标
        icon.setIcon(InfoBarIcon.SUCCESS if task.is_completed else InfoBarIcon.WARNING)
        
        # 创建任务标签
        label = BodyLabel(task.name, card)
        
        # 如果任务已完成，添加删除线
        if task.is_completed:
            label.setProperty("strikeOut", True)
            label.style().polish(label)
        
        # 添加组件到布局
        layout.addWidget(icon)
        layout.addWidget(label)
        
        # 设置最小高度
        card.setMinimumHeight(44)
        
        # 连接点击事件
        card.mousePressEvent = lambda event, idx=index: self.onTaskClicked(event, idx)
        
        return card
    
    def _updateTaskHint(self):
        """更新任务提示文本"""
        if not self.tasks:
            self.hintLabel_2.setText("没有任务，点击 + 添加新任务")
        else:
            total = len(self.tasks)
            completed = sum(1 for task in self.tasks if task.is_completed)
            self.hintLabel_2.setText(f"共 {total} 个任务，已完成 {completed} 个")

    # ================ 图片卡片相关方法 ================
    def onImageClicked(self, event):
        """图片被点击时触发的槽函数"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.showImageMessage()
    def showImageMessage(self):
        """显示图片消息框"""
        if self.isFocusing:
            title = f"🍵"
            content = f"Working..."

        else:
            title = f"🐧"
            content = f"Resting."

        InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
        
# 开启页面
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FocusInterface()
    window.show()
    sys.exit(app.exec())