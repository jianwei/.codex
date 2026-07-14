---
name: react-reverse-docs
description: 从现有 React 项目代码逆向生成完整文档体系，支持跨多个上下文窗口的长任务执行。采用 Initializer Agent + Coding Agent 双代理模式，适用于大型项目的系统梳理、重构前准备、技术评审。当用户有大量 React 代码需要生成文档、梳理系统架构、准备重构、分析遗留系统时务必使用此 Skill。触发关键词：逆向生成文档、从代码生成文档、分析React代码、梳理系统、重构前准备、代码转文档、生成PRD/接口文档/组件文档。
---

# React 逆向生成文档 Skill（每 Task 独立 Session 版）

---

## 两个入口

### 入口一：首次启动 `/react-reverse-docs`

执行以下时间检查逻辑，**再决定是全新开始还是继续**：

```bash
# 检查是否存在未完成的 doc-tasks.json
if [ ! -f "doc-tasks.json" ]; then
  # 不存在 → 直接全新开始，跳到"全新开始流程"
  echo "未找到 doc-tasks.json，全新开始"
else
  # 存在 → 读取 session_started_at，计算时间差
  python3 -c "
import json, datetime
d = json.load(open('doc-tasks.json'))
started = d.get('session_started_at', '')
remaining = [t for t in d['tasks'] if not t['passes']]
done = d['total'] - len(remaining)
if not started:
    print('NO_TIME')
else:
    delta = datetime.datetime.now() - datetime.datetime.strptime(started, '%Y-%m-%d %H:%M:%S')
    mins = int(delta.total_seconds() / 60)
    print(f'FOUND|{d[\"docs_dir\"]}|{done}/{d[\"total\"]}|{mins}|{started}')
"
fi
```

**根据检查结果，询问用户（唯一一次交互）：**

情况 A：`doc-tasks.json` 不存在，或时间差 > 60 分钟：
```
检测到上次任务（开始于 [started_at]，已过 [N] 分钟，完成 [M/T] 个）。
距上次运行超过 1 小时，建议全新开始。

请选择：
  1. 全新开始（清除旧记录，重新扫描项目）
  2. 继续上次任务（从第 [M+1] 个任务继续）
```

情况 B：`doc-tasks.json` 存在，时间差 ≤ 60 分钟：
```
检测到进行中的任务（开始于 [started_at]，已过 [N] 分钟，完成 [M/T] 个）。

请选择：
  1. 继续上次任务（推荐，从第 [M+1] 个任务继续）
  2. 全新开始（清除旧记录，重新扫描项目）
```

情况 C：`doc-tasks.json` 不存在：
```
未检测到进行中的任务，将全新开始。

请确认：
1. 项目根目录路径是什么？
2. 有什么特别要注意的吗？（没有直接回答"没有"）
```

> 用户回答后，立即执行，**不再询问任何问题**。

---

### 入口二：继续执行 `/react-reverse-docs-continue`

**每次 `/clear` 后由 Agent 自动调用，无需用户输入。**

执行相同的时间检查：

```bash
python3 -c "
import json, datetime
d = json.load(open('doc-tasks.json'))
started = d.get('session_started_at', '')
if started:
    delta = datetime.datetime.now() - datetime.datetime.strptime(started, '%Y-%m-%d %H:%M:%S')
    mins = int(delta.total_seconds() / 60)
    remaining = len([t for t in d['tasks'] if not t['passes']])
    print(f'mins={mins} remaining={remaining}')
"
```

- 时间差 ≤ 60 分钟：**直接继续**，不询问用户，从下一个 passes=false 的任务开始
- 时间差 > 60 分钟：**停止自动循环**，提示用户重新运行 `/react-reverse-docs` 手动选择

> `/react-reverse-docs-continue` 是自动循环专用入口，只在同一批次（≤60分钟）内有效。

---

## 核心设计：`run-docs.sh` 全自动驱动

```
/react-reverse-docs（首次，只需一次确认）
         │
         ▼
  Initializer Agent
  扫描项目 → 生成任务清单 → 生成 run-docs.sh → git commit
         │
         ▼
  输出提示：bash run-docs.sh
         │
         ▼（用户执行一次）
  run-docs.sh 循环：
    while 还有未完成任务:
      claude --print /react-reverse-docs-continue  ← 新子进程，全新上下文
          └── 完成 1 个 task → git commit → exit
         │
         ▼
  🎉 全部完成，输出终态报告
```

**用户总共只需要两次输入：**
1. 回答启动确认（项目路径 + 注意事项）
2. 执行 `bash run-docs.sh`

之后全程自动，每个 task 独立子进程，上下文天然隔离，不会累积。

---

## 执行规则

- ❌ 不允许在一个 Session 里完成超过 1 个 task
- ❌ 不允许跳过 git commit 直接 /clear
- ❌ 不允许跳过验证直接标记 passes=true
- ❌ 不允许使用 Write 工具写文件（必须用 bash `cat >`）
- ❌ 不允许在文件写入失败后假装自检通过
- ✅ 每次 /clear 前必须确认 commit 已成功（用 `git log --oneline -1` 验证）

---

## 目录命名规则

- Agent 自动识别当前模型名（优先自我声明，其次读环境变量）
- 格式：`project-docs-{模型名}`（转小写，空格替换为 `-`）
- 例：`project-docs-claude-sonnet-4-6`、`project-docs-gpt-4o`、`project-docs-glm-5`
- 目录已存在时**直接覆盖**，不追加日期，不新建新目录

**产出结构：**
```
project-docs-{model}/
├── doc-progress.md
├── init.sh
├── architecture.md
├── tech-debt.md
├── api/
├── pages/
├── components/
└── state/

doc-tasks.json          ← 放项目根目录，所有 Session 共享
```

---

## 文档模板索引

| 文档类型 | 参考文件 |
|---------|---------|
| Initializer Agent 完整提示 | `references/initializer.md` |
| Coding Agent 完整提示 | `references/coding-agent.md` |
| 架构文档模板 | `references/tpl-architecture.md` |
| PRD 页面文档模板 | `references/tpl-prd.md` |
| API 接口文档模板 | `references/tpl-api.md` |
| 组件文档模板 | `references/tpl-component.md` |
| 状态管理文档模板 | `references/tpl-state.md` |
| 技术债务报告模板 | `references/tpl-tech-debt.md` |

---

## doc-tasks.json 结构

```json
{
  "project": "my-react-app",
  "model": "glm-5",
  "docs_dir": "project-docs-glm-5",
  "created_at": "2026-03-07 14:48:48",
  "session_started_at": "2026-03-07 14:48:48",
  "total": 37,
  "completed": 0,
  "tasks": [
    {
      "seq": 1,
      "id": "arch-001",
      "category": "architecture",
      "description": "生成整体架构文档",
      "target_file": "project-docs-glm-5/architecture.md",
      "source_files": ["package.json", "src/App.jsx", "src/router/index.js"],
      "priority": 1,
      "passes": false,
      "created_at": "2026-03-07 14:48:48",
      "completed_at": null
    }
  ]
}
```

**字段规则：**
- `model`：Agent 自动识别写入，不可修改
- `docs_dir`：每个 Session 通过此字段定位目录，不可修改
- `session_started_at`：Initializer 初始化时写入，**用于时间差判断**，每次全新开始时更新，继续执行时不修改
- `seq`：从 1 递增，仅展示，不可修改
- `passes`：只能 `false → true`，不可逆
- `completed_at`：格式 `2026-03-07 14:48:48`，未完成保持 `null`