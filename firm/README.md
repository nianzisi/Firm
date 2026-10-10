# firm

一个从零手写的个人**练习项目**：把「LLM Agent 框架」和「种植 / 战斗小游戏」拼在一起，用来自学工程化、边界处理与 LLM 应用开发。

> ⚠️ 这是一个**学习 / 练习性质**的项目，不是生产级代码。
> 大量模块是边学边写，追求的是「自己动手把整条链路跑通」，而不是健壮、完整或可维护。

---

## 这是什么

项目有两条主线：

1. **`agent/`** —— 不依赖任何现成 Agent 框架，从零实现的一套 LLM 调用与工具系统（消息管理、HTTP 调用、工具注册、模板渲染、事件总线），并在其上搭了一条**小说自动生成流水线**。
2. **种植 / 战斗 / Web** —— 一个练手的小游戏：`seed/` 种田系统、`war/` 战斗结算、`web/` FastAPI 页面，`commomd/` 是共享的数据层（SQLAlchemy）。

---

## 目录结构

```
firm/
├── agent/                  # 从零手写的 LLM Agent 框架 + 小说生成流水线
│   ├── creat_env.py        # 读取 os.env 到环境变量
│   ├── chat.py             # url / headers / payload（LLM 环境）
│   ├── message.py          # 消息容器与校验
│   ├── send.py             # Send：组织消息、发请求、处理 tool_calls
│   ├── Even_bus.py         # 单例 EventBus + 注册/触发装饰器
│   ├── os.env              # API 配置（需自行填写）
│   ├── tools/              # get_sql.py（工具注册）、var.py（模板渲染）
│   ├── check/              # 数据与消息校验
│   ├── template/           # 提示词模板
│   ├── test/               # 测试
│   └── navel/              # 小说生成流水线（见下）
├── commomd/                # 共享数据层：SQLAlchemy 引擎 / Session / 通用 CRUD
│   ├── mind.py             # 引擎 / Session / with_db 装饰器
│   ├── data_class.py       # 通用增删查改
│   ├── decision.py
│   ├── datacreat.py
│   └── attribute_change.py
├── seed/                   # 种植系统：土地、种子、收获、背包
├── war/                    # 战斗系统：属性、战斗结算、掉落
├── web/                    # FastAPI 页面（种植侧）
├── learn/                  # AI Agent 学习计划（ReAct → 结构化输出 → 最小 agent → 图规划）
└── README.md
```

---

## 核心模块

### 1. agent —— 从零手写的 LLM Agent 框架

| 文件 | 职责 |
| --- | --- |
| `creat_env.py` / `os.env` | 从配置文件读取 API 配置，写入环境变量 |
| `chat.py` | 只负责 `url` / `headers` / `payload`（模型、messages、其他参数） |
| `message.py` | 消息容器：角色消息、system 位置管理、消息校验 |
| `send.py` | `Send` 类：组织消息 → 发请求 → 处理 tool_calls 递归 |
| `tools/get_sql.py` | `@tool` 装饰器 + 工具单例；由 docstring / 类型注解**自动生成 function JSON** |
| `tools/var.py` | `{{占位符}}` / `{{占位符=默认值}}` 模板渲染 |
| `Even_bus.py` | 单例 EventBus 与 `event_on` / `event_emit` 装饰器 |
| `check/` | 数据与消息的清洗、校验 |

设计上刻意做了分层：`chat`（网络参数）/ `message`（消息）/ `send`（编排）/ `tools`（工具）各管一段。

### 2. agent/navel —— 小说自动生成流水线

一条「世界观 → 大纲 → 角色 → 场景 → 章节 → 蒸馏风格 → 按风格重写」的生成链：

| 模块 | 作用 | 产物 |
| --- | --- | --- |
| `world_background.py` | 由一句设定生成世界观（含歧义检查） | `输出物/世界观.txt` |
| `outline.py` | 由世界观生成可驱动写作的章节大纲 | `输出物/大纲.txt` |
| `Initial_character.py` | 生成角色 DNA 卡（样貌 / 动机 / 弱点 / 价值观…） | `输出物/角色卡/角色2.json` |
| `scene.py` | 生成场景卡 | `输出物/角色卡/场景.json` |
| `chapter.py` | 逐章生成正文 + 角色状态表，并回写角色状态 | `输出物/章节/第N章.txt` |
| `distill.py` | **风格蒸馏**：喂若干小说片段，提炼可复用的写作技法 | `输出物/设定/风格.*` |
| `rewrite.py` | **按蒸馏风格重写**已有章节 | `输出物/章节_重写/第N章.txt` |

提示词都放在 `navel/template/`，素材放 `navel/资料/`，产物放 `navel/输出物/`。

### 3. commomd —— 共享数据层

- `mind.py`：SQLAlchemy 引擎 / `SessionLocal` / `with_db` 装饰器（自动建/提交/回滚/关闭 session）。
- `data_class.py`：通用增删查改 `data_add` / `data_change` / `data_del` / `data_search`，内置字段与类型校验。
- `decision.py`：数据库对象的属性判断辅助。

### 4. seed / war / web —— 练手小游戏

- **seed/**：土地（`Firm`）、种子（`Seed`）、收获关联（`Rewards`）、背包（`Back_bag`），以及完整动作 `Action`（种植 `plan_plan` / 收获 `reward` / 入库 `get_rewards`）。
- **war/**：属性（`Attribute`）、战斗（`attalk`）、结算控制（`paymentcontrol`，一个迷你的「行动 → 观察 → 思考 → 行动」流程）、掉落（`win_reward`）。
- **web/**：FastAPI + Jinja2，种植侧的种子上架 / 关联 / 查询页面。

---

## 环境与运行

**要求**

- Python 3.10+（代码里用了 `X | None` 语法）
- MySQL（库名 `planfirm`，连接串见 `commomd/mind.py`）

**依赖**（按代码导入整理）

```
requests
SQLAlchemy
PyMySQL
fastapi
uvicorn
jinja2
pytest      # 开发 / 测试
ruff        # 开发 / Lint
```

**配置 LLM**：填写 `agent/os.env`，需要这些键：

```
API_KEY    = "..."
api_url    = "https://api.deepseek.com/chat/completions"
MODEL      = "..."
stream     = "False"
max_tokens = "..."
temperature = "..."
```

**运行**

```bash
# 种植 Web 页面
python web/app.py            # http://localhost:8000

# 测试
pytest

# 小说生成（示例）
python agent/navel/world_background.py   # 逐步跑各环节
python agent/navel/chapter.py
```

---

## 技术栈

- **语言**：Python 3.10+
- **LLM**：DeepSeek / 兼容 OpenAI 格式的 Chat Completions API
- **Web**：FastAPI + Uvicorn + Jinja2
- **数据**：SQLAlchemy + MySQL（PyMySQL）
- **工程**：pytest、ruff

---

## 路线图 / 待做

- [ ] **种田侧**
  - [ ] 完善作物数量
  - [ ] 完善作物功能
  - [ ] 完善 web
- [ ] **战斗侧**
  - [ ] 角色 web
  - [ ] 优化成回合制
  - [ ] 角色模板
- [ ] **剧情（navel）**
  - [ ] 骨架层与扩写层分离：骨架只出「事件 + 状态 + 逻辑」，扩写只负责外饰
  - [ ] 章节间衔接（前情摘要 + 上一章结尾）
  - [ ] 角色静态 DNA 与动态状态分离
  - [ ] 不烧 token 的离线测试（fixture 回放）

---

> 再次说明：这是个人**练习项目**
Commit message
