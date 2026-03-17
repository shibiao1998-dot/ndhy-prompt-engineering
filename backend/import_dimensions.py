"""Import dimensions from v1 project markdown files into the v2 database.

Parses 12 categories × ~99 dimensions from:
  D:\code\openclaw-home\workspace\projects\prompt-engineering\dimensions\*.md

Each dimension extracts: id, name, category, category_name,
description (具体信息内容), quality_role (质量作用),
data_source (数据来源), update_frequency (更新机制).
"""

import os
import re
import sqlite3
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────────
V1_DIMENSIONS_DIR = r"D:\code\openclaw-home\workspace\projects\prompt-engineering\dimensions"
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "prompt_engineering.db")

# ── Category map (from filenames and headers) ────────────────────
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


def parse_md_file(filepath: str) -> list[dict]:
    """Parse a single dimension markdown file into dimension records."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    dimensions = []

    # Split by ## headings (dimension entries like "## A01 战略核心方向")
    # Pattern: ## <ID> <Name>
    dim_pattern = re.compile(r"^## ([A-L]\d{2})\s+(.+)$", re.MULTILINE)
    matches = list(dim_pattern.finditer(content))

    for i, match in enumerate(matches):
        dim_id = match.group(1)
        dim_name = match.group(2).strip()
        category = dim_id[0]
        category_name = CATEGORY_NAMES.get(category, category)

        # Extract section content (from this heading to the next heading or end)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section = content[start:end].strip()

        # Extract fields
        description = _extract_section(section, "具体信息内容")
        quality_role = _extract_field(section, "质量作用")
        data_source = _extract_field(section, "数据来源")
        update_frequency = _extract_field(section, "更新机制")

        # If no "具体信息内容" section found, try "维度定义" as fallback
        if not description:
            description = _extract_field(section, "维度定义")

        dimensions.append({
            "id": dim_id,
            "name": dim_name,
            "category": category,
            "category_name": category_name,
            "description": description or "",
            "quality_role": quality_role or "",
            "data_source": data_source or "",
            "update_frequency": update_frequency or "",
        })

    return dimensions


def _extract_section(text: str, heading: str) -> str:
    """Extract content under a ### heading until the next ### or ** field."""
    pattern = re.compile(
        rf"###\s+{re.escape(heading)}\s*\n(.*?)(?=\n###\s|\n\*\*数据来源\*\*|\n\*\*更新机制\*\*|\n---|\Z)",
        re.DOTALL,
    )
    m = pattern.search(text)
    if m:
        return m.group(1).strip()
    return ""


def _extract_field(text: str, field_name: str) -> str:
    """Extract a **field_name**：value line."""
    # Try: **field_name**：content (until next ** or end of line/paragraph)
    pattern = re.compile(
        rf"\*\*{re.escape(field_name)}\*\*[：:]\s*(.*?)(?=\n\n\*\*|\n---|\n##|\Z)",
        re.DOTALL,
    )
    m = pattern.search(text)
    if m:
        return m.group(1).strip()
    return ""


def import_all():
    """Parse all dimension files and insert into the database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Collect all dimensions
    all_dims = []
    md_files = sorted(
        f for f in os.listdir(V1_DIMENSIONS_DIR) if f.endswith(".md")
    )
    print(f"Found {len(md_files)} markdown files in {V1_DIMENSIONS_DIR}")

    for fname in md_files:
        filepath = os.path.join(V1_DIMENSIONS_DIR, fname)
        dims = parse_md_file(filepath)
        print(f"  {fname}: {len(dims)} dimensions")
        all_dims.extend(dims)

    print(f"\nTotal dimensions parsed: {len(all_dims)}")
    print(f"Categories: {len(set(d['category'] for d in all_dims))}")

    # Print category summary
    from collections import Counter
    cat_counts = Counter(d["category"] for d in all_dims)
    for cat in sorted(cat_counts):
        print(f"  {cat} {CATEGORY_NAMES.get(cat, '?')}: {cat_counts[cat]} dimensions")

    # Insert into database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure table exists
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    now = datetime.now().isoformat()
    inserted = 0
    for d in all_dims:
        try:
            cursor.execute(
                """INSERT OR REPLACE INTO dimensions
                   (id, name, category, category_name, description, quality_role, data_source, update_frequency, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    d["id"], d["name"], d["category"], d["category_name"],
                    d["description"], d["quality_role"],
                    d["data_source"], d["update_frequency"],
                    now, now,
                ),
            )
            inserted += 1
        except Exception as e:
            print(f"  ERROR inserting {d['id']}: {e}")

    conn.commit()
    conn.close()
    print(f"\nInserted {inserted} dimensions into {DB_PATH}")


if __name__ == "__main__":
    import_all()
