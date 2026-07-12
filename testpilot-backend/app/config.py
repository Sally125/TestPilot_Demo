"""配置管理：从 .env 文件读取所有配置项"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，通过 .env 文件注入"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===== DeepSeek API =====
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # ===== 服务 =====
    app_port: int = 8000
    debug: bool = True

    # ===== Playwright 执行 =====
    target_app_url: str = ""
    browser_type: str = "chromium"
    browser_timeout: int = 30000
    storage_state_path: str = ""

    # ===== 测试账号 =====
    test_username: str = ""
    test_password: str = ""
    login_url: str = ""

    @property
    def base_dir(self) -> Path:
        """项目根目录"""
        return Path(__file__).resolve().parent.parent

    @property
    def generated_dir(self) -> Path:
        """AI 生成的 Playwright 脚本存放目录"""
        path = self.base_dir / "generated"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def playwright_root(self) -> Path:
        """Playwright 依赖所在目录（含 node_modules/@playwright/test）"""
        for candidate in (self.base_dir, self.base_dir.parent, self.base_dir.parent.parent):
            if (candidate / "node_modules" / "@playwright" / "test").exists():
                return candidate
        return self.base_dir.parent

    @property
    def runtime_dir(self) -> Path:
        """单次脚本执行的临时目录（位于项目内，便于 Playwright 发现依赖）"""
        path = self.generated_dir / ".runtime"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def db_path(self) -> Path:
        """SQLite数据库文件路径"""
        path = self.base_dir / "data" / "testpilot.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def has_api_key(self) -> bool:
        return bool(self.deepseek_api_key and self.deepseek_api_key.startswith("sk-"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
