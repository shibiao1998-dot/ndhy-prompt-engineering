# NDHY AI Team 全新升级方案 v1

更新时间：2026-03-20 14:50（Asia/Shanghai）

---

## 1. 背景与目标

当前团队已经完成组织瘦身，进入一个非常适合“重新长骨架”的窗口期：

- 主航道已收口到 **软件 / Web 研发**
- 研发流程已收口为 **7 阶段闭环**
- 专家池已收口为 **8 位专家 + Leader**
- 默认检索已切到 **QMD-only**
- `workspace/skills/` 已重启设计，但当前活跃 skills 仍然很少，专家设定与专家 skill 尚未成体系

这意味着：

**现在最需要的不是继续零散加能力，而是构建一套新的团队操作系统。**

这轮升级的目标不是“多装几个 skill”，而是让团队形成：

1. 明确的角色边界
2. 清晰的阶段门控
3. 稳定的任务流转机制
4. 可复用的专家 skill 体系
5. 可审计、可治理、可迭代的团队底座

---

## 2. 当前现状判断

## 2.1 已有基础

### 组织层
- 唯一方向：软件 / Web 开发
- 唯一流程：需求澄清 → 产品定义 → 技术架构 → UX/UI 设计 → 前后端开发 → 测试（含代码审查） → 项目管理与必要记忆沉淀
- 专家池：需求分析、产品定义、技术架构、体验设计、UI 设计、前端开发、后端开发、测试、Leader

### 系统层
- 飞书是主入口
- OpenClaw 是编排核心
- ACP Claude 是主要外部编码执行引擎
- 记忆系统已形成持续上下文底座
- QMD 已成为默认检索入口

### 当前 skills 层
当前 workspace 活跃 skills 仅有：
- `retrieve`
- `content-extract`
- `search-layer`

这说明当前 skills 体系仍处于“基础设施阶段”，尚未覆盖团队运行层与专家运行层。

---

## 2.2 当前主要缺口

### 缺口 1：专家设定不完整
虽然有专家名单和职责映射，但多数专家仍缺少：
- 明确的角色边界
- 输入输出合同
- 决策权限定义
- 与上下游协作协议
- 对应的专属 skill

### 缺口 2：共享流程未 Skill 化
当前流程已被写进 `AGENTS.md` / `SOUL.md` / `MEMORY.md`，但还没有沉淀成真正可触发、可复用、可约束的共享 workflow skills。

### 缺口 3：团队运行缺少阶段门
当前已有流程顺序，但尚未形成真正的：
- 进入条件
- 输出要求
- 质量门
- 打回机制
- 交接机制

### 缺口 4：治理增强未成型
目前尚缺：
- skill 审计机制
- 安全巡检机制
- 验证闭环机制
- 模型路由规范
- 子 Agent 统一交付协议

---

## 3. 外部项目吸收结论

本轮升级参考三类外部项目：
- ECC（Everything Claude Code）
- Trellis
- Superpowers

本次不采用“整套搬运”，而采用“分层吸收”。

---

## 3.1 ECC：作为治理与增强层

ECC 最值得吸收的不是插件分发壳，而是它的增强能力。

### 建议吸收
1. **安全扫描 / AgentShield 思路**
   - 用于 OpenClaw 配置、skills、hooks、agents 的治理检查
2. **verification-loop / eval-harness 思路**
   - 用于开发完成后的验证闭环
3. **search-first / iterative-retrieval 思路**
   - 强化我们当前的 QMD-only 检索节奏
4. **cost-aware-llm-pipeline / model-route 思路**
   - 用于 AIAE + ACP 的模型路由治理
5. **skill-stocktake 思路**
   - 用于后续技能盘点与去重治理

### 不建议直接照搬
- Claude Code 插件壳
- marketplace / commands 分发层
- 大量语言 rules 全量安装
- 自动学习自动写规则的激进模式

### ECC 在我们体系中的定位
**增强器 / 治理层**

---

## 3.2 Trellis：作为团队结构层

Trellis 最强的是“repo-native 团队结构感”。

### 建议吸收
1. **spec 层思想**
   - 统一维护项目规范、团队标准、角色边界、设计准则
2. **tasks 层思想**
   - 每个需求/任务拥有自己的上下文、产物、状态与验收记录
3. **workspace / journal 层思想**
   - 记录专家和任务的连续性上下文
4. **团队共享标准思想**
   - 规则写入仓库而不是散落在个人脑中
5. **多平台工作流一致性思想**
   - 即便未来 agent/harness 变化，核心工作流不变

### 不建议直接照搬
- 整套 CLI 初始化机制
- 原目录结构一比一复制
- 多平台支持的完整分发实现

### Trellis 在我们体系中的定位
**骨架 / 结构层**

---

## 3.3 Superpowers：作为流程执行层

Superpowers 最强的是“强制流程感”。

### 建议吸收
1. **brainstorm → spec → plan → execute → review → finish 的阶段推进感**
2. **先澄清再动手的默认工作方式**
3. **按小任务拆解再执行的实施节奏**
4. **子 Agent 执行前后有 review gate 的机制**
5. **完工必须经过 finish / verify / review 的收口逻辑**

### 不建议直接照搬
- 强 TDD 原教旨的全部要求
- 完全以 coding-agent 为中心的流程语言
- 原始技能命名和实现细节

### Superpowers 在我们体系中的定位
**阶段门 / 执行纪律层**

---

## 4. 新团队体系的总设计

## 4.1 总体原则

新的 NDHY AI Team 不复制任何单一项目，而采用三层融合：

- **Trellis 做骨架**：规范、任务、记忆结构化
- **Superpowers 做流程**：阶段门清晰、先澄清后执行
- **ECC 做增强**：安全、验证、检索、路由、审计

最终形成：

**一个以 Leader 为总编排、以专家为专业执行单元、以 Skill 为行为协议、以任务包为交付容器、以记忆系统为组织连续性的 AI 产品团队。**

---

## 4.2 目标架构

### 层 1：角色层
包含：
- Leader
- 8 位专家

职责：承担专业判断、专业执行、交接与验收。

### 层 2：共享流程层
包含：
- 需求入口
- 阶段门控
- 任务编排
- 子 Agent 执行协议
- 验证闭环
- 记忆沉淀协议

职责：约束“团队怎么跑”。

### 层 3：专家 Skill 层
包含：
- 每位专家自己的主 Skill
- 配套模板 / 参考标准 / 输出合同

职责：约束“每个专家怎么干活”。

### 层 4：治理增强层
包含：
- skill 审计
- 安全扫描
- 检索规范
- 模型路由
- 质量门

职责：确保团队不会在扩张过程中重新失控。

---

## 5. 角色升级方案

## 5.1 每位角色都必须补齐的 5 个维度

所有专家与 Leader 都要重新补齐以下结构：

1. **角色定位**：你是谁，你解决什么问题
2. **职责边界**：你负责什么，不负责什么
3. **输入 / 输出**：接什么，交什么
4. **决策权限**：你能决定到哪一层
5. **协作协议**：你和上下游怎么交接

这一步完成后，专家才算真正“可调度”。

---

## 5.2 角色升级范围

### Leader
定位升级为：
- 需求入口分诊台
- 团队总调度器
- 阶段推进负责人
- 最终验收与汇报负责人
- 团队规则与记忆沉淀负责人

### 8 位专家
| 专家 | 升级重点 |
|---|---|
| 需求分析专家 | 深化澄清、范围边界、成功标准定义 |
| 产品定义专家 | 产品规则、MVP、优先级、能力拆分 |
| 技术架构专家 | 技术方案、模块边界、风险控制 |
| 体验设计专家 | 流程设计、任务路径、信息架构 |
| UI 设计专家 | 界面方案、视觉一致性、设计规范 |
| 前端开发专家 | 前端实现、交互落地、前端排障 |
| 后端开发专家 | 接口、数据模型、部署发布、后端排障 |
| 测试专家 | 验证策略、代码审查、联调验收、质量门 |

---

## 6. Skill 体系升级方案

## 6.1 先建共享 Skill，再建专家 Skill

原则：

**没有共享流程，专家 skill 越多，团队越乱。**

所以必须先做团队共用技能，再做专家私有技能。

---

## 6.2 第一批共享 Skills（优先级最高）

### 1）delivery-orchestrator
定位：Leader 总编排 Skill

用途：
- 需求分诊
- 阶段推进
- 专家调度
- 子 Agent 派发与验收
- 对老板汇报

### 2）task-intake
定位：正式需求入口

用途：
- 将老板输入转为结构化需求上下文
- 判断当前输入属于想法 / 问题 / 抱怨 / 方向 / 明确需求
- 生成进入研发流程的最小输入包

### 3）stage-gate
定位：阶段门控 Skill

用途：
- 定义每个阶段的进入条件、输出要求、打回规则、交接规则

### 4）subagent-execution
定位：子 Agent 执行协议

用途：
- 规范派发、上下文输入、执行边界、产出格式、验收回报格式

### 5）verification-gate
定位：验证闭环 Skill

用途：
- 开发完成后的检查、回归、代码审查、验收记录

### 6）project-memory-ops
定位：项目与团队记忆操作 Skill

用途：
- 定义什么值得写入记忆
- 定义写入粒度、位置和格式
- 防止记忆噪音膨胀

### 7）skill-stocktake
定位：技能盘点 Skill

用途：
- 盘点过时 skills
- 去重、归并、清理失效技能
- 检查技能边界是否清晰

### 8）model-routing-policy
定位：模型路由 Skill

用途：
- 定义规划、审查、开发、批量处理、检索总结等任务该如何选模型
- 映射到当前 AIAE + ACP 体系

---

## 6.3 第一批专家主 Skills

### Leader
- `delivery-orchestrator`

### 需求分析专家
- `requirements-clarification`

### 产品定义专家
- `product-definition`

### 技术架构专家
- `architecture-design`

### 体验设计专家
- `ux-flow-design`

### UI 设计专家
- `ui-spec-design`

### 前端开发专家
- `frontend-delivery`

### 后端开发专家
- `backend-delivery`

### 测试专家
- `verification-gate`（与共享层联动）

---

## 6.4 每个专家 Skill 的统一结构

每个专家 skill 至少包含：

1. `SKILL.md`
2. `references/`
   - 输出模板
   - 质量标准
   - 交接示例
3. 必要时 `scripts/`
   - 稳定可重复执行的检查或转换逻辑

每个专家 skill 必须明确：
- 触发条件
- 输入格式
- 输出格式
- 不处理什么
- 需要交给谁继续做

---

## 7. 团队工作流升级方案

## 7.1 新的运行原则

### 原则 1：先澄清，再执行
任何开发动作前，都必须先确认：
- 目标
- 范围
- 优先级
- 核心约束
- 成功判断方式

### 原则 2：阶段不可跳跃
每一阶段必须有明确产物，未完成不进入下一阶段。

### 原则 3：子 Agent 不是自由发挥
子 Agent 必须在：
- 明确上下文
- 明确任务边界
- 明确产出格式
- 明确验收标准
的前提下执行。

### 原则 4：完成不等于交付
任何实现完成后，都必须经过：
- 验证
- 审查
- 风险确认
- 汇报收口

### 原则 5：记忆只沉淀高价值信息
不是所有过程都写记忆，只沉淀：
- 长期有效决策
- 流程调整
- 工具链约束
- 关键风险与教训
- 对后续有复用价值的结论

---

## 7.2 阶段门设计（建议版）

| 阶段 | 负责人 | 核心输出 | 进入下一阶段条件 |
|---|---|---|---|
| 需求澄清 | Leader + 需求分析专家 | 结构化需求说明 | 目标 / 范围 / 优先级 / 约束 / 成功标准明确 |
| 产品定义 | 产品定义专家 | 产品定义文档 / MVP / 规则 | 功能范围与产品规则明确 |
| 技术架构 | 技术架构专家 | 架构方案 / 技术边界 / 风险点 | 方案可实现、风险可控 |
| UX/UI 设计 | 体验设计 + UI 设计 | 流程方案 / 界面方案 | 交互和视觉方案可落地 |
| 前后端开发 | 前端 + 后端开发 | 可运行实现 | 满足定义与设计要求 |
| 测试 / 代码审查 | 测试专家 | 验证结论 / 缺陷清单 / 审查结论 | 关键问题关闭 |
| 项目管理与记忆沉淀 | Leader | 汇报、归档、记忆沉淀 | 当前任务正式收口 |

---

## 8. 目录与资产建议

## 8.1 skills 目录建议

建议将 `workspace/skills/` 重建为：

```text
skills/
  shared/
    delivery-orchestrator/
    task-intake/
    stage-gate/
    subagent-execution/
    verification-gate/
    project-memory-ops/
    skill-stocktake/
    model-routing-policy/
  experts/
    requirements-clarification/
    product-definition/
    architecture-design/
    ux-flow-design/
    ui-spec-design/
    frontend-delivery/
    backend-delivery/
    testing-verification/
  infrastructure/
    retrieve/
    content-extract/
    search-layer/
```

说明：
- `shared/` 放团队共用工作流 skills
- `experts/` 放专家主技能
- `infrastructure/` 放底层能力型 skills

---

## 8.2 专家设定资产建议

建议新增一个统一目录存放专家设定，例如：

```text
team/
  leader/
    PROFILE.md
    STANDARDS.md
  experts/
    requirement-analyst/
      PROFILE.md
      STANDARDS.md
    product-definer/
      PROFILE.md
      STANDARDS.md
    technical-architect/
      PROFILE.md
      STANDARDS.md
    experience-designer/
      PROFILE.md
      STANDARDS.md
    ui-designer/
      PROFILE.md
      STANDARDS.md
    frontend-developer/
      PROFILE.md
      STANDARDS.md
    backend-developer/
      PROFILE.md
      STANDARDS.md
    testing-expert/
      PROFILE.md
      STANDARDS.md
```

其中：
- `PROFILE.md`：角色定位、输入输出、协作边界
- `STANDARDS.md`：专业标准、交付标准、常见检查点

---

## 9. 实施路线图

## Phase 1：团队蓝图定版

### 目标
把本方案定成团队升级总图。

### 产出
- 本文档定版
- 团队目标架构确认
- 优先级确认

### 完成标准
- 老板确认整体方向
- 确认按“共享 skill 优先，再专家 skill”推进

---

## Phase 2：角色设定升级

### 目标
重写 Leader + 8 位专家设定。

### 产出
- 9 份 `PROFILE.md`
- 9 份 `STANDARDS.md`
- 角色边界矩阵
- 上下游交接矩阵

### 完成标准
- 每位角色都能被明确触发、明确交接、明确验收

---

## Phase 3：共享 Skill 建设

### 目标
先把团队工作流 Skill 化。

### 首批建设对象
1. `delivery-orchestrator`
2. `task-intake`
3. `stage-gate`
4. `subagent-execution`
5. `verification-gate`
6. `project-memory-ops`

### 完成标准
- 团队共用流程可被统一调用
- Leader 与专家的协作方式不再依赖临场发挥

---

## Phase 4：专家 Skill 建设

### 目标
为每位专家补齐主 Skill。

### 完成标准
- 每位专家都具备稳定触发条件、标准输出与交接协议

---

## Phase 5：治理增强

### 目标
引入 ECC 风格治理增强。

### 建设对象
- skill-stocktake
- model-routing-policy
- 安全扫描方案
- 验证闭环模板

### 完成标准
- 团队具备扩张后仍可收敛的治理能力

---

## 10. 当前建议的执行顺序

建议严格按以下顺序推进：

1. **定蓝图**
2. **重写角色设定**
3. **先建共享 Skill**
4. **再建专家 Skill**
5. **最后补治理增强**

不建议的顺序：
- 先各自写专家 skill
- 先大量装新工具
- 先扩自动化 loop

原因：
**如果流程和边界没定，越快只会越乱。**

---

## 11. 本轮升级的最终目标

这轮升级完成后，NDHY AI Team 应该达到以下状态：

### 组织状态
- 角色清晰
- 分工稳定
- 边界明确
- 可调度、可交接、可验收

### 流程状态
- 阶段清晰
- 门控明确
- 质量有检查
- 子 Agent 有纪律

### 能力状态
- 共享流程 Skill 化
- 专家专业能力 Skill 化
- 检索、验证、路由、安全具备治理机制

### 管理状态
- Leader 不是临场硬扛，而是基于一套团队操作系统做编排
- 团队的优秀做法能沉淀，而不是随对话消失

---

## 12. 推荐的下一步

本蓝图之后，建议立即进入：

### 下一步 A（推荐）
**先重写 9 位角色设定**

理由：
- 这是整个团队升级的前置条件
- 角色设定定不下来，后面的 skill 都会漂

### 下一步 B
**并行起草 6 个共享 Skill 的骨架**

理由：
- 共享流程是团队协作的总线
- 越早成型，后面越稳

---

## 13. 本文档结论

本轮升级不走“多装功能”路线，而走：

**角色重建 + 流程 Skill 化 + 治理增强 + 记忆收敛**

采用策略：
- **Trellis 做骨架**
- **Superpowers 做流程**
- **ECC 做增强器**

这是当前最适合 NDHY AI Team 的升级路径。
