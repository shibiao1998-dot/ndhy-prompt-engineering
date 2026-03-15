# 华渔提示词工程 · AI设计师

> 信息对称 · 相信 AI —— 让每次设计对话都达到专业级别

为华渔 AI 设计师提供信息对称的提示词工程服务——用户描述设计任务，系统自动补全所有维度信息，调用 AI 直接产出设计方案。

## 核心理念

> "提示词工程就是信息对等，只做信息对等……为AI提供最全面的信息，保证它能够把后续工作做好的信息。" —— DJ

## 功能特性

- 🎯 **对话式设计工作台**：输入设计任务 → AI 智能追问 → 产出结构化设计方案
- 📊 **99维度知识库**：12大类信息维度，覆盖战略/用户/竞品/场景/方法/可行性/历史/规范/质量/领域知识/术语/全生命周期
- 🔍 **引擎盖面板**：维度覆盖报告 + 提示词原文（正向/反向分离）+ 多引擎格式预览
- 📚 **维度管理**：查看/编辑/审核维度描述，支持新维度发现
- 🔄 **多引擎适配**：Claude/GPT/Gemini/DeepSeek/Midjourney/DALL-E/Suno 格式预览 + 一键复制
- 💬 **多轮对话**：AI 带着完整维度上下文持续迭代

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.11+ / FastAPI / SQLite / aiosqlite |
| 前端 | React 18 / TypeScript / Vite / Ant Design 5 |
| AI | Claude Opus 4.6 via ndhy-gateway |

## 快速开始

### 后端
```bash
cd backend
pip install -r requirements.txt
python init_dimensions.py  # 初始化89维度数据
python main.py             # 启动后端 http://localhost:8000
```

### 前端开发
```bash
cd frontend
npm install
npm run dev    # 启动开发服务器 http://localhost:5173
npm run build  # 构建生产版本
```

### 部署
```bash
# 构建前端并部署到后端静态文件
cd frontend && npm run build
cp -r dist ../backend/static
cd ../backend && python main.py  # http://localhost:8000
```

## 项目结构

```
prompt-engineering-v2/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── database.py          # SQLite 数据库
│   ├── models.py            # Pydantic 模型
│   ├── init_dimensions.py   # 维度初始化脚本
│   ├── routers/             # API 路由
│   │   ├── chat.py          # 对话 + SSE 流式
│   │   ├── dimensions.py    # 维度 CRUD
│   │   ├── review.py        # 审核流程
│   │   ├── match.py         # 维度匹配
│   │   ├── prompt.py        # 提示词预览
│   │   ├── engines.py       # 引擎列表
│   │   └── stats.py         # 统计数据
│   └── services/            # 业务服务
│       ├── ai_service.py    # Claude API 集成
│       ├── dimension_matcher.py  # 维度匹配逻辑
│       ├── engine_adapter.py     # 多引擎适配
│       └── prompt_assembler.py   # 正反向提示词组装
├── frontend/
│   └── src/
│       ├── App.tsx           # 路由
│       ├── main.tsx          # 入口
│       ├── pages/            # 页面
│       │   ├── Workbench.tsx # 设计工作台
│       │   └── DimensionManager.tsx  # 维度管理
│       ├── components/       # 组件
│       ├── hooks/            # 自定义 Hook
│       ├── services/         # API 服务
│       └── types/            # TypeScript 类型
└── product-spec.md           # 产品方案
```

## License

Private - 华渔教育内部使用
