# Skill 路由

用户请求匹配当前会话**实际可用**的 Skill 时，将读取或调用该 Skill 作为任务的第一步，并按其使用说明执行。若会话没有对应 Skill、Skill tool 或调用方式，不要假定它们存在；继续使用可用工具完成任务。

常见请求与 Skill 的对应关系（仅在对应 Skill 可用时使用）：

- 产品想法、是否值得开发、头脑风暴 → `office-hours`
- Bug、错误、故障原因、500 错误 → `investigate`
- 发布、部署、推送、创建 PR → `ship`
- QA、测试站点、寻找问题 → `qa`
- 代码评审、检查 diff → `review`
- 发布后更新文档 → `document-release`
- 周回顾 → `retro`
- 设计系统、品牌 → `design-consultation`
- 视觉审查、设计打磨 → `design-review`
- 架构评审 → `plan-eng-review`
- 保存进度、检查点、恢复 → `checkpoint`
- 代码质量、健康检查 → `health`
