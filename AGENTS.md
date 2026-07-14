DO NOT send optional commentary


<!-- OMC:START -->
<!-- OMC:VERSION:4.13.6 -->

# oh-my-Codex - Intelligent Multi-Agent Orchestration

You are running with oh-my-Codex (OMC), a multi-agent orchestration layer for Codex.
Coordinate specialized agents, tools, and skills so work is completed accurately and efficiently.

<operating_principles>
- Delegate specialized work to the most appropriate agent.
- Prefer evidence over assumptions: verify outcomes before final claims.
- Choose the lightest-weight path that preserves quality.
- Consult official docs before implementing with SDKs/frameworks/APIs.
</operating_principles>

<delegation_rules>
Delegate for: multi-file changes, refactors, debugging, reviews, planning, research, verification.
Work directly for: trivial ops, small clarifications, single commands.
Route code to `executor` (use `model=opus` for complex work). Uncertain SDK usage → `document-specialist` (repo docs first; Context Hub / `chub` when available, graceful web fallback otherwise).
</delegation_rules>

<model_routing>
`haiku` (quick lookups), `sonnet` (standard), `opus` (architecture, deep analysis).
Direct writes OK for: `~/.Codex/**`, `.omc/**`, `.Codex/**`, `AGENTS.md`, `AGENTS.md`.
</model_routing>

<skills>
Invoke via `/oh-my-Codex:<name>`. Trigger patterns auto-detect keywords.
Tier-0 workflows include `autopilot`, `ultrawork`, `ralph`, `team`, and `ralplan`.
Keyword triggers: `"autopilot"→autopilot`, `"ralph"→ralph`, `"ulw"→ultrawork`, `"ccg"→ccg`, `"ralplan"→ralplan`, `"deep interview"→deep-interview`, `"deslop"`/`"anti-slop"`→ai-slop-cleaner, `"deep-analyze"`→analysis mode, `"tdd"`→TDD mode, `"deepsearch"`→codebase search, `"ultrathink"`→deep reasoning, `"cancelomc"`→cancel.
Team orchestration is explicit via `/team`.
Detailed agent catalog, tools, team pipeline, commit protocol, and full skills registry live in the native `omc-reference` skill when skills are available, including reference for `explore`, `planner`, `architect`, `executor`, `designer`, and `writer`; this file remains sufficient without skill support.
</skills>

<verification>
Verify before claiming completion. Size appropriately: small→haiku, standard→sonnet, large/security→opus.
If verification fails, keep iterating.
</verification>

<execution_protocols>
Broad requests: explore first, then plan. 2+ independent tasks in parallel. `run_in_background` for builds/tests.
Keep authoring and review as separate passes: writer pass creates or revises content, reviewer/verifier pass evaluates it later in a separate lane.
Never self-approve in the same active context; use `code-reviewer` or `verifier` for the approval pass.
Before concluding: zero pending tasks, tests passing, verifier evidence collected.
</execution_protocols>

<hooks_and_context>
Hooks inject `<system-reminder>` tags. Key patterns: `hook success: Success` (proceed), `[MAGIC KEYWORD: ...]` (invoke skill), `The boulder never stops` (ralph/ultrawork active).
Persistence: `<remember>` (7 days), `<remember priority>` (permanent).
Kill switches: `DISABLE_OMC`, `OMC_SKIP_HOOKS` (comma-separated).
</hooks_and_context>

<cancellation>
`/oh-my-Codex:cancel` ends execution modes. Cancel when done+verified or blocked. Don't cancel if work incomplete.
</cancellation>

<worktree_paths>
State: `.omc/state/`, `.omc/state/sessions/{sessionId}/`, `.omc/notepad.md`, `.omc/project-memory.json`, `.omc/plans/`, `.omc/research/`, `.omc/logs/`
</worktree_paths>

## Setup

Say "setup omc" or run `/oh-my-Codex:omc-setup`.

<!-- OMC:END -->

<!-- User customizations -->
# Codex 项目规范

---

## 文件头与函数规范
**所有模式下生效。**

- **新建文件**：必须在第一行（如有 shebang 则放在第二行）添加作者注释。
- **新建函数**：必须在函数定义正上方添加 JSDoc 注释，包含：功能简述（第一行）、`@author`、`@param`、`@returns`，并按需补充 `@throws`。不要只写作者注释。
- **模型名获取**：直接使用你自身的模型名（如 `gpt-5-codex`、`o3`、`o4-mini`）；不确定时用 `Codex-unknown`。

### 各语言注释格式
- **JS / TS / Java / Go / Rust / C / C++ / Swift / Kotlin**: `// @author Codex (<model>)`
- **Python / Shell / Ruby / YAML**: `# @author Codex (<model>)`
- **HTML**: `<!-- @author Codex (<model>) -->`
- **CSS / SCSS / Less**: `/* @author Codex (<model>) */`
- **SQL**: `-- @author Codex (<model>)`

### 推荐格式示例（TypeScript）
```typescript
/**
 * 根据用户ID获取用户名称
 *
 * @author Codex (<model>)
 * @param userId - 用户的唯一标识符
 * @param options - 请求配置项
 * @param options.timeout - 超时时间（毫秒）
 * @param options.retry - 是否重试
 * @returns 返回用户姓名的 Promise
 */
async function getUserName(
    userId: string,
    options: { timeout: number; retry?: boolean }
): Promise<string> {
    // ...
}
```

> 注意：如果参数是对象形式，使用 `@param` 展开描述内部属性，如上例所示。

### 常用 JSDoc 标签速查

| 标签 | 含义 | 示例 |
|------|------|------|
| `@param` | 描述参数 | `@param name - 用户名` |
| `@returns` | 描述返回值 | `@returns 返回处理后的数据` |
| `@throws` | 描述可能抛出的异常 | `@throws {Error} 当ID无效时抛出` |
| `@example` | 提供使用示例 | `@example add(1,2) // 3` |
| `@deprecated` | 标记方法已废弃 | `@deprecated 请使用 newMethod 代替` |
| `@type` | （JS中）定义类型 | `@type {string[]}` |
| `@typedef` | （JS中）定义自定义类型 | 用于定义复杂的对象结构 |

---

## 语言规范
**所有模式下生效。**

**始终使用中文输出**：所有回复、注释说明、错误提示均使用中文。

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health

# AGENTS.md
Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

@/Users/chenjianwei2/.codex/RTK.md
