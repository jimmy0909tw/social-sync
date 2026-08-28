import os
import json
from abc import ABC, abstractmethod

class BaseCollector(ABC):
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
        self.config_file = os.path.join(self.config_dir, f"{platform_name}_config.json")
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        """若 JSON 檔不存在，自動建立預設模板"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        if not os.path.exists(self.config_file):
            default_config = self.get_default_config()
            self.save_config(default_config)

    def load_config(self) -> dict:
        """讀取該平台獨立的 JSON 設定檔"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config for {self.platform_name}: {e}")
            return {}

    def save_config(self, config_data: dict):
        """寫入/更新該平台獨立的 JSON 設定檔"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

    @abstractmethod
    def get_default_config(self) -> dict:
        """各平台需自行定義預設需要的 API 密鑰格式"""
        pass

    @abstractmethod
    def fetch_metrics(self) -> dict:
        """各平台自行實作 API 連線與數據抓取"""
        pass
