# NDHY Expert Pack 发行层设计草案 v0

更新时间：2026-03-21 16:05（Asia/Shanghai）
状态：草案 / 可进入评审
负责人：Leader

---

# 1. 文档目的

本文档用于定义 **NDHY Expert Pack** 的发行层方案。

目标不是创建一个新的“大型 agent 市场”，而是把当前已经稳定下来的：

- Leader
- 8 位固定专家
- 共享 workflow skills
- 团队角色设定资产

整理为一套：

- 可导出
- 可安装
- 可校验
- 可版本化
- 可在多运行环境复用

的 **专家发行包系统**。

---

# 2. 核心判断

## 2.1 不做什么

NDHY Expert Pack **不做**：

1. 不走“持续扩充几十上百个 agent”的路线
2. 不把运行时治理能力退化成 prompt 文本
3. 不把 orchestrator、gate、memory governance 混回单一人格文件
4. 不以某一平台专用格式作为源头资产

## 2.2 做什么

NDHY Expert Pack 要做的是：

1. 保持当前 **固定专家体系** 不变
2. 保持当前 **workflow 治理层** 不变
3. 在外部补一层 **发行适配层**
4. 让同一套专家资产支持 OpenClaw / ACP Claude 等环境复用
5. 建立 manifest、export、install、validate 的最小工程体系

---

# 3. 当前基础盘点

## 3.1 当前权威角色池

当前权威名单以 `EXPERTS.md` 为准，包含：

- Leader
- requirement-analyst
- product-definer
- technical-architect
- experience-designer
- ui-designer
- frontend-developer
- backend-developer
- testing-expert

## 3.2 当前共享 workflow skills

当前保留共享 skills：

- `delivery-orchestrator`
- `task-intake`
- `stage-gate`
- `subagent-execution`
- `verification-gate`
- `project-memory-ops`
- `skill-stocktake`
- `model-routing-policy`

## 3.3 当前专家主 skills

- `requirements-clarification`
- `product-definition`
- `architecture-design`
- `ux-flow-design`
- `ui-spec-design`
- `frontend-delivery`
- `backend-delivery`
- `testing-verification`

## 3.4 当前角色设定资产

当前团队设定资产位于：

- `team/leader/PROFILE.md`
- `team/leader/STANDARDS.md`
- `team/experts/*/PROFILE.md`
- `team/experts/*/STANDARDS.md`
- `team/ROLE-FRAMEWORK.md`
- `team/HANDOFF-MATRIX.md`
- `team/ROLE-MATRIX.md`

这意味着当前已经具备：

- 权威专家名单
- 角色设定资产
- 主 Skill
- 共享治理 Skill
- 交接矩阵

**缺的不是专家本身，而是发行层。**

---

# 4. 目标架构

NDHY Expert Pack 采用三层结构：

## 4.1 第一层：治理内核层（保持现状）

职责：

- 需求入口分诊
- 阶段推进
- 专家调度
- 子 Agent 派发协议
- 验证闭环
- 记忆治理

组成：

- Leader
- workflow skills
- MEMORY / memory 体系
- 阶段门 / 验证门规则

原则：

- 这是系统能力，不是发行能力
- 不能为适配外部工具而破坏内核边界

## 4.2 第二层：Canonical 专家资产层

职责：

- 存放平台无关的专家资产真源
- 描述每个角色的职责、边界、输入输出、交接、质量标准
- 为导出层提供稳定输入

组成：

- `team/` 里的角色设定资产
- `skills/` 里的专家主 Skill / workflow Skill
- `EXPERTS.md` 作为权威名录
- 后续新增 `expert-pack/manifest` 与导出 schema

## 4.3 第三层：发行适配层（本次新增）

职责：

- 将 canonical 资产导出为不同运行环境可识别的格式
- 安装到目标环境
- 做一致性校验和版本控制

最小目标平台：

1. OpenClaw
2. ACP Claude / Claude Code

后续可扩展平台（暂不进入 MVP）：

- Gemini CLI
- Qwen Code
- Cursor
- 其他

---

# 5. 设计原则

## 5.1 单一真源原则

所有专家资产必须以 **canonical 结构** 作为唯一真源。

禁止：

- 直接以 OpenClaw 的 `SOUL.md` 当源
- 直接以 Claude 的 agent prompt 当源
- 多平台分别手工维护多份角色定义

## 5.2 平台导出原则

每个平台的产物都视为 **构建产物**，不是人工长期维护文件。

即：

- 源在 canonical
- 平台文件由脚本导出
- 目标环境通过 install 脚本安装

## 5.3 治理与发行分离原则

- workflow gate 属于治理层
- expert persona 属于资产层
- install/export/manifest 属于发行层

任何平台适配都不得把三者重新糊成一个大 prompt。

## 5.4 固定专家优先原则

发行层服务于 **固定专家体系**，不服务于无上限扩容。

如果未来新增专家，必须满足：

- 有长期复用场景
- 无法被现有专家稳定覆盖
- 能明确输入/输出/边界
- 不破坏主航道清晰度

## 5.5 最小可用优先原则

MVP 先覆盖：

- 8 位专家
- Leader（如需要）
- 6 个核心 workflow skills
- OpenClaw
- ACP Claude

不追求首版全平台铺开。

---

# 6. Canonical 数据模型建议

## 6.1 专家元数据建议

建议为每位专家建立统一元数据文件，例如：

```yaml
id: requirements-clarification
name: 需求澄清专家
emoji: "🎯"
role: 需求澄清
owner: NDHY AI Team
stage: 需求澄清
enabled: true

mission: 把模糊输入澄清为可进入产品定义阶段的正式需求说明

in_scope:
  - 目标澄清
  - 范围边界
  - 优先级确认
  - 约束识别
  - 成功标准确认

out_of_scope:
  - 产品方案定稿
  - 技术架构设计
  - UI 设计
  - 具体开发实现

inputs:
  - 老板原始输入
  - 背景上下文
  - 已知限制

outputs:
  - 结构化需求说明
  - 待确认问题列表
  - 是否进入产品定义阶段的判断

handoff_to:
  - product-definition

upstream:
  - leader

downstream:
  - product-definition

primary_skill: requirements-clarification
profile_path: team/experts/requirement-analyst/PROFILE.md
standards_path: team/experts/requirement-analyst/STANDARDS.md

quality_bar:
  - 目标明确
  - 范围边界明确
  - 约束明确
  - 成功标准明确

voice:
  - 中文
  - 直接
  - 结构化
```

## 6.2 workflow skill 元数据建议

建议也为共享 workflow skills 建 manifest，例如：

```yaml
id: stage-gate
name: 阶段门控
category: workflow
enabled: true
purpose: 定义各阶段进入条件、输出要求、打回规则和交接要求
scope:
  - 阶段推进判断
  - 阶段验收
  - 阶段打回
not_scope:
  - 直接替代专家完成专业产出
entry_points:
  - delivery-orchestrator
  - leader
path: skills/stage-gate
```

## 6.3 总 manifest 建议

建议建立总 manifest，例如：

```yaml
version: 0.1.0
name: ndhy-expert-pack

experts:
  - requirements-clarification
  - product-definition
  - architecture-design
  - ux-flow-design
  - ui-spec-design
  - frontend-delivery
  - backend-delivery
  - testing-verification

workflow_skills:
  - delivery-orchestrator
  - task-intake
  - stage-gate
  - subagent-execution
  - verification-gate
  - project-memory-ops

export_targets:
  - openclaw
  - claude-acp
```

---

# 7. 建议目录结构

建议在 workspace 中新增独立发行层目录：

```text
expert-pack/
  manifest/
    pack.yaml
    experts/
      requirements-clarification.yaml
      product-definition.yaml
      architecture-design.yaml
      ux-flow-design.yaml
      ui-spec-design.yaml
      frontend-delivery.yaml
      backend-delivery.yaml
      testing-verification.yaml
    workflow/
      delivery-orchestrator.yaml
      task-intake.yaml
      stage-gate.yaml
      subagent-execution.yaml
      verification-gate.yaml
      project-memory-ops.yaml

  exports/
    openclaw/
    claude-acp/

  scripts/
    export-expert-pack.ps1
    install-expert-pack.ps1
    validate-expert-pack.ps1

  references/
    export-mapping-openclaw.md
    export-mapping-claude-acp.md
```

说明：

- `manifest/`：源清单与元数据
- `exports/`：导出产物
- `scripts/`：构建、安装、校验
- `references/`：映射规则说明

---

# 8. OpenClaw 导出方案

## 8.1 目标

把每位专家导出为 OpenClaw 可直接挂载/注册的 workspace 结构。

## 8.2 导出产物结构

建议每位专家导出为：

```text
exports/openclaw/<expert-id>/
  SOUL.md
  AGENTS.md
  IDENTITY.md
```

## 8.3 映射规则

### `SOUL.md`
承载：

- 角色身份
- 工作方式
- 语气
- 高层边界

来源：

- manifest 的 `name / role / mission / voice`
- `PROFILE.md` 的角色定位 / 核心职责摘要
- 必要的长期边界说明

### `AGENTS.md`
承载：

- 输入输出
- 协作方式
- 不负责什么
- 交接规则
- 质量标准
- 与主 Skill / workflow skill 的关系

来源：

- `PROFILE.md`
- `STANDARDS.md`
- manifest 的 `in_scope / out_of_scope / inputs / outputs / handoff_to / quality_bar`

### `IDENTITY.md`
承载：

- 名称
- emoji
- vibe / 简短定位

来源：

- manifest 元数据

## 8.4 关键原则

OpenClaw 导出必须采用 **显式字段映射**，禁止使用“按标题猜测拆分”的粗暴方式。

即：

- 先有 canonical 字段
- 再按规则拼接 `SOUL/AGENTS/IDENTITY`
- 不反向从长 prompt 再切片

---

# 9. ACP Claude 导出方案

## 9.1 目标

让固定专家可以在 ACP / Claude Code 环境中，以稳定角色包方式被调用。

## 9.2 导出产物建议

建议每位专家导出为：

```text
exports/claude-acp/<expert-id>/
  AGENT.md
  PROMPT.md
  ACTIVATION.md
```

## 9.3 各文件职责

### `AGENT.md`
用于保存专家完整角色定义摘要：

- 身份
- 使命
- 边界
- 输入输出
- 质量标准

### `PROMPT.md`
用于被 ACP 启动时直接加载，强调：

- 当前你是谁
- 要遵守的边界
- 要调用的主 Skill 思维方式
- 产出格式偏好

### `ACTIVATION.md`
用于给 Leader / 系统侧调用参考：

- 什么时候调用该专家
- 任务描述模板
- 最低输入包要求
- 不该如何调用

## 9.4 原则

Claude/ACP 导出层服务于“专家调用”，不是把治理层打扁。

也就是说：

- 专家 prompt 不负责替代 stage-gate
- 不负责替代 verification-gate
- 不负责替代 Leader 的调度职责

---

# 10. 脚本职责建议

## 10.1 `validate-expert-pack.ps1`

职责：

1. 校验总 manifest 是否存在
2. 校验每个专家 manifest 字段完整性
3. 校验 `profile_path` / `standards_path` / `primary_skill` 是否真实存在
4. 校验 `EXPERTS.md` 与 manifest 是否一致
5. 校验 workflow skills 是否齐全
6. 给出错误列表与阻断级别

## 10.2 `export-expert-pack.ps1`

职责：

1. 读取总 manifest
2. 读取专家 manifest
3. 读取 team/ 与 skills/ 源文件
4. 生成 OpenClaw 导出产物
5. 生成 Claude/ACP 导出产物
6. 输出导出结果摘要

## 10.3 `install-expert-pack.ps1`

职责：

1. 把 OpenClaw 导出产物安装到指定目录
2. 如有需要，调用 `openclaw agents add`
3. 把 Claude/ACP 导出产物安装到约定路径
4. 输出安装结果与后续动作提示

---

# 11. MVP 范围

## 11.1 首版纳入范围

### 专家

- requirement-analyst
- product-definer
- technical-architect
- experience-designer
- ui-designer
- frontend-developer
- backend-developer
- testing-expert

### workflow skills

先纳入 6 个核心项：

- `delivery-orchestrator`
- `task-intake`
- `stage-gate`
- `subagent-execution`
- `verification-gate`
- `project-memory-ops`

### 导出目标

- OpenClaw
- Claude/ACP

## 11.2 首版不纳入范围

- Gemini CLI
- Qwen Code
- Cursor
- 外部开源包装
- 可视化安装器
- 社区贡献机制

---

# 12. 阶段实施顺序

## Phase 1：清单层搭建

目标：建立 manifest 真源。

动作：

1. 创建 `expert-pack/manifest/pack.yaml`
2. 为 8 位专家建立元数据文件
3. 为 6 个核心 workflow skills 建元数据文件
4. 补齐字段命名规范

产出：

- 专家总清单
- workflow skill 清单
- canonical 元数据骨架

## Phase 2：校验层搭建

目标：建立最小质量门。

动作：

1. 实现 `validate-expert-pack.ps1`
2. 校验 manifest / 路径 / skill / 专家名单一致性
3. 输出校验报告

产出：

- 可重复执行的校验脚本
- 错误报告格式

## Phase 3：OpenClaw 导出层

目标：先打通最重要目标平台。

动作：

1. 定义 OpenClaw 映射规则
2. 实现 OpenClaw 导出
3. 导出 8 位专家 workspace
4. 验证导出结果可被识别

产出：

- `exports/openclaw/*`
- OpenClaw 导出规则文档

## Phase 4：Claude/ACP 导出层

目标：支持 ACP 专家包调用。

动作：

1. 定义 Claude/ACP prompt 结构
2. 实现导出脚本
3. 验证每位专家的启动包完整性

产出：

- `exports/claude-acp/*`
- Claude/ACP 导出规则文档

## Phase 5：安装层

目标：让发行包可落地。

动作：

1. 实现安装脚本
2. 增加 OpenClaw 注册步骤
3. 输出安装日志和后续提醒

产出：

- install 脚本
- 最小落地流程

---

# 13. 风险与控制

## 风险 1：canonical 设计过重

问题：
元数据字段过多，维护成本上升。

控制：
首版只保留导出必需字段，不追求“大而全 schema”。

## 风险 2：源资产与导出产物漂移

问题：
改了 team/ 或 skills/，但导出产物未更新。

控制：
- validate 检查时间戳 / 完整性
- 导出产物视为构建产物，必要时可整体重建

## 风险 3：平台适配反向污染源结构

问题：
为了适配 OpenClaw/Claude，反过来扭曲 canonical 结构。

控制：
坚持“源结构优先”，平台差异由 exporter 消化。

## 风险 4：过早扩平台

问题：
同时适配太多目标，导致 MVP 迟迟不落地。

控制：
先做 OpenClaw + ACP Claude，其他平台明确延后。

---

# 14. 成功标准

NDHY Expert Pack v0 成功的判断标准：

1. 8 位专家均有 canonical manifest
2. 6 个核心 workflow skills 均有 manifest
3. 能通过 validate 脚本检查
4. 能成功导出 OpenClaw 产物
5. 能成功导出 Claude/ACP 产物
6. 导出过程不改动现有治理内核
7. 后续新增专家或平台时，不需要重写整套结构

---

# 15. 当前结论

当前最正确的路线不是“继续造更多 agent”，而是：

**把现有固定专家体系做成一个有清单、有校验、有导出、有安装的发行层。**

一句话总结：

> 我们不是做 another `agency-agents`。
> 我们是把“固定专家 + workflow 治理 + 交付主航道”做成可分发、可复用的专家包系统。

---

# 16. 建议下一步

建议下一步直接进入 **Phase 1：清单层搭建**，先做三件事：

1. 建 `expert-pack/manifest/pack.yaml`
2. 先为 8 位专家生成第一版 manifest
3. 再补 6 个核心 workflow skills manifest

完成后，就能进入 validate 脚本开发。
