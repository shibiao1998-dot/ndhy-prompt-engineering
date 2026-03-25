# 当前 OpenClaw 系统全景图 + 风险清单 + 治理路线图

更新时间：2026-03-19 22:17（Asia/Shanghai）

---

## 1. 执行摘要

当前这套 OpenClaw 已经不是单纯聊天助手，而是一个 **以飞书为入口、以 OpenClaw 为编排核心、以 ACP Claude 为外部编码引擎、以记忆系统为持续上下文底座的 AI 研发工作台**。

### 当前结论
- **可用性**：高，核心链路已打通
- **组织聚焦度**：高，已收口到软件 / Web 研发主航道
- **自动化程度**：中高，已有心跳、Cron、记忆压缩、调研任务
- **治理成熟度**：中低，存在安全边界偏松、服务配置非标准、自动化资产未归整等问题

### 当前最重要判断
**现阶段最优先的不是继续加功能，而是做系统治理。**

---

## 2. 当前系统全景图

## 2.1 入口层

### 飞书（主入口）
- 渠道：Feishu
- 模式：WebSocket
- 当前状态：正常
- 当前会话：老板私聊为主

### 当前飞书能力
已启用并可调用：
- IM 消息
- Calendar 日历
- Task 任务
- Bitable 多维表格
- Doc 云文档
- Drive 文件
- Wiki
- Sheets
- OAuth

### 结论
飞书已经不只是消息入口，而是 **办公操作层**。

---

## 2.2 编排层

### OpenClaw Gateway
- 版本：`2026.3.13`
- Dashboard：`http://127.0.0.1:18789/`
- 监听：`127.0.0.1:18789`
- 部署方式：本地 Gateway
- 运行环境：Windows 10 + Node 24.13.0
- Tailscale：关闭

### 当前状态
- Gateway 运行中
- RPC probe 正常
- 本机 loopback 访问正常

### 问题
- 服务注册方式非标准
- `gateway.cmd` 启动命令存在老配置痕迹
- 状态检查明确提示：service command 不包含 `gateway` 子命令

---

## 2.3 模型层

### 默认主模型
- `aiae/gpt-5.4-2026-03-05`

### 当前心跳模型
- `aiae/qwen3.5-flash-2026-02-23`

### 当前心跳模式
- `every = 30m`
- `lightContext = true`

### 已配置模型池
#### NDHY Gateway（Anthropic）
- `claude-opus-4-6`
- `claude-sonnet-4-6`

#### AIAE Gateway（OpenAI Compatible）
- `qwen3.5-plus-2026-02-15`
- `gpt-5.4-2026-03-05`
- `gemini-3.1-pro-preview`

### 结论
模型分层已初步形成：
- 主会话：旗舰通用模型
- 心跳：便宜快速模型
- ACP 编码：Claude 体系

---

## 2.4 Agent / 专家组织层

### 当前唯一方向
- 软件 / Web 开发

### 当前唯一研发流程
- 需求澄清
- 产品定义
- 技术架构
- UX/UI 设计
- 前后端开发
- 测试（含代码审查）
- 项目管理与必要记忆沉淀

### 当前保留专家（8 位）
1. requirement-analyst
2. product-definer
3. technical-architect
4. experience-designer
5. ui-designer
6. frontend-developer
7. backend-developer
8. testing-expert

### 当前角色结构
- Leader：需求确认、调度、验收、汇报
- 专家：覆盖完整研发主链路

### 结论
组织已完成收缩，当前形态清晰、聚焦、可执行。

---

## 2.5 项目层

### 当前保留项目
- `projects/prompt-engineering-v2`

### 当前状态
- 旧项目已不再作为默认上下文
- 当前项目体系收口完成

### 结论
项目层已实现“主线聚焦”。

---

## 2.6 ACP 外部编程 Agent 层

### 当前状态
- ACP：已启用
- backend：`acpx`
- defaultAgent：`claude`
- allowedAgents：仅 `claude`
- 最大并发会话：8
- runtime TTL：30 分钟

### 当前能力
可做：
- 派发编码任务
- 独立会话执行
- 多轮追指令
- 与主会话协同

### 当前限制
- 仅开通 Claude ACP
- Codex / Gemini / Pi 尚未纳入 allowedAgents

### 结论
ACP 已可承担“外包开发引擎”角色，但多 Agent 外挂生态还没铺开。

---

## 2.7 工具层

### 当前核心工具能力
- 文件：`read / write / edit`
- 执行：`exec / process`
- 浏览器：`browser`
- Web：`web_search / web_fetch`
- 会话：`sessions_spawn / sessions_send / sessions_list / sessions_history`
- 记忆：`memory_search / memory_get`
- 图像：`image`

### 当前工具 profile
- `coding`

### 结论
当前工具面更像“工程操作台”，不是轻量聊天机器人。

---

## 2.8 记忆层

### 当前状态
- Memory 文件：524
- Chunks：3190
- vector：ready
- fts：ready
- cache：on

### 当前结构
- `MEMORY.md`：长期决策
- `memory/YYYY-MM-DD.md`：每日记忆
- `memory/retrospective/`：复盘
- `memory/_backup/`：备份

### 当前能力判断
已具备：
- 跨天延续
- 语义检索
- 工作记忆沉淀
- 组织经验累积

### 结论
记忆系统已经是“工作底座”，不是简单聊天历史。

---

## 2.9 自动化层

### 心跳
- 周期：30 分钟
- 模型：`aiae/qwen3.5-flash-2026-02-23`
- `lightContext = true`

### 当前已观察到的自动化资产
- 心跳巡查
- AI 资讯雷达
- 调研复盘与学习推动
- AI 组织进化调研
- 每日记忆压缩

### 当前自动化能力判断
已具备：
- 半主动巡查
- 定时调研
- 定时复盘
- 记忆自动维护

### 问题
- cron / heartbeat 职责边界仍不够清晰
- 自动化资产缺少统一清单与生命周期治理

---

## 3. 当前风险清单

## 3.1 P0 高风险

### R1. 飞书群策略过于开放
**现状**
- `channels.feishu.groupPolicy = "open"`

**风险**
- 任意群只要满足提及门槛，就可能接入系统
- 当前系统又暴露了 runtime / fs / coding 类能力
- prompt injection 风险被放大

**结论**
- 这是当前最重要安全风险

**建议**
- 改为 `allowlist`

---

### R2. 运行时 / 文件系统暴露过大
**现状**
- 当前工具 profile 为 `coding`
- `exec / process / read / write / edit` 暴露

**风险**
- 一旦外部入口边界失守，后果比普通聊天 Agent 严重得多

**建议**
- 明确群聊与私聊权限边界
- 对 group 场景单独降权
- 限制 runtime / fs 在群场景暴露

---

### R3. 多用户风险警报已出现
**现状**
- `openclaw status` 已提示 potential multi-user setup detected

**风险**
- 当前系统更像“个人超级助手 + 编排器”，不适合开放给弱信任多用户共享

**建议**
- 若要多人使用，必须拆 trust boundary

---

## 3.2 P1 中风险

### R4. Gateway 服务配置非标准
**现状**
- service config out of date / non-standard
- command 不包含 `gateway` 子命令

**影响**
- 后续升级、维护、排障成本上升

**建议**
- 跑一次 `openclaw doctor --repair` 级别修复方案评估

---

### R5. 自动化资产偏杂
**现状**
- 已有多个 cron / heartbeat / ACP 历史会话
- 缺少统一资产台账

**影响**
- 后续很容易出现：重复任务、遗忘任务、旧规则挂着不清理

**建议**
- 统一做自动化资产清单

---

### R6. 会话池开始膨胀
**现状**
- 当前 active sessions：68

**影响**
- 管理复杂度上升
- 需要归档和会话治理规则

**建议**
- 制定 cron / heartbeat / ACP 会话归档规则

---

## 3.3 P2 低风险但应治理

### R7. 技能体系已清空，尚未重建
**现状**
- `workspace/skills/` 已清空

**影响**
- 系统现在主要依赖平台能力和零散配置
- 缺乏一层“组织自定义技能资产”

**建议**
- 后续按最小必要原则重建技能体系

---

## 4. 当前治理目标

未来一阶段目标不是继续扩张，而是把系统治理成：

### 目标状态
1. **安全边界清晰**：谁能进、进来能做什么、群和私聊权限分离
2. **服务配置规范**：Gateway 启动、升级、排障链路干净
3. **自动化资产可见**：所有 heartbeat / cron / ACP 都有台账
4. **会话治理明确**：哪些保留、哪些归档、哪些清理
5. **系统地图固化**：新会话和未来 Agent 都能快速理解全局

---

## 5. 治理路线图

## Phase 1：安全收口（P0）

### 目标
先把高风险面收住

### 动作
1. 把 `channels.feishu.groupPolicy` 从 `open` 改为 `allowlist`
2. 评估群聊场景工具降权方案
3. 梳理 runtime / fs 暴露边界
4. 明确“仅私聊允许高权限操作”的规则

### 产出物
- 安全边界规则表
- 群/私聊权限矩阵
- 配置变更清单

---

## Phase 2：服务治理（P1）

### 目标
把 Gateway 服务链路规范化

### 动作
1. 盘点当前 Scheduled Task 注册方式
2. 修复 service command 非标准问题
3. 形成标准重启 / 诊断 / 升级 SOP
4. 验证修复后状态输出是否恢复正常

### 产出物
- Gateway 服务治理说明
- 标准操作手册

---

## Phase 3：自动化资产治理（P1）

### 目标
让 heartbeat / cron / 自动任务全量可见

### 动作
1. 列出全部 heartbeat / cron / system event 自动化项
2. 给每项标记：用途、触发方式、负责人、保留/清理
3. 拆清 heartbeat 与 cron 的职责边界
4. 删除或合并重复自动化

### 建议台账格式
| 模块 | 名称 | 作用 | 触发方式 | 当前状态 | 是否保留 | 负责人 |
|---|---|---|---|---|---|---|
| Heartbeat | 心跳巡查 | 例行巡查 | 30m | 使用中 | 保留 | Leader |
| Cron | AI 资讯雷达 | 行业扫描 | 定时 | 使用中 | 待审 | Leader |
| Cron | 调研复盘 | 学习总结 | 定时 | 使用中 | 保留 | Leader |
| Cron | 每日记忆压缩 | 历史压缩 | 定时 | 使用中 | 保留 | Leader |

---

## Phase 4：会话治理（P1）

### 目标
控制 session 池复杂度

### 动作
1. 划分主会话 / cron 会话 / heartbeat 会话 / ACP 会话
2. 建立归档与清理规则
3. 对长期无用历史会话做治理
4. 建立“新自动化必须登记”的规则

---

## Phase 5：技能与系统地图重建（P2）

### 目标
为未来扩展建立稳定基座

### 动作
1. 重建最小技能体系
2. 固化系统地图文档
3. 让新会话默认可快速理解系统格局

---

## 6. 建议优先级

### 本周最值得做的 4 件事
1. **把 Feishu groupPolicy 收紧到 allowlist**
2. **做自动化资产清单**
3. **修正 Gateway 服务注册问题**
4. **输出一份群/私聊权限矩阵**

---

## 7. 最终判断

当前 OpenClaw 的问题已经不是“能力不够”，而是：

> **能力开始溢出，需要治理收口。**

如果继续无节制加能力，后面会越来越难管；
如果现在先治理，这套系统就会从“能跑的实验场”升级为“可持续进化的 AI 研发操作系统”。

---

## 8. 附：当前快照（本次盘点）

### 快照摘要
- OpenClaw：`2026.3.13`
- Gateway：本地 loopback 正常
- 主模型：`aiae/gpt-5.4-2026-03-05`
- 心跳：`30m + qwen3.5-flash-2026-02-23 + lightContext=true`
- 记忆：524 文件 / 3190 chunks
- 会话：68 active
- 当前保留项目：1 个
- 当前保留专家：8 位

### 本次确认到的关键事实
- 心跳配置已更新为 `lightContext = true`
- 飞书渠道正常
- Gateway 仍提示 service config 非标准
- 安全审计仍提示 3 个 critical
