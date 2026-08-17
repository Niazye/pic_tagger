from src.utils.path import get_config_path
from pathlib import Path
import json

class Config:
    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or get_config_path()
        self.data: dict = {}
        self.load()
    def load(self) -> None:
        if self.config_path.exists():
            try:
                self.data = json.loads(self.config_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                self.data = self.data or {}
        else:
            self.data = self.data or {}
    def save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(self.data, indent=4, ensure_ascii=False), encoding='utf-8')

    def get(self, key: str, default=None):
        """获取配置项"""
        return self.data.get(key, default)

    def set(self, key: str, value) -> None:
        """设置配置项"""
        self.data[key] = value
        self.save()

config = Config()