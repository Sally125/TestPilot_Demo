"""数据库迁移：启动时为已有表补充新增列（幂等）"""

from sqlalchemy import text
from app.database import engine


def run_migration():
    """启动时执行数据库迁移（幂等，字段已存在时静默跳过）"""
    with engine.connect() as conn:
        # test_cases 新增字段
        for ddl in [
            "ALTER TABLE test_cases ADD COLUMN review_status VARCHAR(30)",
            "ALTER TABLE test_cases ADD COLUMN version INTEGER NOT NULL DEFAULT 1",
        ]:
            try:
                conn.execute(text(ddl))
                conn.commit()
            except Exception:
                pass  # 字段已存在

        # review_reports 新增字段
        try:
            conn.execute(text(
                "ALTER TABLE review_reports ADD COLUMN is_expired INTEGER NOT NULL DEFAULT 0"
            ))
            conn.commit()
        except Exception:
            pass
