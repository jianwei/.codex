# Codex 全局规则索引

以下规则集中在 `/Users/chenjianwei2/.codex/agent-rules/`。按任务触发条件**显式读取**对应文件。所有入口均使用绝对路径，不能相对当前项目目录解析，也不依赖 `@` 语法自动展开。

| 触发条件 | 必须读取的规则 |
| --- | --- |
| 每次任务开始 | [语言与沟通](/Users/chenjianwei2/.codex/agent-rules/LANGUAGE_RULES.md)、[任务路由](/Users/chenjianwei2/.codex/agent-rules/TASK_ROUTING_RULES.md)、[Skill 路由](/Users/chenjianwei2/.codex/agent-rules/SKILL_ROUTING_RULES.md) |
| 规划、实施或验证非简单任务 | [通用工作原则](/Users/chenjianwei2/.codex/agent-rules/WORKING_RULES.md) |
| 打开页面或调试网页 | [浏览器调试](/Users/chenjianwei2/.codex/agent-rules/BROWSER_RULES.md) |
| 新建函数，或新增、修改 JavaScript、TypeScript 或 Vue 脚本代码 | [JavaScript 与 TypeScript 代码规范](/Users/chenjianwei2/.codex/agent-rules/JS_TS_CODE_RULES.md) |
| 评审 `.js`、`.jsx`、`.mjs`、`.cjs`、`.ts`、`.tsx`、`.mts`、`.cts` 或 Vue 脚本代码 | [JavaScript 与 TypeScript 代码评审](/Users/chenjianwei2/.codex/agent-rules/JS_TS_REVIEW_RULES.md) |
| 新增、修改或评审 HTML、Vue 模板或 JSX/TSX 界面标记 | [HTML 代码规范](/Users/chenjianwei2/.codex/agent-rules/HTML_CODE_RULES.md) |
| 新增、迁移、修改或评审测试文件与测试用例 | [测试规则](/Users/chenjianwei2/.codex/agent-rules/TEST_RULES.md) |
| 完成任何代码新增、修改、删除或重构后，在交付前自动执行代码评审；不等待用户另行触发 | [代码评审与工程约束](/Users/chenjianwei2/.codex/agent-rules/CODE_REVIEW_RULES.md) |
| 代码修改完成且验证通过后，项目根目录存在 `README.md` | [README 同步规则](/Users/chenjianwei2/.codex/agent-rules/README_SYNC_RULES.md) |
| 执行 shell 命令 | [RTK 命令规则](/Users/chenjianwei2/.codex/agent-rules/RTK.md) |
