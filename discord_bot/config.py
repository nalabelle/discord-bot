"""
Discord Bot Settings and Configuration
"""

from pathlib import Path

from pydantic import conlist, conset, constr
from pydantic_yaml import YamlModel, YamlStrEnum


class LogLevelEnum(YamlStrEnum):
    """Log Level Enum for Validation"""

    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    WARN = "WARN"
    INFO = "INFO"
    DEBUG = "DEBUG"


class ExtensionConfig(YamlModel):
    """Structure for Extension Config"""

    name: str
    path_override: str = None
    intents: conset(item_type=str) = set()


class BotConfig(YamlModel):
    """Base Config Class"""

    command_prefix: constr(min_length=1, max_length=1, strip_whitespace=True) = "!"
    log_level: LogLevelEnum = LogLevelEnum.WARNING
    discord_log_level: LogLevelEnum = LogLevelEnum.ERROR
    data_path: str
    extension_path: str
    extensions: conlist(item_type=ExtensionConfig) = []


def load(config_path: Path) -> BotConfig:
    """Loads the Config from the config_path and returns a BotConfig"""
    return BotConfig.parse_file(config_path)
