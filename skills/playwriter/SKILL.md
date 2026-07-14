---
name: playwriter
description: 使用 Playwriter MCP 进行浏览器自动化控制。当用户提到"测试"、"使用playwriter"、"用playwriter"、"自动化测试"、"跑测试"、"执行测试用例"、"测试功能"、"测试页面"时，必须立即开始执行，不要询问"需要我做什么"，直接读取测试文件并用 Playwriter MCP 逐条执行所有测试用例。触发关键词：测试、使用playwriter、用playwriter、浏览器自动化、控制浏览器、网页操作、点击网页、截图、浏览器测试、Playwright、Playwriter、自动填表、网页爬取、执行测试、跑用例。
---

# Playwriter 浏览器自动化 Skill

> 本 Skill 分为 4 个文件，请按需查阅：
> - **SKILL.md**（本文件）：安装配置、快速上手
> - **references/RULES.md**：强制规则、禁止行为、常见违规
> - **references/API.md**：工具函数列表、操作代码示例
> - **references/OPTIMIZATION.md**：性能优化规则（evaluate/waitFor/流程模板/错误检查）
> - **references/TROUBLESHOOTING.md**：实战经验、问题排查

**GitHub 地址：** https://github.com/remorses/playwriter
**Chrome 扩展：** https://chromewebstore.google.com/detail/playwriter-mcp/jfeammnjpkecdekppnclgkkffahnhfhe

## ⚡ 收到测试指令后的行为规则

**当用户说"使用 Playwriter 测试 xxx"、"用 Playwriter 跑测试"、"测试这个文件里的功能"等指令时：**

1. **直接开始执行，不要问"需要我做什么"**
2. 读取测试文件 → 确认页面已连接 → 逐条执行所有 TC → 输出汇总结果
3. 如果测试文件已经在上下文中（如 `@test/xxx.md`），直接开始，无需再次确认

---

**GitHub 地址：** https://github.com/remorses/playwriter
**Chrome 扩展：** https://chromewebstore.google.com/detail/playwriter-mcp/jfeammnjpkecdekppnclgkkffahnhfhe

Playwriter 是一个基于 Chrome 扩展的浏览器 MCP 工具，通过完整的 Playwright API 控制浏览器标签页，比传统 Playwright MCP 节省 80% 上下文窗口，同时支持完整 CDP 访问。

---

## 🚀 快速上手：从零到可用的完整步骤（Claude Code 环境）

> 使用环境：**Claude Code**（命令行工具），不是 Claude Desktop。

### Step 1：确认 Node.js 已安装

```bash
node -v   # 需要 v18 以上
npx -v    # 确认 npx 可用
```

如未安装，前往 https://nodejs.org 下载安装。

---

### Step 2：安装 Chrome 扩展

1. 用 Chrome 访问扩展商店：
   https://chromewebstore.google.com/detail/playwriter-mcp/jfeammnjpkecdekppnclgkkffahnhfhe
2. 点击「添加至 Chrome」安装扩展
3. 点击浏览器右上角 **拼图图标 🧩** → 找到 Playwriter → 点击 **📌 固定** 到工具栏

---

### Step 3：配置 Claude Code MCP

Claude Code 支持多种方式配置 MCP，推荐使用项目级 `.mcp.json`。

**方式一：项目级配置（推荐）**

在项目根目录创建 `.mcp.json` 文件：

```json
{
  "mcpServers": {
    "playwriter": {
      "command": "npx",
      "args": ["playwriter@latest"]
    }
  }
}
```

**方式二：通过 Claude Code 命令行添加**

```bash
claude mcp add playwriter npx playwriter@latest
```

**方式三：添加到全局配置**

```bash
claude mcp add --global playwriter npx playwriter@latest
```

验证配置是否生效：

```bash
claude mcp list
# 输出中应包含 playwriter
```

---

### Step 4：连接浏览器标签页

1. 打开 Chrome，导航到你想控制的网页
2. 点击工具栏中的 **Playwriter 扩展图标**
3. 图标变为 **绿色** = 连接成功 ✅

图标状态说明：

| 图标状态 | 含义 |
|---------|------|
| 灰色 | 未连接，需点击 |
| 绿色 ✅ | 已连接，可以开始 |
| 橙色（...）| 正在连接中 |
| 红色（!）| 连接出错，刷新页面后重试 |

---

### Step 5：启动 Claude Code 并开始使用

```bash
# 进入含 .mcp.json 的项目目录
cd your-project

# 启动 Claude Code
claude
```

然后直接告诉 Claude 你想做什么：

```
帮我截图当前页面
帮我在搜索框输入 "hello world" 并点击搜索
帮我抓取这个页面所有产品的名称和价格
帮我填写并提交这个表单
```

Claude 会通过 `execute` 工具自动调用 Playwright 代码完成操作。

---

### 远程/容器环境额外步骤（devcontainer / VM / WSL）

如果 Claude Code 运行在容器或 WSL 内，而 Chrome 在宿主机上：

**① 宿主机（Chrome 所在机器）执行：**
```bash
# 启动 relay server
npx -y playwriter serve --token my-secret-token

# 或用环境变量
PLAYWRITER_TOKEN=my-secret-token npx -y playwriter serve
```

**② 容器 / WSL 内的 `.mcp.json`：**
```json
{
  "mcpServers": {
    "playwriter": {
      "command": "npx",
      "args": [
        "playwriter@latest",
        "--host", "host.docker.internal",
        "--token", "my-secret-token"
      ]
    }
  }
}
```

或用环境变量方式：
```json
{
  "mcpServers": {
    "playwriter": {
      "command": "npx",
      "args": ["playwriter@latest"],
      "env": {
        "PLAYWRITER_HOST": "host.docker.internal",
        "PLAYWRITER_TOKEN": "my-secret-token"
      }
    }
  }
}
```

> devcontainer 使用 `host.docker.internal`；SSH/VM 使用宿主机 IP。
> WSL 完全支持，Playwriter 通过 WebSocket :19988 通信，无需 Native Messaging。

---


## 与其他方案对比

| 功能 | Claude in Chrome | BrowserMCP | Playwriter |
|------|-----------------|------------|------------|
| Windows WSL 支持 | ❌ | ❌ | ✅ |
| 兼容任意 MCP 客户端 | ❌（仅 Claude）| ✅ | ✅ |
| 上下文传输方式 | 截图（100KB-1MB+）| 截图 | 无障碍快照（5-20KB）|
| 完整 Playwright API | ❌ | ❌ | ✅ |
| 调试器（断点）| ❌ | ❌ | ✅ |
| 实时代码编辑 | ❌ | ❌ | ✅ |
| CSS 样式检查 | ❌ | ❌ | ✅ |
| 完整网络拦截 | 有限 | 有限 | ✅ |
| React 源码定位 | ❌ | ❌ | ✅ |
| 右键钉元素 | ❌ | ❌ | ✅ |
| 原始 CDP 访问 | ❌ | ❌ | ✅ |
| MCP 工具数量 | 多个 | 17+ 个 | **1 个** |