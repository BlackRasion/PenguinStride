# coding:utf-8
from config import cfg, HELP_URL, isWin11
from qfluentwidgets import (
    SettingCardGroup, SwitchSettingCard, OptionsSettingCard,
    ComboBoxSettingCard, ExpandLayout, CustomColorSettingCard,
    setTheme, setThemeColor, isDarkTheme, ScrollArea, HyperlinkCard,
    LargeTitleLabel, InfoBar, FluentIcon
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget

from utils import signalBus

from paths import *

class SettingInterface(ScrollArea):
    """ 设置页面 """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # 设置标签
        self.settingLabel = LargeTitleLabel(self.tr("Settings"), self)

        # 个性化
        self.personalGroup = SettingCardGroup(self.tr('Personalization'), self.scrollWidget)
        self.micaCard = SwitchSettingCard( # 亚克力效果开关设置卡
            FluentIcon.TRANSPARENT,
            self.tr("Mica effect"),
            self.tr("Apply semi transparent to windows and surfaces"),
            configItem=cfg.micaEnabled,
            parent=self.personalGroup
        )
        self.themeCard = OptionsSettingCard( # 主题设置卡
            cfg.themeMode,
            FluentIcon.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )

        self.themeColorCard=CustomColorSettingCard( # 主题颜色设置卡
            cfg.themeColor,
            FluentIcon.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        ) 

        self.languageCard = ComboBoxSettingCard( # 语言下拉选项设置卡
            cfg.language,
            FluentIcon.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # 主面板
        self.mainPanelGroup = SettingCardGroup(self.tr('Main Panel'), self.scrollWidget)
        self.minimizeToTrayCard = SwitchSettingCard( # 最小化到托盘开关设置卡
            FluentIcon.MINIMIZE,
            self.tr('Minimize to tray after closing'),
            self.tr('PyQt-Fluent-Widgets will continue to run in the background'),
            configItem=cfg.minimizeToTray,
            parent=self.mainPanelGroup
        )

        # 关于
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.helpCard = HyperlinkCard( # 帮助超链接卡
            HELP_URL,
            self.tr('Open help page'),
            FluentIcon.HELP,
            self.tr('Help'),
            self.tr('Discover new features and learn useful tips about PyQt-Fluent-Widgets'),
            self.aboutGroup
        )

        self._initWidget()

    def _initWidget(self): # 初始化界面
        self.resize(911, 807)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # 水平滚动条策略
        self.setViewportMargins(0, 120, 0, 20) # 设置视口边距
        self.setWidget(self.scrollWidget) 
        self.setWidgetResizable(True) 
        self.setObjectName('settingInterface') # 设置对象名

        # 初始化样式表
        self._setQss()

        # 初始化布局
        self._initLayout()

        # 初始化信号槽
        self._initSignal()

    def _initLayout(self): # 初始化布局
        self.settingLabel.move(60, 63) # 设置标签位置
        
        # 添加卡片到组
        self.personalGroup.addSettingCard(self.micaCard) 
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)

        self.aboutGroup.addSettingCard(self.helpCard)

        # 添加组到布局
        self.expandLayout.setSpacing(28) # 设置组之间的间距
        self.expandLayout.setContentsMargins(60, 0, 60, 0) # 设置组的边距
        self.expandLayout.addWidget(self.personalGroup) # 添加个性化组
        self.expandLayout.addWidget(self.mainPanelGroup) # 添加主面板组
        self.expandLayout.addWidget(self.aboutGroup) # 添加关于组

    def _initSignal(self): # 初始化信号槽
        """ 连接信号槽 """
        # 重启信号
        cfg.appRestartSig.connect(self.__showRestartTooltip)

        # 个性化组
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged) # 亚克力效果开关改变信号

        cfg.themeChanged.connect(setTheme) # 主题改变信号
    
        self.themeColorCard.colorChanged.connect(setThemeColor) # 主题颜色改变信号

        # 主面板组
        self.minimizeToTrayCard.checkedChanged.connect( # 最小化到托盘开关改变信号
            signalBus.minimizeToTrayChanged)

        # 关于组

    def __showRestartTooltip(self): 
        """ 显示重启提示 """
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )
    
    def _setQss(self): 
        """ 设置样式表 """
        self.settingLabel.setObjectName('settingLabel') # 设置标签对象名
        self.personalGroup.setObjectName('personalGroup') # 设置个性化组对象名
        self.scrollWidget.setObjectName('scrollWidget') # 设置滚动部件对象名
        
        theme = 'dark' if isDarkTheme() else 'light'
        theme_path = os.path.join(qss_path, theme, "setting_interface.qss")
        with open(theme_path, encoding='utf-8') as f: # 打开样式表文件
            self.setStyleSheet(f.read()) # 设置样式表     
        self.micaCard.setEnabled(isWin11())

           

       