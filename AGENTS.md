# Codex 全局规则索引

以下规则集中在 `/Users/chenjianwei2/.codex/agent-rules/`。按任务触发条件**显式读取**对应文件。所有入口均使用绝对路径，不能相对当前项目目录解析，也不依赖 `@` 语法自动展开。

| 触发条件 | 必须读取的规则 |
| --- | --- |
| 每次任务开始 | [语言与沟通](/Users/chenjianwei2/.codex/agent-rules/LANGUAGE_RULES.md)、[代理路由](/Users/chenjianwei2/.codex/agent-rules/AGENT_ROUTING_RULES.md)、[模型路由](/Users/chenjianwei2/.codex/agent-rules/MODEL_ROUTING_RULES.md)、[Skill 路由](/Users/chenjianwei2/.codex/agent-rules/SKILL_ROUTING_RULES.md) |
| 规划、实施或验证非简单任务 | [通用工作原则](/Users/chenjianwei2/.codex/agent-rules/WORKING_RULES.md) |
| 打开页面或调试网页 | [浏览器调试](/Users/chenjianwei2/.codex/agent-rules/BROWSER_RULES.md) |
| 新建函数或修改代码 | [函数注释规范](/Users/chenjianwei2/.codex/agent-rules/CODE_STYLE_RULES.md) |
| 新增、修改或评审 JavaScript、TypeScript 或 Vue 代码 | [JavaScript 与 TypeScript 代码规范](/Users/chenjianwei2/.codex/agent-rules/JS_TS_CODE_RULES.md) |
| 新增、修改或评审 HTML 或 Vue 模板 | [HTML 代码规范](/Users/chenjianwei2/.codex/agent-rules/HTML_CODE_RULES.md) |
| 新增、迁移或修改测试代码 | [测试目录布局](/Users/chenjianwei2/.codex/agent-rules/TEST_LAYOUT_RULES.md) |
| 实施或评审相关代码 | [代码评审与工程约束](/Users/chenjianwei2/.codex/agent-rules/CODE_REVIEW_RULES.md) |
| 执行 shell 命令 | [RTK 命令规则](/Users/chenjianwei2/.codex/agent-rules/RTK.md) |
