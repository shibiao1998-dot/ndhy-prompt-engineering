"""Import dimensions from 维度信息.md into the database.

Parses markdown tables for all 12 categories (A-L), 99 dimensions.
Replaces ALL existing dimension data.
"""

import os
import re
import sqlite3
from datetime import datetime

MD_PATH = os.path.join(os.path.dirname(__file__), "维度信息.md")
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "prompt_engineering.db")

CATEGORY_NAMES = {
    "A": "战略与价值观",
    "B": "用户真实性",
    "C": "竞品与差异化",
    "D": "场景与需求",
    "E": "设计方法与技巧",
    "F": "可行性与资源",
    "G": "历史经验与案例",
    "H": "设计标准与规范",
    "I": "质量判断与检查",
    "J": "特殊领域知识",
    "K": "专有名词与定义",
    "L": "项目全生命周期",
}


def parse_md_tables(filepath: str) -> list[dict]:
    """Parse all dimension tables from the markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    dimensions = []

    # Find all table rows that start with | **X## (dimension ID pattern)
    # Table format: | **A01** | **战略核心方向** | 具体信息内容 | 质量作用 | 数据来源 | 更新机制 |
    row_pattern = re.compile(
        r"^\|\s*\*\*([A-L]\d{2})\*\*\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
        re.MULTILINE,
    )

    for m in row_pattern.finditer(content):
        dim_id = m.group(1).strip()
        name = m.group(2).strip()
        description = m.group(3).strip()
        quality_role = m.group(4).strip()
        data_source = m.group(5).strip()
        update_frequency = m.group(6).strip()

        category = dim_id[0]
        category_name = CATEGORY_NAMES.get(category, category)

        # Clean up bold markers from quality_role
        quality_role = re.sub(r"\*\*(.+?)\*\*", r"\1", quality_role)

        dimensions.append({
            "id": dim_id,
            "name": name,
            "category": category,
            "category_name": category_name,
            "description": description,
            "quality_role": quality_role,
            "data_source": data_source,
            "update_frequency": update_frequency,
        })

    return dimensions


def update_db(dimensions: list[dict]):
    """Replace all dimensions in the database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure table exists with correct schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dimensions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            category_name TEXT,
            description TEXT,
            quality_role TEXT,
            data_source TEXT,
            update_frequency TEXT,
            source_explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add source_explanation column if missing (migration)
    try:
        cursor.execute("ALTER TABLE dimensions ADD COLUMN source_explanation TEXT")
    except Exception:
        pass

    # Clear old data
    cursor.execute("DELETE FROM dimensions")

    now = datetime.now().isoformat()
    inserted = 0
    for d in dimensions:
        cursor.execute(
            """INSERT INTO dimensions
               (id, name, category, category_name, description, quality_role, data_source, update_frequency, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (d["id"], d["name"], d["category"], d["category_name"],
             d["description"], d["quality_role"], d["data_source"], d["update_frequency"],
             now, now),
        )
        inserted += 1

    conn.commit()
    conn.close()
    return inserted


if __name__ == "__main__":
    dims = parse_md_tables(MD_PATH)
    print(f"Parsed {len(dims)} dimensions from {MD_PATH}")

    from collections import Counter
    cats = Counter(d["category"] for d in dims)
    for c in sorted(cats):
        print(f"  {c} {CATEGORY_NAMES.get(c, '?')}: {cats[c]}")

    # Show first dimension as sample
    if dims:
        d = dims[0]
        print(f"\nSample — {d['id']} {d['name']}:")
        print(f"  description: {d['description'][:100]}...")
        print(f"  quality_role: {d['quality_role']}")
        print(f"  data_source: {d['data_source']}")
        print(f"  update_frequency: {d['update_frequency']}")

    count = update_db(dims)
    print(f"\nInserted {count} dimensions into database")
