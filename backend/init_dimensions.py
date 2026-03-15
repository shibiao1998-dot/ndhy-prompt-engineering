"""Dimension initialization script.

Reads 17 markdown files from the dimensions directory,
parses each dimension, and imports them into SQLite.

Can be run repeatedly (clears and reimports).

Usage:
    python init_dimensions.py
"""

import asyncio
import json
import os
import re
import sys

# Add backend dir to path
sys.path.insert(0, os.path.dirname(__file__))

from database import get_db, init_db

# Source directory for dimension markdown files
DIMENSIONS_DIR = r"D:\code\openclaw-home\workspace\projects\prompt-engineering\dimensions"

# Optional JSON with enhanced descriptions
DESCRIPTIONS_JSON = r"D:\code\openclaw-home\workspace\projects\prompt-engineering-v2\dimension-descriptions.json"

# Category mapping from filename prefix to category info
CATEGORY_MAP = {
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


def parse_dimensions_from_file(filepath: str) -> list[dict]:
    """Parse a dimension markdown file and extract individual dimensions.

    Each dimension starts with `## XX` where XX is a dimension ID like A01, B01, etc.
    """
    filename = os.path.basename(filepath)

    # Determine category from filename
    # Filenames: A-strategy-values.md, B-user-authenticity-1.md, J01-J02.md, etc.
    category = filename[0].upper()
    category_name = CATEGORY_MAP.get(category, category)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    dimensions = []
    # Match ## <ID> <NAME> or # <ID> <NAME> patterns
    # IDs like: A01, A02, B01, J01, K01, L01 etc.
    # Handle both h1 and h2 headers: "# J01 K12教育理论库" or "## A01 战略核心方向"
    pattern = re.compile(r"^#{1,2} ([A-L]\d{2})\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))

    for i, match in enumerate(matches):
        dim_id = match.group(1)
        dim_name = match.group(2).strip()

        # Extract content until next dimension or end of file
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        dim_content = content[start:end].strip()

        # Extract data_source if present
        data_source = None
        source_match = re.search(r"\*\*数据来源\*\*[：:](.+?)(?:\n|$)", dim_content)
        if source_match:
            data_source = source_match.group(1).strip()

        # Extract update_frequency if present
        update_frequency = None
        freq_match = re.search(r"\*\*更新机制\*\*[：:](.+?)(?:\n|$)", dim_content)
        if freq_match:
            update_frequency = freq_match.group(1).strip()

        # Determine direction from content
        direction = "positive"
        name_lower = dim_name.lower()
        if any(kw in name_lower for kw in ["红线", "禁忌", "禁区", "不做"]):
            direction = "negative"
        elif any(kw in dim_content[:500] for kw in ["❌ 不能做", "禁止", "红线"]):
            if any(kw in dim_content[:500] for kw in ["✅ 可以做", "正面案例"]):
                direction = "mixed"
            else:
                direction = "negative"

        # Default priority based on category
        priority = 2  # Default: 建议
        if category == "A":
            priority = 1  # 战略 = 必须
        elif category in ("B", "D"):
            priority = 1  # 用户/场景 = 必须
        elif category in ("K", "L"):
            priority = 3  # 术语/生命周期 = 可选

        dimensions.append({
            "id": dim_id,
            "name": dim_name,
            "category": category,
            "category_name": category_name,
            "description": dim_content,
            "data_source": data_source,
            "update_frequency": update_frequency,
            "direction": direction,
            "priority": priority,
        })

    return dimensions


async def import_dimensions():
    """Main import function."""
    await init_db()

    # Collect all dimensions from files
    all_dimensions = []
    files = sorted(os.listdir(DIMENSIONS_DIR))
    print(f"发现 {len(files)} 个维度文件")

    for fname in files:
        if not fname.endswith(".md"):
            continue
        filepath = os.path.join(DIMENSIONS_DIR, fname)
        dims = parse_dimensions_from_file(filepath)
        print(f"  {fname}: 解析出 {len(dims)} 个维度")
        all_dimensions.extend(dims)

    print(f"\n共解析 {len(all_dimensions)} 个维度")

    # Load optional descriptions JSON
    descriptions = {}
    if os.path.exists(DESCRIPTIONS_JSON):
        print(f"\n发现增强描述文件: {DESCRIPTIONS_JSON}")
        with open(DESCRIPTIONS_JSON, "r", encoding="utf-8") as f:
            desc_data = json.load(f)
        if isinstance(desc_data, list):
            for item in desc_data:
                if "id" in item:
                    descriptions[item["id"]] = item
        elif isinstance(desc_data, dict):
            descriptions = desc_data
        print(f"  加载 {len(descriptions)} 个增强描述")

    # Import to database
    db = await get_db()
    try:
        # Clear existing data
        await db.execute("DELETE FROM dimensions")
        await db.commit()
        print("\n已清空旧数据")

        # Insert dimensions
        count = 0
        for dim in all_dimensions:
            dim_id = dim["id"]

            # Apply enhanced descriptions if available
            if dim_id in descriptions:
                enhanced = descriptions[dim_id]
                if "description" in enhanced and enhanced["description"]:
                    dim["description"] = enhanced["description"]
                if "direction" in enhanced and enhanced["direction"]:
                    dim["direction"] = enhanced["direction"]

            await db.execute(
                """INSERT INTO dimensions
                   (id, name, category, category_name, description,
                    data_source, update_frequency, direction, priority,
                    review_status, created_at, last_updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved', datetime('now'), datetime('now'))""",
                (
                    dim["id"],
                    dim["name"],
                    dim["category"],
                    dim["category_name"],
                    dim["description"],
                    dim["data_source"],
                    dim["update_frequency"],
                    dim["direction"],
                    dim["priority"],
                ),
            )
            count += 1

        await db.commit()
        print(f"成功导入 {count} 个维度\n")

        # Print summary by category
        cursor = await db.execute(
            """SELECT category, category_name, COUNT(*) as cnt,
                      SUM(CASE WHEN description IS NOT NULL AND description != '' THEN 1 ELSE 0 END) as filled
               FROM dimensions GROUP BY category ORDER BY category"""
        )
        rows = await cursor.fetchall()
        print("类别统计：")
        print(f"{'类别':<5} {'名称':<15} {'总数':<6} {'已填充':<6}")
        print("-" * 35)
        total = 0
        total_filled = 0
        for row in rows:
            print(f"{row['category']:<5} {row['category_name'] or '':<15} {row['cnt']:<6} {row['filled']:<6}")
            total += row["cnt"]
            total_filled += row["filled"]
        print("-" * 35)
        print(f"{'合计':<5} {'':<15} {total:<6} {total_filled:<6}")
        fill_rate = round(total_filled / total * 100, 1) if total else 0
        print(f"\n填充率: {fill_rate}%")

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(import_dimensions())
