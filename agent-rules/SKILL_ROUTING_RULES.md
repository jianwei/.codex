# Skill 路由

每次任务开始时，以当前会话提供的 Available skills 为准选择 Skill；本文件只维护高频路由和重叠 Skill 的选择规则，不缓存完整清单。

## 选择规则

- 用户明确点名 Skill 时，先读取该 Skill，再执行任务。
- 请求命中 Skill 描述中的强制触发条件时，必须读取该 Skill；其余场景选择能完整覆盖任务的最窄 Skill。
- 多个 Skill 同时匹配时，按“用户点名 → 具体业务或框架 Skill → 通用 Skill”选择；只有职责互补时才组合使用，并遵循各 Skill 规定的先后顺序。
- Skill 决定工作流程，执行代理、模型和推理强度仍由 [任务路由](/Users/chenjianwei2/.codex/agent-rules/TASK_ROUTING_RULES.md) 决定。
- 当前会话没有对应 Skill 或调用能力时，说明缺失项并使用现有工具继续；不得使用本文件中的名称推定 Skill 已安装。

## 排障、测试与评审

| 请求 | Skill |
| --- | --- |
| 复杂 Bug、性能回退、根因排查 | `diagnosing-bugs` |
| 交互式 QA、持续记录问题 | `qa` |
| 钉钉文档或表格中的 Bug 任务 | `fix-bug-by-dingding` |
| 通用代码评审或 diff 评审 | `code-review` |
| JavaScript、TypeScript、React 前端评审 | `frontend-code-review` |
| 极严格的可维护性和抽象质量评审 | `thermo-nuclear-code-quality-review` |
| UI 规范与可访问性评审 | `web-design-guidelines` |
| 明确要求测试驱动开发 | `tdd` |
| Web 单元、集成、E2E、性能或安全测试 | `web-testing` |
| 操作并验证本地 Web 应用 | `webapp-testing` |
| 生成 Vue 或 React 页面测试用例文档 | `frontend-test-cases` |

## 前端、设计与浏览器

| 请求 | Skill |
| --- | --- |
| Vue 代码任务 | `vue-best-practices`；按需组合 `vue`、`vue-router-best-practices`、`vue-testing-best-practices` |
| Vue 迁移到 Vue 3 或 TypeScript | `vue-migrate`；旧 SPA 单页升级使用 `vue-legacy-spa-upgrade` |
| 迁移、重写或复刻已有页面 | `page-migration` |
| 新建或重做生产级前端界面 | `frontend-design` |
| 根据 Figma 实现界面 | `figma:figma-design-to-code`，再按该 Skill 要求调用 `figma:figma-use`；代码实施使用 `implement-design` |
| 途牛设计系统 | `tuniu-design` |
| Vue/HTML 埋点 | `event-track`；React 页面点或性能打点使用 `page-track` |
| 使用现有 Chrome 登录态 | `chrome:control-chrome`；明确要求 Playwriter 时使用 `playwriter` 或 `playwriter-connect` |
| 使用应用内浏览器 | `browser:control-in-app-browser` |

## Git、交付与工程工具

| 请求 | Skill |
| --- | --- |
| 只生成提交说明 | `commit-msg` |
| 执行 Git 暂存、提交、推送或分支操作 | `git-commit` |
| 创建 PR | `pr-creator`；只生成 PR 描述使用 `create-pr-msg` |
| 解决 merge 或 rebase 冲突 | `resolving-merge-conflicts` |
| 强制回滚 Git 历史 | `git-rollback` |
| 同步 SVN 历史到 Git | `sync-svn-history-to-git` |
| 格式化代码 | `code-formatter`；配置提交前检查使用 `setup-pre-commit` |
| pnpm、Vite、Turborepo | 分别使用 `pnpm`、`vite`、`turborepo` |
| Nginx 或 Express 服务 | 分别使用 `nginx-configuration`、`nodejs-express-server` |
| JumpServer 登录 | `bastion-login` |

## 文档、研究与 Skill 管理

| 请求 | Skill |
| --- | --- |
| 根据代码变更同步项目文档 | `update-docs` |
| 逆向生成 jQuery、React 或 Vue 项目文档 | 分别使用 `jquery-reverse-docs`、`react-reverse-docs`、`vue-reverse-docs` |
| Obsidian 笔记 | `obsidian-vault` |
| 调研并引用高可信来源 | `research` |
| 翻译文章或文档 | `baoyu-translate` |
| PDF、Word、演示文稿或电子表格 | 分别使用 `pdf:pdf`、`documents:documents`、`presentations:Presentations`、`spreadsheets:Spreadsheets` |
| 查找或安装 Skill | 分别使用 `find-skills`、`skill-installer` |
| 创建或修改 Codex Skill | `skill-creator`；Agent 或 Claude 专用 Skill 分别使用 `skill-creator-agents`、`skill-creator-claude` |
| 编写供 Agent 使用的规则或说明 | `writing-for-agents` |
