# Codex 全局规则索引

以下规则集中在 `agent-rules/`。按任务触发条件**显式读取**对应文件；Markdown 链接仅用于定位，不依赖 `@` 语法自动展开。

| 触发条件 | 必须读取的规则 |
| --- | --- |
| 每次任务开始 | [语言与沟通](./agent-rules/LANGUAGE_RULES.md)、[代理路由](./agent-rules/AGENT_ROUTING_RULES.md)、[模型路由](./agent-rules/MODEL_ROUTING_RULES.md)、[Skill 路由](./agent-rules/SKILL_ROUTING_RULES.md) |
| 规划、实施或验证非简单任务 | [通用工作原则](./agent-rules/WORKING_RULES.md) |
| 打开页面或调试网页 | [浏览器调试](./agent-rules/BROWSER_RULES.md) |
| 新建函数或修改代码 | [函数注释规范](./agent-rules/CODE_STYLE_RULES.md) |
| 实施或评审相关代码 | [代码评审与工程约束](./agent-rules/CODE_REVIEW_RULES.md) |
| 执行 shell 命令 | [RTK 命令规则](./agent-rules/RTK.md) |
