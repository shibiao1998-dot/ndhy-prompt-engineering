# GitHub 开源项目深度调研：提示词工程与 AI 知识管理

> 调研时间：2026-03-16 00:50
> 目的：学习大型开源项目的经验，指导我们 AI 组织的专家能力提升

---

## 一、调研项目总览

| 项目 | Star | 核心定位 | 对我们的价值 |
|------|------|---------|------------|
| **Dify** | 132K | 生产级 Agent 工作流平台 | 知识库+RAG+工作流编排的完整架构参考 |
| **Prompt-Engineering-Guide** | 71K | 提示词工程教程合集 | 方法论学习，但偏理论 |
| **Anthropic 教程** | 33K | Claude 提示词工程交互教程 | Claude 最佳实践（我们用 Claude） |
| **promptfoo** | 16K | 提示词评估+红队测试 | 提示词质量评估方法论 |
| **Context-Engineering** | 8.5K | 上下文工程理论框架 | 从"提示词工程"到"上下文工程"的范式升级 |
| **BAML** | 7.7K | 提示词工程框架（Schema Engineering） | 将提示词变成类型安全的函数式编程 |
| **Microsoft promptbase** | 5.7K | 微软内部提示词最佳实践 | 企业级提示词管理经验 |

---

## 二、关键经验提炼

### 经验1：从 Prompt Engineering 到 Context Engineering（最重要）

**来源**：Andrej Karpathy + Context-Engineering 项目（8.5K star）

**核心转变**：
> "Context engineering is the delicate art and science of filling the context window with just the right information for the next step."
> — Andrej Karpathy

| Prompt Engineering | Context Engineering |
|-------------------|-------------------|
| 关注"你说什么" | 关注"模型看到的一切" |
| 单条指令 | 示例 + 记忆 + 检索 + 工具 + 状态 + 控制流 |
| 手动编写提示词 | 系统化的信息编排 |

**与 DJ 理念的完美对齐**：
- DJ 说"信息对称"= Karpathy 说的 "filling the context window with just the right information"
- DJ 说"维度"= Context Engineering 说的 "structured informational components"
- DJ 说"SOP + multi-agent"= Context Engineering 说的 "orchestration"

**对我们产品的启发**：
我们做的不是 Prompt Engineering 工具，而是 **Context Engineering 平台**——系统化地管理和组装上下文信息。

### 经验2：BAML 的 Schema Engineering 范式

**来源**：BoundaryML/baml（7.7K star）

**核心思路**：
- 将提示词变成**函数**：有输入类型、输出类型、模型选择
- 提示词不是字符串拼接，是**类型安全的模板渲染**
- 所有 prompt 都有 schema 约束，输出有类型检查

**代码示例**：
```baml
function ChatAgent(message: Message[], tone: "happy" | "sad") -> StopTool | ReplyTool {
  client "openai/gpt-4o-mini"
  prompt #"
    Be a {{ tone }} bot.
    {{ ctx.output_format }}
    {% for m in message %}
      {{ _.role(m.role) }}
      {{ m.content }}
    {% endfor %}
  "#
}
```

**对我们产品的启发**：
- 我们的维度组装逻辑可以借鉴 BAML 的模板思路
- 每个维度 = 一个结构化的信息模块，有类型（正向/反向/混合）
- 组装 prompt 的过程 = 模板渲染，不是字符串拼接

### 经验3：Dify 的知识库 + RAG 架构

**来源**：langgenius/dify（132K star）

**核心架构**：
1. **知识库管理**：文档上传 → 分段 → 向量化 → 检索
2. **RAG Pipeline**：查询 → 检索相关文档 → 注入上下文 → 生成回答
3. **工作流编排**：可视化 DAG，支持条件分支、循环、子流程
4. **多模型支持**：统一接口适配 100+ 模型
5. **LLMOps**：监控、日志、性能分析

**对我们产品的启发**：
- 维度库 = Dify 的知识库概念，但我们的维度是**结构化的**（不是自由文本文档）
- 维度匹配 = Dify 的 RAG 检索，但我们用**规则匹配+AI动态匹配**（不只是向量检索）
- 未来接入 AI Hub 知识库（DJ会议纪要）时，可以借鉴 Dify 的文档处理 pipeline

### 经验4：promptfoo 的评估方法论

**来源**：promptfoo/promptfoo（16K star）

**核心能力**：
- 提示词 A/B 测试：同一输入，不同提示词，对比输出质量
- 红队测试：自动发现提示词的安全漏洞
- CI/CD 集成：提示词变更自动触发评估
- 多模型对比：同一提示词在不同模型上的表现

**对我们产品的启发**：
- **维度覆盖率**就是一种评估指标——我们已经在做
- 未来可以加入"同一任务，不同维度组合，对比输出质量"的 A/B 测试
- DJ 说的"提示词进步"可以用 promptfoo 的评估框架来量化

### 经验5：Anthropic 的 Claude 最佳实践

**来源**：anthropics/prompt-eng-interactive-tutorial（33K star）

**关键技巧**（我们用 Claude，直接适用）：
1. **给 Claude 角色**：明确告诉 Claude 它是"华渔教育的 AI 设计师"
2. **结构化输出**：用 XML 标签（`<design_overview>`）引导输出格式
3. **思维链**：让 Claude 先分析再产出，提高质量
4. **示例学习**：给 Claude 看好的设计方案范例
5. **长上下文利用**：Claude 200K 上下文足够装下所有89个维度

---

## 三、对组织各专家的学习建议

| 专家 | 应该学习的项目 | 学什么 |
|------|--------------|--------|
| **后端开发专家** | Dify 后端架构 | RAG pipeline、知识库 CRUD、流式 API、工作流引擎 |
| **前端开发专家** | Dify 前端 + BAML Playground | 对话式 UI、流式渲染、可视化编排界面 |
| **技术架构专家** | Dify + Context-Engineering | 上下文工程架构、知识库+检索+生成的系统设计 |
| **体验设计专家** | Dify/ChatGPT 对话式交互 | 对话式 AI 产品的 UX 模式 |
| **产品定义专家** | Context-Engineering 理论 | 从 Prompt Engineering 到 Context Engineering 的范式转变 |
| **API设计专家** | Dify API + BAML 类型系统 | AI 产品的 API 设计模式（流式、知识库、评估） |
| **测试专家** | promptfoo | 提示词评估方法论、红队测试、自动化质量检查 |
| **教育领域专家** | Anthropic Claude 教程 | Claude 特有的提示词技巧（我们主力用 Claude） |

---

## 四、对 v2 产品的直接改进建议

### 立即可用（v2.0）
1. **借鉴 BAML 的模板思路**：维度组装用 Jinja2 模板而非字符串拼接
2. **借鉴 Anthropic 教程**：system prompt 用 XML 标签分段（正向/反向）
3. **借鉴 Dify 的知识库 UI**：维度管理页参考 Dify 的知识库管理界面

### 后续迭代（v2.1+）
4. **借鉴 promptfoo 评估**：加入"同一任务、不同维度组合"的对比功能
5. **借鉴 Context-Engineering**：将维度库进化为完整的上下文工程平台
6. **借鉴 Dify RAG**：接入 AI Hub 知识库后，用 RAG 方式检索 DJ 会议纪要

---

## 五、核心结论

**我们在做的事情，比业界大多数"提示词工程"工具更先进**：
- 大多数工具关注"怎么写好一条提示词"
- 我们关注"怎么系统化地管理和组装完整的信息上下文"
- 这正是 Andrej Karpathy 说的 Context Engineering

**但我们的实现方式需要向这些项目学习**：
- 知识库管理 → 学 Dify
- 提示词模板化 → 学 BAML
- 质量评估 → 学 promptfoo
- Claude 最佳实践 → 学 Anthropic 教程

**DJ 的"信息对称"理念是走在了行业前面的。** 我们要做的是用工程化的方式把它落地。
