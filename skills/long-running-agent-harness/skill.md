---
name: long-running-agent-harness
description: 构建和管理长时间运行的 AI Agent 工作流，使其在多个上下文窗口中持续有效工作，通过双层 Agent 架构（初始化 + 编码）实现增量进度、测试验证和状态桥接。
metadata:
  author: cursor AI claude-4.6-opus-high-thinking
  version: "2.0.0"
  source: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
---

# Long-Running Agent Harness

构建和管理长时间运行的 AI Agent，使其能够在多个上下文窗口中持续有效地工作。

## 触发条件

- 用户需要构建复杂项目（跨越多个上下文窗口，数小时或数天）
- 用户需要将大型任务拆分为可增量完成的子功能
- 用户希望 Agent 能在会话间保持进度、避免重复劳动
- 用户明确提到 "long-running"、"多轮会话"、"增量开发"、"功能列表" 等关键词

## 核心问题

Agent 必须在离散的会话中工作，每个新会话开始时都没有之前的记忆。如同轮班工程师——每位新工程师到达时不知道前一班发生了什么。上下文窗口有限，复杂项目无法在单个窗口内完成，Agent 需要一种在会话之间搭建桥梁的方法。

### 常见失败模式

| 失败模式 | 表现 | 后果 |
|----------|------|------|
| 一次性完成 | Agent 试图在一个会话中做完所有事 | 上下文耗尽，半成品无文档，下个会话需猜测状态 |
| 过早宣布完成 | 看到已有进展就认为项目完成 | 大量功能缺失 |
| 缺乏测试就标记完成 | 代码能编译就标记 passing | 功能端到端不可用 |
| 环境不干净 | 留下未提交的代码、未记录的进度 | 下个会话需大量时间清理 |

## 解决方案：双层 Agent 架构

### 架构总览

```
┌─────────────────────────────────────────────┐
│              第一次运行                       │
│  ┌─────────────────────────────────────┐    │
│  │     初始化 Agent (Initializer)       │    │
│  │  - git init                         │    │
│  │  - 创建 feature_list.json           │    │
│  │  - 创建 init.sh                     │    │
│  │  - 创建 claude-progress.txt         │    │
│  │  - 初始 git commit                  │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          每个后续会话（循环）                  │
│  ┌─────────────────────────────────────┐    │
│  │      编码 Agent (Coding Agent)       │    │
│  │  1. pwd → 确认工作目录               │    │
│  │  2. 读取 claude-progress.txt         │    │
│  │  3. 读取 feature_list.json           │    │
│  │  4. git log --oneline -20            │    │
│  │  5. 运行 init.sh 启动服务            │    │
│  │  6. E2E 验证基础功能                  │    │
│  │  7. 选择一个未完成功能                 │    │
│  │  8. 实现 + 测试                      │    │
│  │  9. git commit + 更新进度文件         │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### 1. 初始化 Agent

仅在第一次运行时执行，为整个项目生命周期奠基。

**产出物：**

| 文件 | 用途 |
|------|------|
| `feature_list.json` | 从用户需求分解出的完整功能清单，所有功能初始标记为 `"passes": false` |
| `init.sh` | 一键启动开发环境的脚本（安装依赖 + 启动服务器） |
| `claude-progress.txt` | Agent 进度日志，每个会话追加记录 |
| 初始 git commit | 记录项目初始状态 |

**feature_list.json 格式：**

```json
[
  {
    "category": "functional",
    "description": "New chat button creates a fresh conversation",
    "steps": [
      "Navigate to main interface",
      "Click 'New Chat' button",
      "Verify a new conversation is created",
      "Check that chat area shows welcome state",
      "Verify conversation appears in sidebar"
    ],
    "passes": false
  }
]
```

**关键约束：**
- 使用 JSON 而非 Markdown（模型不太可能不当修改或覆盖 JSON 文件）
- 功能列表应包含详细的端到端测试步骤
- 所有功能初始标记为 `false`
- 使用强措辞保护测试完整性：**"移除或编辑测试是不可接受的，因为这可能导致缺失或有缺陷的功能"**

### 2. 编码 Agent

每个后续会话执行，专注于增量进度。

**会话开始协议：**

```
1. pwd                              → 确认工作目录
2. read claude-progress.txt         → 了解最近完成的工作
3. read feature_list.json           → 查看功能清单和完成状态
4. git log --oneline -20            → 检查最近提交历史
5. ./init.sh                        → 启动开发服务器
6. 浏览器自动化 E2E 验证              → 确保基础功能正常
```

**功能实现协议：**
- 每次只处理一个功能
- 实现后使用浏览器自动化进行端到端测试（像人类用户一样操作）
- 仅在通过完整 E2E 测试后才标记 `"passes": true`

**会话结束协议：**

```
1. git add . && git commit -m "feat: [功能描述]"
2. 追加到 claude-progress.txt：[时间] Completed: [功能描述]
3. 更新 feature_list.json 中对应功能的 passes 字段
4. git add . && git commit -m "chore: update progress for [功能描述]"
```

**清洁状态定义：**
- 没有主要错误
- 代码有序且有文档
- 其他开发者可以立即开始新功能，无需先清理无关问题

## 环境管理

### 项目文件结构

```
project-root/
├── init.sh                  # 开发环境启动脚本
├── claude-progress.txt      # Agent 进度日志
├── feature_list.json        # 功能需求清单（JSON）
└── src/                     # 源代码目录
```

### 测试策略

- 使用浏览器自动化工具（Playwright MCP / Puppeteer MCP / cursor-ide-browser）
- 以人类用户视角进行所有测试——验证功能实际可用，而非仅代码能编译
- 每个会话开始前先执行基础 E2E 测试，捕获可能的回归错误
- 在实现新功能之前确保已有功能仍然工作

### 进度桥接机制

会话间的状态传递依赖三个信息源：

1. **claude-progress.txt**：自然语言描述的工作日志，快速了解最近做了什么
2. **feature_list.json**：结构化的功能完成状态，明确还有多少工作待做
3. **git history**：代码级别的变更记录，可回溯和恢复

## 执行步骤

### 步骤 1：初始化环境（仅首次）

1. 分析用户需求，分解为详细功能列表
2. 创建 `feature_list.json`（每个功能包含 category、description、steps、passes）
3. 创建 `init.sh`（安装依赖 + 启动开发服务器）
4. 创建空的 `claude-progress.txt`
5. `git init && git add . && git commit -m "Initial project setup"`

### 步骤 2：持续开发循环（每个会话）

1. 读取 `claude-progress.txt` + `git log` 获取上下文
2. 读取 `feature_list.json`，选择下一个 `passes: false` 的功能
3. 运行 `init.sh` 启动开发服务器
4. E2E 验证基础功能正常
5. 实现选定功能
6. E2E 测试该功能
7. 通过后 git commit + 更新进度文件 + 更新功能状态

### 步骤 3：验证完成

1. 读取 `feature_list.json`，确认所有功能 `passes: true`
2. 执行最终全量 E2E 测试
3. 标记项目完成

## 失败模式对照表

| 问题 | 初始化 Agent 应对 | 编码 Agent 应对 |
|------|-------------------|-----------------|
| 一次性做太多 | 创建完整 feature_list.json，明确列出所有功能 | 每次只处理一个功能 |
| 过早宣布完成 | 初始提交显示添加的文件 | 读取功能列表，只处理 passes: false 的功能 |
| 环境状态混乱 | 初始 git 仓库 + 进度日志 | 会话结束必须 git commit + 更新日志 |
| 未测试就标记完成 | 详细的测试步骤 | E2E 测试通过后才标记 passing |
| 不知道如何运行应用 | 编写 init.sh | 会话开始读取并运行 init.sh |

## 提示词模板

### 初始化 Agent

```markdown
你是一个初始化 Agent，负责为长时间运行的编码任务设置环境。

用户需求：[TASK_DESCRIPTION]

请执行以下操作：

1. 创建项目目录结构
2. 初始化 Git 仓库
3. 创建 feature_list.json，将用户需求分解为详细的功能列表
   - 每个功能包含：category、description、steps（端到端测试步骤）、passes（初始 false）
   - 功能粒度要足够细，每个功能可在一个会话内完成
4. 创建 init.sh 脚本（安装依赖 + 启动开发服务器）
5. 创建空的 claude-progress.txt
6. git commit -m "Initial project setup"

重要：
- feature_list.json 必须使用 JSON 格式
- 移除或编辑测试步骤是不可接受的
```

### 编码 Agent

```markdown
你是一个编码 Agent，负责在长时间运行的项目中实现功能。

会话开始：
1. pwd → 确认工作目录
2. 读取 claude-progress.txt → 了解已完成的工作
3. 读取 feature_list.json → 选择优先级最高且 passes 为 false 的功能
4. git log --oneline -20 → 查看最近提交
5. 运行 init.sh → 启动开发服务器
6. 浏览器自动化验证基础功能正常

实现功能：
1. 阅读功能描述和测试步骤
2. 编写代码实现
3. 使用浏览器自动化进行 E2E 测试
4. 修复所有发现的错误

会话结束：
1. git commit（有意义的提交消息）
2. 更新 claude-progress.txt
3. 更新 feature_list.json 中 passes 字段为 true
4. git commit 进度更新

重要：
- 每次会话只处理一个功能
- 不要移除或编辑现有测试
- 仅通过完整 E2E 测试后才标记功能完成
- 留下干净的状态以便下个会话继续
```

## 适用场景与限制

### 适用场景
- 全栈 Web 应用开发
- 需要多天/多会话完成的复杂项目
- 任何需要跨上下文窗口保持进度的长期任务

### 当前限制
- 浏览器自动化无法捕获所有 UI 问题（如原生 alert 模态框）
- Vision 能力限制可能导致部分 UI bug 遗漏
- 单一通用 Agent 可能不如专业化多 Agent 架构（测试 Agent、QA Agent、清理 Agent）

### 未来方向
- 多 Agent 架构：专业化的测试、QA、代码清理 Agent
- 推广到非 Web 开发领域（科学研究、金融建模等）
