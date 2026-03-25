"""Import 111 dimensions from markdown file into structured data.

This module parses the new 111 dimensions from docs/111 个维度.md
and provides structured data for database import.

New structure (111 dimensions, 11 categories):
- A: 战略与价值观 (8)
- B: 用户真实性 (10)
- C: 竞品与差异化 (5)
- E: 可行性与资源 (3)
- F: 历史经验与案例 (6)
- G: 标准与规范 (3)
- I: 专有知识 (9)
- J: 专有名词 (5)
- K: 项目信息 (5)
- M: 马斯洛需求层次 (25) - with 5 levels
- O: 教育内容形式 (32)

Removed: quality_role field
"""

import re
from typing import Optional

# Category name mapping
CATEGORY_NAMES = {
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

# M class level mapping (based on dimension ID ranges)
M_CLASS_LEVELS = {
    # Level 1: 生理需求 (4)
    'M01': 1, 'M02': 1, 'M03': 1, 'M04': 1,
    # Level 2: 安全需求 (5)
    'M05': 2, 'M06': 2, 'M07': 2, 'M08': 2, 'M09': 2,
    # Level 3: 社交需求 (5)
    'M10': 3, 'M11': 3, 'M12': 3, 'M13': 3, 'M14': 3,
    # Level 4: 尊重需求 (5)
    'M15': 4, 'M16': 4, 'M17': 4, 'M18': 4, 'M19': 4,
    # Level 5: 自我实现 (6)
    'M20': 5, 'M21': 5, 'M22': 5, 'M23': 5, 'M24': 5, 'M25': 5,
}

# Hardcoded 111 dimensions data from 111 个维度.md
DIMENSION_DATA = [
    # A 类：战略与价值观 (8)
    {'id': 'A01', 'name': '战略核心方向', 'category': 'A', 'category_name': '战略与价值观', 'description': 'DJ 最近 3 次会议中强调的战略重点（不超过 3 个），每个包含：原话、背景、为什么重要、时效性', 'data_source': '会议纪要（近 3 月）', 'update_frequency': '每月更新'},
    {'id': 'A02', 'name': '战略红线清单', 'category': 'A', 'category_name': '战略与价值观', 'description': '明确"不做"的方向，每条包含：红线内容、边界说明、原因、案例', 'data_source': '会议纪要、战略决策记录', 'update_frequency': '重大决策后更新'},
    {'id': 'A03', 'name': '战略演变历史', 'category': 'A', 'category_name': '战略与价值观', 'description': '过去 2 年战略调整的关键节点，每个包含：时间、原因、影响、当前是否仍有效', 'data_source': '会议纪要（按时间线整理）', 'update_frequency': '每季度复盘'},
    {'id': 'A04', 'name': '教育理念核心原则', 'category': 'A', 'category_name': '战略与价值观', 'description': 'DJ 反复强调的教育理念（如"按需学习""以学生为中心""3E 教育"），每个包含：原话、解释、正反案例', 'data_source': '会议纪要、公开演讲', 'update_frequency': '持续积累'},
    {'id': 'A05', 'name': '价值观禁忌库', 'category': 'A', 'category_name': '战略与价值观', 'description': 'DJ 明确反对的设计理念/方法，每条包含：禁忌内容、原因、原话、触犯案例', 'data_source': '会议纪要、批评记录', 'update_frequency': '持续积累'},
    {'id': 'A06', 'name': '公司使命', 'category': 'A', 'category_name': '战略与价值观', 'description': '公司的核心使命表述，包含：使命原文、使命背景、核心含义解读、使命在不同业务中的体现', 'data_source': '公司官方文档', 'update_frequency': '年度更新'},
    {'id': 'A07', 'name': '项目类型与战略定位', 'category': 'A', 'category_name': '战略与价值观', 'description': '不同项目类型（实验项目、工具项目、平台项目）在战略中的定位和优先级', 'data_source': '项目官网 + 会议纪要', 'update_frequency': '每季度更新'},
    {'id': 'A08', 'name': '业务优先级矩阵', 'category': 'A', 'category_name': '战略与价值观', 'description': '当前公司重点项目排序、资源投入级别、业务重要性', 'data_source': '项目官网 + 会议纪要', 'update_frequency': '每月更新'},

    # B 类：用户真实性 (10)
    {'id': 'B01', 'name': '用户原声库', 'category': 'B', 'category_name': '用户真实性', 'description': '用户访谈、调研的原始记录（用户原话），每条包含：原话、背景、用户信息、时间、来源', 'data_source': '应用市场评价、社交媒体、行业调研报告、客服对话、用户反馈', 'update_frequency': '实时更新，超过 6 个月标注"需验证"'},
    {'id': 'B02', 'name': '用户行为数据库', 'category': 'B', 'category_name': '用户真实性', 'description': '产品使用数据、埋点数据、关键指标变化，每条包含：数据内容、时间范围、样本量、数据源、可信度', 'data_source': '行业报告、竞品数据、数据平台', 'update_frequency': '实时更新'},
    {'id': 'B03', 'name': '用户细分维度参考库', 'category': 'B', 'category_name': '用户真实性', 'description': '如何细分用户群体的维度（年龄、学段、使用频率、能力、动机、场景），每个维度包含：定义、典型特征、行业标准', 'data_source': '历史项目总结 + 行业最佳实践 + 教育行业标准', 'update_frequency': '每季度更新'},
    {'id': 'B05', 'name': '用户痛点证据库', 'category': 'B', 'category_name': '用户真实性', 'description': '已知痛点及其证据链，每个痛点包含：痛点描述、证据来源、影响范围、紧迫性', 'data_source': '用户调研 + 数据分析 + 客服记录 + 外部报告', 'update_frequency': '实时更新'},
    {'id': 'B06', 'name': '反常识用户发现库', 'category': 'B', 'category_name': '用户真实性', 'description': '与行业常识相悖的用户行为/需求发现，每个包含：发现内容、违反了什么常识、证据、影响、适用范围', 'data_source': '用户调研、实验结果、失败复盘', 'update_frequency': '持续积累'},
    {'id': 'B07', 'name': '用户使用场景库', 'category': 'B', 'category_name': '用户真实性', 'description': '真实使用场景描述，每个场景包含：时间、地点、动机、前置条件、干扰因素、心理状态、行为序列、期望结果', 'data_source': '用户访谈、观察记录、日志分析', 'update_frequency': '持续积累'},
    {'id': 'B08', 'name': '用户决策因素库', 'category': 'B', 'category_name': '用户真实性', 'description': '用户选择/放弃产品的真实原因，每个包含：决策因素、证据、影响权重、用户原话', 'data_source': '用户访谈、流失分析、转化分析', 'update_frequency': '每季度更新'},
    {'id': 'B09', 'name': '用户语言/表达习惯库', 'category': 'B', 'category_name': '用户真实性', 'description': '目标用户群体的语言习惯、常用词汇、表达方式，每个群体包含：语言特征、案例、禁忌表达', 'data_source': '用户访谈、社交媒体分析', 'update_frequency': '每半年更新'},
    {'id': 'B10', 'name': '用户认知水平库', 'category': 'B', 'category_name': '用户真实性', 'description': '不同用户群体的认知水平、知识储备、理解能力，每个群体包含：认知特征、理解门槛、学习曲线', 'data_source': '用户测试、问卷调查', 'update_frequency': '每半年更新'},
    {'id': 'B11', 'name': '用户设备与环境信息', 'category': 'B', 'category_name': '用户真实性', 'description': '用户使用的设备类型、网络环境、物理环境，每个维度包含：分布数据、约束影响', 'data_source': '设备数据、行业报告', 'update_frequency': '每季度更新'},

    # C 类：竞品与差异化 (5)
    {'id': 'C01', 'name': '竞品信息库', 'category': 'C', 'category_name': '竞品与差异化', 'description': '主要竞品的详细信息，每个竞品包含：产品定位、核心功能、用户评价、优势、劣势、更新动态、用户规模', 'data_source': '竞品官网、应用市场、市场调研报告', 'update_frequency': '每月更新'},
    {'id': 'C02', 'name': '竞品核心优势库', 'category': 'C', 'category_name': '竞品与差异化', 'description': '竞品的核心优势（用户为什么选他们），每个包含：优势内容、证据、可复制性评估', 'data_source': '竞品分析、用户评价', 'update_frequency': '每季度更新'},
    {'id': 'C03', 'name': '竞品盲区/弱点库', 'category': 'C', 'category_name': '竞品与差异化', 'description': '竞品的弱点、用户抱怨、未满足需求，每个包含：弱点内容、证据、原因分析', 'data_source': '竞品评价、用户反馈', 'update_frequency': '每季度更新'},
    {'id': 'C04', 'name': '我方独特资源清单', 'category': 'C', 'category_name': '竞品与差异化', 'description': '竞品不具备的资源，每个包含：资源内容、独特性分析、强度评估、如何转化为产品优势', 'data_source': 'AI 从公司信息中提炼 → 人工筛查确认', 'update_frequency': '每季度更新'},
    {'id': 'C06', 'name': '竞品动态追踪记录', 'category': 'C', 'category_name': '竞品与差异化', 'description': '竞品近期的产品更新、战略调整、市场动作，每条包含：动态内容、时间、影响分析', 'data_source': '竞品监测、行业报告', 'update_frequency': '实时更新'},

    # E 类：可行性与资源 (3)
    {'id': 'E01', 'name': '资源信息查询途径', 'category': 'E', 'category_name': '可行性与资源', 'description': '如何获取资源信息：人力（HR 系统）、预算（财务系统）、工具（技术栈清单）、时间（项目排期表）；包含：查询入口、数据格式', 'data_source': '各资源管理系统', 'update_frequency': '系统变更时更新'},
    {'id': 'E03', 'name': '合作方信息库', 'category': 'E', 'category_name': '可行性与资源', 'description': '公司的合作方清单（供应商、外包商、战略伙伴），每个包含：合作方名称、提供的服务/能力、合作模式、联系方式、历史合作评价', 'data_source': '采购系统、商务合作记录', 'update_frequency': '每季度更新'},
    {'id': 'E04', 'name': '法规与合规要求清单', 'category': 'E', 'category_name': '可行性与资源', 'description': '必须遵守的法规（教育内容审查、隐私保护、数据安全），每项包含：要求内容、审批流程、周期、违规后果', 'data_source': '法务 + 行业标准', 'update_frequency': '重大政策变化时更新'},

    # F 类：历史经验与案例 (6)
    {'id': 'F01', 'name': '历史优秀设计案库', 'category': 'F', 'category_name': '历史经验与案例', 'description': '被认可为优秀的设计案，每个包含：案子内容、优秀理由、可复用点', 'data_source': '设计方法论平台（优秀标注）', 'update_frequency': '持续积累'},
    {'id': 'F02', 'name': '历史问题设计案库', 'category': 'F', 'category_name': '历史经验与案例', 'description': '有问题的设计案，每个包含：案子内容、问题类型、改进建议', 'data_source': '设计方法论平台（问题标注）+ 审核记录', 'update_frequency': '持续积累'},
    {'id': 'F03', 'name': '高频问题库', 'category': 'F', 'category_name': '历史经验与案例', 'description': '反复出现的问题，每个包含：问题描述、出现频率、原因、解决方法', 'data_source': '案子审核统计分析', 'update_frequency': '持续积累'},
    {'id': 'F04', 'name': '项目成功要素库', 'category': 'F', 'category_name': '历史经验与案例', 'description': '成功项目的关键成功要素，每个包含：成功项目、成功要素、因果分析、可复用性', 'data_source': '项目复盘系统', 'update_frequency': '持续积累'},
    {'id': 'F05', 'name': '项目失败原因库', 'category': 'F', 'category_name': '历史经验与案例', 'description': '项目失败的真实原因，每个包含：失败项目、失败原因、根因分析、教训', 'data_source': '项目复盘系统', 'update_frequency': '持续积累'},
    {'id': 'F06', 'name': '资源预估偏差库', 'category': 'F', 'category_name': '历史经验与案例', 'description': '历史项目预估 vs 实际消耗，每个包含：项目名称、预估、实际、偏差率、偏差原因', 'data_source': '项目复盘系统', 'update_frequency': '持续积累'},

    # G 类：标准与规范 (3)
    {'id': 'G01', 'name': '异常与边界情况处理标准库', 'category': 'G', 'category_name': '标准与规范', 'description': '常见异常和边界情况的标准处理方式，包含：系统异常（网络异常、权限不足、数据为空、加载失败）、边界情况（首次使用、账号异常、极端输入），每种包含：情况描述、出现概率、处理原则、标准话术、交互方式、案例', 'data_source': '平台规范 + 历史设计+QA 经验 + 用户反馈', 'update_frequency': '每半年更新'},
    {'id': 'G02', 'name': '文档标准与模板', 'category': 'G', 'category_name': '标准与规范', 'description': '各类产出物的标准格式（核心价值、目标用户、原始需求、设计案、原型），每种包含：标准结构、必需章节、格式要求、案例', 'data_source': '历史优秀文档', 'update_frequency': '模板优化时更新'},
    {'id': 'G04', 'name': '命名规范库', 'category': 'G', 'category_name': '标准与规范', 'description': '设计案、文件、图层、变量的命名规范，每类包含：命名规则、案例、常见错误', 'data_source': '命名规范', 'update_frequency': '规范更新时同步'},

    # I 类：专有知识 (9)
    {'id': 'I01', 'name': 'K12 教育理论库', 'category': 'I', 'category_name': '专有知识', 'description': '相关教育理论（建构主义、支架理论、最近发展区），每个包含：理论内容、如何应用到设计、案例', 'data_source': '教育专家、教育文献', 'update_frequency': '新理论出现时更新'},
    {'id': 'I02', 'name': '学习心理学知识库', 'category': 'I', 'category_name': '专有知识', 'description': '学习相关的心理学知识（认知负荷、动机理论、记忆规律），每个包含：知识内容、设计启示、案例', 'data_source': '心理学文献、专家', 'update_frequency': '新研究时更新'},
    {'id': 'I03', 'name': '教学设计原则库', 'category': 'I', 'category_name': '专有知识', 'description': '教学设计的原则和方法（ADDIE 模型、教学目标分类、评价设计），每个包含：原则内容、应用方法、案例', 'data_source': '教学设计理论', 'update_frequency': '新方法时更新'},
    {'id': 'I04', 'name': '学科知识库', 'category': 'I', 'category_name': '专有知识', 'description': '相关学科的专业知识（概念、原理、常见误区），每个包含：知识内容、教学难点、设计启示', 'data_source': '学科专家、教材', 'update_frequency': '按需更新'},
    {'id': 'I05', 'name': '实验教学方法库', 'category': 'I', 'category_name': '专有知识', 'description': '实验教学的方法和原则（探究式学习、实验设计、安全要求），每个包含：方法内容、适用场景、案例', 'data_source': '实验教学专家', 'update_frequency': '新方法时更新'},
    {'id': 'I06', 'name': '教育政策与标准库', 'category': 'I', 'category_name': '专有知识', 'description': '相关教育政策、课程标准、考试要求，每项包含：政策内容、影响、设计启示', 'data_source': '教育部门文件', 'update_frequency': '政策变化时更新'},
    {'id': 'I07', 'name': '教育技术应用研究库', 'category': 'I', 'category_name': '专有知识', 'description': '教育技术应用的研究成果（有效性研究、最佳实践），每个包含：研究内容、结论、设计启示', 'data_source': '教育技术文献', 'update_frequency': '新研究时更新'},
    {'id': 'I08', 'name': '教育行业特殊需求库', 'category': 'I', 'category_name': '专有知识', 'description': '教育行业的特殊需求（教师需求、学校需求、监管要求），每个包含：需求内容、来源、设计影响', 'data_source': '行业调研、客户反馈', 'update_frequency': '每季度更新'},
    {'id': 'I09', 'name': '学习目标库', 'category': 'I', 'category_name': '专有知识', 'description': '公司建立的学习目标体系，包含：各学段各学科的学习目标、目标分类、目标描述标准、目标与教学设计的关联、优秀案例', 'data_source': '公司学习目标库平台', 'update_frequency': '学习目标库更新时同步'},

    # J 类：专有名词 (5)
    {'id': 'J01', 'name': '公司核心术语库', 'category': 'J', 'category_name': '专有名词', 'description': '公司内部定义的术语（如"核心价值""衍生价值""解决方案"），每个包含：标准定义、DJ 原话解释、正反案例、常见误用', 'data_source': '会议纪要、官方文档', 'update_frequency': '新术语出现时更新'},
    {'id': 'J02', 'name': '项目专有名词库', 'category': 'J', 'category_name': '专有名词', 'description': '各项目内部定义的术语（如"颗粒""套路""器材资源"），每个包含：项目名称、术语定义、使用场景、案例', 'data_source': '项目文档、团队沉淀', 'update_frequency': '按项目更新'},
    {'id': 'J03', 'name': '设计方法论术语库', 'category': 'J', 'category_name': '专有名词', 'description': '设计方法论中的标准术语（如"目标用户拆分""竞品整合""情景罗列"），每个包含：标准定义、操作含义、产出物要求', 'data_source': '设计方法论平台', 'update_frequency': '方法论更新时同步'},
    {'id': 'J04', 'name': '教育领域标准术语库', 'category': 'J', 'category_name': '专有名词', 'description': '教育行业的标准术语（如"学习目标分类""教学评价""形成性评价"），每个包含：标准定义、教育学依据、使用场景', 'data_source': '教育学文献、课程标准', 'update_frequency': '每年更新'},
    {'id': 'J05', 'name': '技术术语标准库', 'category': 'J', 'category_name': '专有名词', 'description': '技术相关的标准术语（如"前端""后端""API""3D 渲染"），每个包含：标准定义、技术含义、设计影响', 'data_source': '技术文档', 'update_frequency': '技术栈变化时更新'},

    # K 类：项目信息 (5)
    {'id': 'K01', 'name': '项目备选池信息', 'category': 'K', 'category_name': '项目信息', 'description': '备选池中的项目清单，每个项目包含：项目名称、初衷、价值、可行性前置分析、当前状态', 'data_source': '项目管理系统', 'update_frequency': '实时更新'},
    {'id': 'K02', 'name': '项目前置分析信息', 'category': 'K', 'category_name': '项目信息', 'description': '各项目的前置分析内容，每个包含：原始需求、项目初衷、项目定义、项目价值分析、可行性分析', 'data_source': '项目管理系统', 'update_frequency': '项目启动时更新'},
    {'id': 'K03', 'name': '项目立项评估信息', 'category': 'K', 'category_name': '项目信息', 'description': '各项目的立项评估结果，每个包含：评估结论、必要性评分、可行性评分、战略对齐度、资源匹配度', 'data_source': '项目管理系统', 'update_frequency': '立项时更新'},
    {'id': 'K04', 'name': '项目理想化状态', 'category': 'K', 'category_name': '项目信息', 'description': '各项目的理想化状态定义，每个包含：项目名称、理想状态描述、实现路径、关键里程碑', 'data_source': '项目规划文档', 'update_frequency': '项目规划时更新'},
    {'id': 'K05', 'name': '项目目标体系', 'category': 'K', 'category_name': '项目信息', 'description': '各项目的目标层级（理想化状态→中短期目标→阶段结项目标→月度计划→周版本），每个层级包含：目标内容、对齐关系、完成标准', 'data_source': '项目管理系统', 'update_frequency': '每周/每月更新'},

    # M 类：马斯洛需求层次 (25) - Level 1: 生理需求 (4)
    {'id': 'M01', 'name': '基本生存与身体舒适', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 1, 'description': '确保学习过程中的基本生理需求得到满足。包含：饮食满足、睡眠质量、身体舒适、温度适宜、呼吸与空气、疼痛消除、排泄便利、卫生清洁。教育场景应用：合理的课时安排（避免连续 3 小时以上）、提醒休息和活动、界面设计考虑视觉舒适度', 'data_source': 'DJ 经验：长时间学习需要考虑疲劳因素，避免认知过载', 'update_frequency': '持续积累'},
    {'id': 'M02', 'name': '运动与活动需求', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 1, 'description': '在学习中融入适当的活动元素。包含：运动与活动、恢复与休息、能量补充、即时满足。教育场景应用：学习过程中穿插互动环节、鼓励站立走动动手操作、避免完全静态的学习体验', 'data_source': 'DJ 经验：教育不应该是完全静态的', 'update_frequency': '持续积累'},
    {'id': 'M03', 'name': '感官与认知舒适', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 1, 'description': '优化信息呈现方式，减少认知负担。包含：感官刺激（视觉、听觉、触觉）、认知的流畅度、信息密度适配、视觉呼吸感、阅读/浏览的物理舒适度（字号、行距、对比度、亮度）。教育场景应用：界面设计（合理的信息密度、清晰的层级）、内容呈现（分段、分屏，避免信息过载）、多感官学习（图文结合、视听结合）', 'data_source': '专家经验：多感官学习效果更好，但不要过度刺激', 'update_frequency': '持续积累'},
    {'id': 'M04', 'name': '便利与即时性', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 1, 'description': '降低学习过程中的摩擦和阻碍。包含：即时满足（需求被快速响应）、便利可及性（功能资源容易找到和使用）、减少摩擦（减少不必要的步骤等待切换）。教育场景应用：一键式操作减少复杂流程、快速加载减少等待时间、常用功能易于触达', 'data_source': '用户体验原则：降低使用成本提升效率', 'update_frequency': '持续积累'},

    # M 类 Level 2: 安全需求 (5)
    {'id': 'M05', 'name': '物理与信息安全', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 2, 'description': '保护用户的基本安全不受威胁。包含：人身安全（内容不引发危险行为如化学实验的安全提示）、信息安全（数据不被泄露或滥用）、隐私保护（学习数据个人信息的隐私）、法律保护（内容合规不触犯法律）、资产保全（付费内容的权益保护）。教育场景应用：实验类内容必须包含安全提示、明确的隐私政策和数据使用说明、家长监控功能的边界设定（既要监督又要尊重隐私）', 'data_source': '用户反馈：学生担心学习数据被过度监控', 'update_frequency': '持续积累'},
    {'id': 'M06', 'name': '心理安全感', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 2, 'description': '营造不被批评嘲笑的学习氛围。包含：心理安全感（不怕犯错不怕提问）、情绪稳定性（学习过程中情绪不被负面刺激）、环境可控感（用户感觉可以掌控学习节奏）。教育场景应用：回答错误不被批评、实验失败不被责怪、犯错是学习的一部分、语言表述避免"你错了""你不行"等否定式表达', 'data_source': 'DJ 经验：设计化学实验场景时强调"让学生被尊重"，实际应用中产生了显著效果', 'update_frequency': '持续积累'},
    {'id': 'M07', 'name': '认知安全', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 2, 'description': '确保用户不会因为"看不懂"而产生挫败感。包含：认知安全感（不怕"我看不懂"）、失败容错感（可以回头可以重来有后悔药）、降低试错成本（鼓励尝试而非惩罚失败）。教育场景应用：提供"重新学习"或"回顾"功能、不设置不可逆的惩罚机制、难度阶梯设计合理避免突然的高难度', 'data_source': '专家经验：学生需要知道"我在学什么""学到哪里了"', 'update_frequency': '持续积累'},
    {'id': 'M08', 'name': '可预期性', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 2, 'description': '让用户对学习过程和结果有清晰的预期。包含：可预期性（清晰的学习路径和目标）、结构可预期性（知道自己在哪下一步是什么）、未来确定性（明确的学习计划和进度）、秩序与规则（一致的交互规则和评价标准）。教育场景应用：明确的学习目标和路径图、清晰的进度指示、一致的操作逻辑和反馈方式、透明的评价标准', 'data_source': '用户体验原则：减少不确定性提供清晰预期', 'update_frequency': '持续积累'},
    {'id': 'M09', 'name': '权威与信任', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 2, 'description': '内容来源让用户放心信任。包含：权威可信度（内容来源让我放心）、专业背书（教师专家机构认证）、风险规避（避免错误信息不当内容）。教育场景应用：标注内容来源（如：名师讲解教材同步）、展示资质认证、定期更新确保内容准确性', 'data_source': '信任建立原则：透明的信息来源和专业背书', 'update_frequency': '持续积累'},

    # M 类 Level 3: 社交需求 (5)
    {'id': 'M10', 'name': '归属与认同', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 3, 'description': '让用户感觉"我是这个群体的一员"。包含：归属感（我是这个班级/社群的一员）、被接纳（我的存在被认可）、社群认同（我认同这个群体的价值观）、共同价值观（与群体成员有共同的追求）、排他性圈子（这是"我们"的圈子）。教育场景应用：班级荣誉感（班级排名集体成就）、学习社群（学习小组同学圈）、身份标识（班级徽章成员身份）', 'data_source': '专家经验：班级归属感是重要的学习动力', 'update_frequency': '持续积累'},
    {'id': 'M11', 'name': '情感连接', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 3, 'description': '建立深层次的情感纽带。包含：亲密关系（与同学老师的亲密感）、情感连接（情感上的相互理解和支持）、消除孤独感（不孤单的学习体验）、友谊维护（维持和深化友谊）、家庭连结（学习成果与家庭的连接）。教育场景应用：AI 的陪伴感设计、虚拟角色的情感连接、与同学的情感互动机制、学习成果可以分享给家人', 'data_source': '用户反馈：学生希望学习过程中有情感支持和陪伴', 'update_frequency': '持续积累'},
    {'id': 'M12', 'name': '协作与互动', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 3, 'description': '在学习中产生互动和协作。包含：协作互助（共同完成任务互相帮助）、社交互动（交流讨论分享）、共同体验（一起经历某个学习过程）、被需要感（我能帮助别人我有价值）。教育场景应用：小组学习任务、讨论区问答区、互助解答、协作式游戏或项目', 'data_source': 'DJ 经验：合作学习需要明确每个人的贡献', 'update_frequency': '持续积累'},
    {'id': 'M13', 'name': '分享与传播', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 3, 'description': '让用户愿意分享学习成果和体验。包含：分享与传播（将学习成果分享给他人）、共鸣与理解（分享后得到他人的共鸣）、社交货币（值得炫耀值得传播的内容）。教育场景应用：学习成果可视化（证书作品）、一键分享功能、社交平台适配', 'data_source': '社交传播原则：提供值得分享的内容和便利的分享方式', 'update_frequency': '持续积累'},
    {'id': 'M14', 'name': '陪伴感', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 3, 'description': 'AI/虚拟角色提供的情感陪伴。包含：AI 的陪伴感（不孤单的学习体验）、虚拟角色的情感连接（角色的性格语言风格情感反馈）、长期关系（AI"记得"用户有持续的互动）。教育场景应用：AI 助手的人格化设计、情感化的语言表达、持续的关怀和鼓励', 'data_source': 'DJ 核心观点（会议原话）："AI 员工上，我们都说要有陪伴感...正常情况，谁会讲这个话"。这是公司特定的观察方式，是差异化来源', 'update_frequency': '持续积累'},

    # M 类 Level 4: 尊重需求 (5)
    {'id': 'M15', 'name': '社会认可与地位', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 4, 'description': '获得他人的认可和社会地位。包含：社会认可（被外界如老师家长同学认可）、地位象征（排名等级称号）、荣誉感（获得荣誉的自豪感）、声誉管理（维护自己的声誉）、排名与头衔（榜单称号头衔）。教育场景应用：排行榜（需慎用避免过度竞争）、荣誉称号（如"学习之星"）、公开表彰。注意事项：DJ 价值观中反对过度的排名竞争需平衡', 'data_source': 'DJ 价值观：避免过度竞争保持健康的激励方式', 'update_frequency': '持续积累'},
    {'id': 'M16', 'name': '能力与自信', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 4, 'description': '展示能力建立自信。包含：自信心（相信自己能做到）、能力展示（有机会展示自己的能力）、专业威信（在某个领域的专业形象）、独立自主（自己做决策自己解决问题）、竞争胜出（在竞争中获胜）。教育场景应用：能力徽章（如"化学实验达人"）、展示作品的平台、独立完成任务的机会、难度挑战（可选）', 'data_source': '自信建立原则：通过真实的能力提升建立自信而非虚假鼓励', 'update_frequency': '持续积累'},
    {'id': 'M17', 'name': '被看见与认可', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 4, 'description': '自己的努力和进步被看到。包含：被看见感（我的存在我的努力被注意到）、被尊重感（我的意见选择被尊重）、被及时认可（努力后立即得到反馈）、他人评价（来自他人的正面评价）、自我评价（自己对自己的认可）。教育场景应用：课堂发言被认可、作业被同学参考点赞、知识分享获得赞赏、即时的正向反馈', 'data_source': 'DJ 经验：教育应该尊重学生的选择权。用户反馈：学生希望自己的优势被看到', 'update_frequency': '持续积累'},
    {'id': 'M18', 'name': '成就可视化', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 4, 'description': '将成就以可见的形式展现。包含：勋章与徽章（收集成就勋章）、里程碑庆祝（重要节点的庆祝仪式）、成就墙（展示所有成就的空间）。教育场景应用：徽章系统、里程碑动画（如"完成第 10 个实验"）、成就展示页', 'data_source': '游戏化设计原则：将无形成就转化为可见可收集的物品', 'update_frequency': '持续积累'},
    {'id': 'M19', 'name': '因何种特质被尊重', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 4, 'description': '理解不同的尊重来源多元价值观。包含：因能力被尊重（学习能力强）、因才华被尊重（某方面有天赋）、因幽默被尊重（性格特点）、因善良被尊重（道德品质）、因坚持被尊重（意志品质）。教育场景应用：多维度的评价体系（不只是成绩）、不同特质的认可机制、避免单一价值观', 'data_source': 'DJ 原话（会议纪要）："尊重的最下面，很细的尊重...什么尊重？他觉得我有钱，有能力，还是很幽默"', 'update_frequency': '持续积累'},

    # M 类 Level 5: 自我实现 (6)
    {'id': 'M20', 'name': '成就感', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 5, 'description': '完成任务后的满足感和成就感。包含：目标达成感、难度匹配感、阶段完成感、超越自我的感觉、付出得到回报的感觉、被及时认可的感觉。教育场景应用：明确的任务目标和完成标准、难度分级系统、里程碑设计（小目标→大目标）、即时反馈和庆祝', 'data_source': '专家经验：成长感是持续学习的核心动力', 'update_frequency': '持续积累'},
    {'id': 'M21', 'name': '创造力释放', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 5, 'description': '有空间进行创造和表达。包含：开放性边界（有多大的自由度）、约束与自由的张力（在规则内的创造空间）、原创空间的大小（可以创造多少独特内容）、表达媒介的多样性（文字图画视频实物等多种表达方式）。教育场景应用：开放式作业（不是唯一标准答案）、创作工具（画板编辑器）、个性化输出（每个人的作品都不同）', 'data_source': 'DJ 经验：给学生创造的空间，而不是只是接受知识', 'update_frequency': '持续积累'},
    {'id': 'M22', 'name': '成长与精进', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 5, 'description': '看到自己的进步和成长。包含：个人成长（能力认知视野的提升）、技能精进（某项技能越来越熟练）、潜能探索（发现自己未知的潜力）、未知边界的可见性（知道自己还有多大成长空间）、自我发现的密度（不断发现新的自己）。教育场景应用：成长轨迹可视化（学习曲线）、技能树系统、能力雷达图、"你比上周进步了 X%"', 'data_source': '专家经验：成长感与进步可见是持续学习的核心动力', 'update_frequency': '持续积累'},
    {'id': 'M23', 'name': '意义与使命', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 5, 'description': '学习有更高的意义和价值。包含：意义感（学习的意义是什么）、使命感（我在完成一个重要的使命）、理想实现（向着理想前进）、影响他人（我的学习可以帮助别人）、留下遗产（创造有长期价值的东西）、内在一致性（学习内容与我的价值观一致）。教育场景应用：明确学习的意义（而不只是"考试要考"）、知识如何改变世界的案例、学习成果可以帮助他人（如制作学习资料分享）、长期项目（如"我的 XX 研究"）', 'data_source': 'DJ 教育理念：学习应该有意义，而不只是为了考试', 'update_frequency': '持续积累'},
    {'id': 'M24', 'name': '心流与巅峰体验', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 5, 'description': '全身心投入的沉浸体验。包含：心流体验（完全专注忘记时间）、巅峰体验（特别美好难忘的学习瞬间）、审美体验（内容本身的美感）、审美震撼（内容本身的美让人停下来）。教育场景应用：沉浸式学习设计、干扰最小化、难度与能力匹配（心流的关键）、美的内容呈现', 'data_source': '心流理论：当挑战与能力匹配时最容易进入心流状态', 'update_frequency': '持续积累'},
    {'id': 'M25', 'name': '智识与探索', 'category': 'M', 'category_name': '马斯洛需求层次', 'level': 5, 'description': '满足好奇心探索未知。包含：智识满足（获得新知识的满足感）、好奇心驱动（因为好奇而主动探索）、叙事代入感（我成为了故事里的视角）、惊喜感（超出预期的发现）、未完成的张力（想继续探索的冲动）。教育场景应用：设置悬念和疑问、彩蛋和隐藏内容、开放式探索、故事化的知识呈现、"未完待续"的设计', 'data_source': '学习动机原理：好奇心是最强大的内在学习动机', 'update_frequency': '持续积累'},

    # O 类：教育内容形式 (32)
    {'id': 'O01', 'name': '三国武将技能卡', 'category': 'O', 'category_name': '教育内容形式', 'description': '借用三国杀、武将卡的属性体系，将知识点包装在武将的"成名技"中，通过牌局博弈展示逻辑强弱', 'data_source': 'AI 表演项目 (https://aic-service.sdp.101.com/showcase/case1/index.html)', 'update_frequency': '定期同步'},
    {'id': 'O02', 'name': '漫威英雄', 'category': 'O', 'category_name': '教育内容形式', 'description': '赋予特定的"超能力"和"装备"，通过解决灭霸式的"毁灭性危机"体现知识的实用价值', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O03', 'name': '知识 UP 主首秀', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"虚拟流量"和"弹幕互动"模型，设定为需要挣扎涨粉、应对"杠精"弹幕的过程', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O04', 'name': '知识体育竞技', 'category': 'O', 'category_name': '教育内容形式', 'description': '借用竞技项目规则，将知识点的对抗性包装为一场输赢较量', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O05', 'name': '知识侦探档案', 'category': 'O', 'category_name': '教育内容形式', 'description': '包装在"破案"叙事中，现象当案发现场，变量当嫌疑人，通过逻辑取证', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O06', 'name': '知识军事演习', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"战术指挥"和"兵棋推演"，包装成联合行动，知识点当成母舰、导弹或核心密码', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O07', 'name': '知识医疗门诊', 'category': 'O', 'category_name': '教育内容形式', 'description': '通过"诊断"和"开方"的专业模型，包装成精准的外科手术，知识点当成特效药或微创技术', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O08', 'name': '知识吐槽大会', 'category': 'O', 'category_name': '教育内容形式', 'description': '模拟针对性极强的"吐槽"现场，将易错点、伪逻辑作为槽点猛烈攻击，最终由知识真身反杀', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O09', 'name': '知识哑剧挑战', 'category': 'O', 'category_name': '教育内容形式', 'description': '通过"禁言"这一强约束机制，强迫观察知识点的物理运动轨迹，用肢体语言解构逻辑', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O10', 'name': '知识学习日志', 'category': 'O', 'category_name': '教育内容形式', 'description': '通过"第一人称成长路线"，包装成笨拙但努力的个体的闯关笔记，利用"成长感"抵消知识威压', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O11', 'name': '知识宗教仪式', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"仪式感"和"神圣感"，将知识点传递包装成一次洗礼或觉醒', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O12', 'name': '知识家居家装', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"室内设计"和"家居搭建"的结构感，将知识点包装成软装、硬装和水电管线', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O13', 'name': '知识播客电台', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"纯听觉"或"模拟电台现场"，将知识点包装在松弛的对谈中，用比喻和金句透传逻辑', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O14', 'name': '知识改编神曲', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用经典旋律的"听觉成瘾性"，将知识点填入歌词，通过声韵、节奏强行写入长期记忆', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O15', 'name': '知识新闻直播间', 'category': 'O', 'category_name': '教育内容形式', 'description': '模拟专业新闻联播或突发事件直播，将知识点的发现、实验、应用作为"全球重大新闻"报道', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O16', 'name': '知识旅行游记', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"探险"和"打卡"的叙事模型，包装成跨越奇特地理景观的自驾游', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O17', 'name': '知识时装 T 台', 'category': 'O', 'category_name': '教育内容形式', 'description': '包装成身着不同设计语言的"时装系列"，利用走秀的节奏感、面料质感和剪裁感讲解逻辑结构', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O18', 'name': '知识梗图制造机', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用互联网 Meme 的非对称表达力，将知识点的反差、冲突塞入经典梗图模板，实现"秒懂"效果', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O19', 'name': '知识演说家', 'category': 'O', 'category_name': '教育内容形式', 'description': '借用 TED 或乔布斯发布会式的演讲张力，包装在"改变世界"的演讲叙事中', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O20', 'name': '知识爱情罗曼史', 'category': 'O', 'category_name': '教育内容形式', 'description': '将两个知识点包装成一对拉扯感十足的恋人，利用相遇、相知、冲突、契约讲解逻辑耦合', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O21', 'name': '知识科幻编年史', 'category': 'O', 'category_name': '教育内容形式', 'description': '将知识点的诞生、演化和未来应用设定为"文明发展史"，利用宏大的时间尺度展示逻辑的力量', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O22', 'name': '知识穿越书信', 'category': 'O', 'category_name': '教育内容形式', 'description': '包装成跨越时空的"逆天改命"情报，利用时空信息差产生的"优越感"或"遗憾感"驱动学习', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O23', 'name': '知识童话新编', 'category': 'O', 'category_name': '教育内容形式', 'description': '借用经典童话的叙事框架，将知识点替换为任务奖励或关键变身道具', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O24', 'name': '知识美食菜谱', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"烹饪"极强的因果逻辑和步骤感，模拟为一道色香味俱全的菜肴制作', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O25', 'name': '知识脱口秀', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"吐槽"和"反差梗"，通过自嘲式叙事和冒犯性比喻，让知识在笑声中被动植入', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O26', 'name': '知识荒诞剧场', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"超现实主义"和"逻辑极限"，包装成荒诞不经的戏剧，通过物理法则的"失灵"反衬真理', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O27', 'name': '知识说唱创作', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用 Hip-hop 的强节奏感和 Flow，将知识点的因果逻辑编写成押韵的歌词', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O28', 'name': '知识配音秀', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用经典影视片段进行重新配音，将剧中角色的博弈台词替换为知识点的博弈过程', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O29', 'name': '科学家实验日志', 'category': 'O', 'category_name': '教育内容形式', 'description': '通过"实验重现"和"容错调试"，包装成充满变数的实验室探索', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O30', 'name': '脱口秀知识剧场', 'category': 'O', 'category_name': '教育内容形式', 'description': '将学术逻辑转化为生活化的"观察式幽默"，利用段子的 Set-up 与 Punchline 完成知识的非对称交付', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O31', 'name': '蚂蚁帝国探索', 'category': 'O', 'category_name': '教育内容形式', 'description': '利用"集体主义"与"精微分工"的蚂蚁社会模型，将复杂的流程、网络架构转化为蚂蚁搬家的日常', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
    {'id': 'O32', 'name': '西游记', 'category': 'O', 'category_name': '教育内容形式', 'description': '将知识点具象化为取经路上的各路妖魔、神仙或核心关卡，借用西游记的叙事框架和角色体系', 'data_source': 'AI 表演项目', 'update_frequency': '定期同步'},
]


def parse_111_dimensions(md_file_path: str) -> list:
    """Parse the 111 dimensions from markdown file.

    This is a placeholder that returns the hardcoded DIMENSION_DATA.
    In a full implementation, this would parse the markdown file.
    """
    # TODO: Implement markdown parsing if needed
    # For now, return hardcoded data which is more reliable
    return DIMENSION_DATA.copy()


def get_m_class_level(dimension_id: str) -> Optional[int]:
    """Get the level for M class dimensions."""
    return M_CLASS_LEVELS.get(dimension_id)


if __name__ == '__main__':
    # Quick validation
    print(f"Total dimensions: {len(DIMENSION_DATA)}")

    from collections import Counter
    cat_counts = Counter(d['category'] for d in DIMENSION_DATA)
    print("\nCategory distribution:")
    for cat in sorted(cat_counts.keys()):
        print(f"  {cat} ({CATEGORY_NAMES[cat]}): {cat_counts[cat]}")

    # M class level distribution
    m_dims = [d for d in DIMENSION_DATA if d['category'] == 'M']
    level_counts = Counter(d.get('level') for d in m_dims)
    print("\nM class level distribution:")
    for level in sorted(level_counts.keys()):
        print(f"  Level {level}: {level_counts[level]}")
