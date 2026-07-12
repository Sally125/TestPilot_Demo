"""查看 SQLite 数据库表结构和数据概况"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import get_settings

db_path = get_settings().db_path
print(f"数据库路径: {db_path}")
print(f"文件存在: {db_path.exists()}")

if not db_path.exists():
    print("\n数据库尚未创建。启动 FastAPI 服务时会自动建表：")
    print("  uvicorn app.main:app --port 8000")
    sys.exit(0)

print(f"文件大小: {db_path.stat().st_size} bytes\n")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print(f"表数量: {len(tables)}")
print("-" * 50)

for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM [{table}]")
    count = cur.fetchone()[0]
    print(f"\n[{table}] — {count} 条记录")
    if count > 0 and count <= 5:
        cur.execute(f"SELECT * FROM [{table}] LIMIT 5")
        cols = [d[0] for d in cur.description]
        print(f"  字段: {', '.join(cols)}")
        for row in cur.fetchall():
            preview = {k: (str(v)[:80] + "..." if v and len(str(v)) > 80 else v) for k, v in dict(row).items()}
            print(f"  → {preview}")

conn.close()
