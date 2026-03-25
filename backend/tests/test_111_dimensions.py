"""Tests for 111 dimensions data import and structure."""

import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from import_111_dimensions import parse_111_dimensions, DIMENSION_DATA


class Test111DimensionsStructure:
    """Test suite for 111 dimensions structure validation."""

    def test_total_dimensions_count(self):
        """Test that total dimensions count is 111."""
        assert len(DIMENSION_DATA) == 111, f"Expected 111 dimensions, got {len(DIMENSION_DATA)}"

    def test_categories_count(self):
        """Test that there are 11 categories."""
        categories = set(d['category'] for d in DIMENSION_DATA)
        assert len(categories) == 11, f"Expected 11 categories, got {len(categories)}"

    def test_category_distribution(self):
        """Test dimension distribution across categories matches specification."""
        from collections import Counter
        cat_counts = Counter(d['category'] for d in DIMENSION_DATA)

        # Expected counts from 111 个维度.md
        expected_counts = {
            'A': 8,   # 战略与价值观
            'B': 10,  # 用户真实性
            'C': 5,   # 竞品与差异化
            'E': 3,   # 可行性与资源
            'F': 6,   # 历史经验与案例
            'G': 3,   # 标准与规范
            'I': 9,   # 专有知识
            'J': 5,   # 专有名词
            'K': 5,   # 项目信息
            'M': 25,  # 马斯洛需求层次
            'O': 32,  # 教育内容形式
        }

        for cat, expected in expected_counts.items():
            actual = cat_counts.get(cat, 0)
            assert actual == expected, f"Category {cat}: expected {expected}, got {actual}"

    def test_m_class_levels(self):
        """Test M class dimensions have correct level assignments."""
        m_dims = [d for d in DIMENSION_DATA if d['category'] == 'M']

        # Level 1: M01-M04 (4 dimensions)
        level1 = [d for d in m_dims if d.get('level') == 1]
        assert len(level1) == 4, f"Level 1: expected 4, got {len(level1)}"

        # Level 2: M05-M09 (5 dimensions)
        level2 = [d for d in m_dims if d.get('level') == 2]
        assert len(level2) == 5, f"Level 2: expected 5, got {len(level2)}"

        # Level 3: M10-M14 (5 dimensions)
        level3 = [d for d in m_dims if d.get('level') == 3]
        assert len(level3) == 5, f"Level 3: expected 5, got {len(level3)}"

        # Level 4: M15-M19 (5 dimensions)
        level4 = [d for d in m_dims if d.get('level') == 4]
        assert len(level4) == 5, f"Level 4: expected 5, got {len(level4)}"

        # Level 5: M20-M25 (6 dimensions)
        level5 = [d for d in m_dims if d.get('level') == 5]
        assert len(level5) == 6, f"Level 5: expected 6, got {len(level5)}"

    def test_dimension_fields(self):
        """Test each dimension has required fields."""
        required_fields = ['id', 'name', 'category', 'category_name', 'description', 'data_source', 'update_frequency']

        for dim in DIMENSION_DATA:
            for field in required_fields:
                assert field in dim, f"Dimension {dim['id']} missing field: {field}"

    def test_no_quality_role_field(self):
        """Test that quality_role field is NOT present (removed in v2)."""
        for dim in DIMENSION_DATA:
            assert 'quality_role' not in dim, f"Dimension {dim['id']} should not have quality_role field"

    def test_dimension_ids_format(self):
        """Test dimension IDs follow the format: Letter + 2 digits."""
        import re
        pattern = re.compile(r'^[A-Z]\d{2}$')

        for dim in DIMENSION_DATA:
            assert pattern.match(dim['id']), f"Invalid dimension ID format: {dim['id']}"

    def test_category_names(self):
        """Test category names match specification."""
        expected_names = {
            'A': '战略与价值观',
            'B': '用户真实性',
            'C': '竞品与差异化',
            'E': '可行性与资源',
            'F': '历史经验与案例',
            'G': '标准与规范',
            'I': '专有知识',
            'J': '专有名词',
            'K': '项目信息',
            'M': '马斯洛需求层次',
            'O': '教育内容形式',
        }

        actual_names = {d['category']: d['category_name'] for d in DIMENSION_DATA}

        for cat, expected_name in expected_names.items():
            actual_name = actual_names.get(cat)
            assert actual_name == expected_name, f"Category {cat}: expected '{expected_name}', got '{actual_name}'"


class TestDimensionParsing:
    """Test suite for dimension parsing from markdown."""

    def test_parse_markdown_file(self):
        """Test parsing the 111 dimensions markdown file."""
        docs_dir = r"D:\code\openclaw-home\workspace\projects\prompt-engineering-v2\docs"
        md_file = os.path.join(docs_dir, "111 个维度.md")

        dimensions = parse_111_dimensions(md_file)

        assert len(dimensions) == 111
        assert all('id' in d for d in dimensions)
        assert all('name' in d for d in dimensions)
        assert all('category' in d for d in dimensions)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
