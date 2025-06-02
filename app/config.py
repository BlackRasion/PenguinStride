# coding:utf-8
from enum import Enum
import sys
from PyQt6.QtCore import QLocale
from qfluentwidgets import (
    qconfig, QConfig, ConfigItem, OptionsConfigItem, 
    BoolValidator, OptionsValidator, ConfigSerializer
)

def isWin11():
    """ 判断是否为Windows 11 """
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000

class Language(Enum):
    """ 语言枚举类 """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Language.Chinese, QLocale.Country.HongKong)
    ENGLISH = QLocale(QLocale.Language.English)
    AUTO = QLocale()

class LanguageSerializer(ConfigSerializer):
    """ 语言序列化器 """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ 配置类 """
    language = OptionsConfigItem( # 语言
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)
    minimizeToTray = ConfigItem( # 最小化到托盘
        "MainWindow", "MinimizeToTray", True, BoolValidator())  
    micaEnabled = ConfigItem( # 亚克力效果
        "MainWindow", "MicaEnabled", isWin11(), BoolValidator())  


HELP_URL = "https://qfluentwidgets.com/zh/pages/about"

cfg = Config() # 创建配置实例并使用配置文件来初始化它
qconfig.load('./config/config.json', cfg) # 加载配置文件
