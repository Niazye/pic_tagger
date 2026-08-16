from pathlib import Path
import sys


def get_base_path() -> Path:
    """
    获取程序基础路径。

    在打包（PyInstaller）环境下返回解压临时目录，
    在开发环境下返回 src 目录。
    """
    if getattr(sys, 'frozen', False):
        # 打包环境：sys._MEIPASS 是 PyInstaller 解压的临时目录
        return Path(sys._MEIPASS)
    else:
        # 开发环境：返回 src 目录
        return Path(__file__).parent.parent


def get_app_root() -> Path:
    """
    获取程序根目录（数据保存位置）。

    根据 PRD 的"绿色"要求，数据全部保存在程序文件夹内，
    不使用注册表或系统目录。

    - 打包环境：返回可执行文件所在目录（用户可写）
    - 开发环境：返回项目根目录（pic_tagger/）
    """
    if getattr(sys, 'frozen', False):
        # 打包后：可执行文件所在目录
        return Path(sys.executable).parent
    else:
        # 开发环境：项目根目录（src 的上一级）
        return Path(__file__).parent.parent.parent


def get_user_data_path() -> Path:
    """
    获取用户数据目录。

    所有持久化数据（数据库、配置、日志）都保存在此目录下。
    遵循"绿色"原则：数据全部在程序文件夹内，不污染系统目录。
    """
    return get_app_root()


def get_db_path() -> Path:
    """获取 SQLite 数据库文件路径。"""
    return get_user_data_path() / "data.db"


def get_cache_dir() -> Path:
    """获取缓存目录（缩略图等）。"""
    return get_user_data_path() / "cache"


def get_thumbnail_dir() -> Path:
    """获取缩略图缓存目录。"""
    return get_cache_dir() / "thumbnails"


def get_logs_dir() -> Path:
    """获取日志目录。"""
    return get_user_data_path() / "logs"


def get_config_path() -> Path:
    """获取配置文件路径。"""
    return get_user_data_path() / "config.json"


def ensure_dirs() -> None:
    """
    确保所有必要的目录存在。

    在程序启动时调用，创建数据目录结构：
    - cache/thumbnails/（缩略图缓存）
    - logs/（日志）
    """
    get_thumbnail_dir().mkdir(parents=True, exist_ok=True)
    get_logs_dir().mkdir(parents=True, exist_ok=True)
