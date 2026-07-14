---
name: fix-bug-by-dingding
description: Fix bug tasks tracked in a DingDing document or sheet. Use when the user asks to read a DingDing bug list/document and repair specified numbered bugs with mandatory before/after screenshots, self-comparison, relevant build/test verification, one commit per bug, the DingDing issue description as the commit message, and DingDing local column updated to done.
---

# Fix Bug By DingDing

## Overview

Use this skill to execute DingDing-tracked bug fixes end to end. The agent must discover the page/reproduction entry from the repository and DingDing row data, then follow the mandatory evidence and commit protocol: read the requested numbered rows, reproduce each issue, capture before/after screenshots, compare them yourself, make the smallest code change, run relevant build/tests, commit once per bug with the DingDing issue description, and update the DingDing `local` column to `done`.

## Mandatory Checklist

For every requested bug, complete all items below before moving to the next bug:

- Capture a before screenshot.
- Capture an after screenshot.
- Compare the before/after screenshots yourself and keep iterating until the bug is fixed.
- Start the local app yourself and locate the page/reproduction entry yourself.
- Run the relevant build and/or test command for the changed surface.
- Create exactly one commit for that bug.
- Use the DingDing problem description as the commit message.
- Update the DingDing `local` column to `done`.
- Read the DingDing row back and confirm `local` is `done`.

If a screenshot or verification command is technically impossible, stop and explain the blocker instead of silently skipping it.

## Workflow

1. Load the DingDing workflow first.
   - Use the `dws` skill/tooling to read the DingDing document or sheet.
   - Identify the requested bug numbers exactly. Treat user numbering as the source of truth.
   - When the first row is the title/header row, map bug number `N` to sheet row `N + 1`; for example, bug 55 is on sheet row 56.
   - Record the bug number, actual sheet row/range, page, issue description, assignee/status, and the `local` column cell for every requested bug.

2. Inspect the repository before editing.
   - Read `AGENTS.md` and any referenced local rules.
   - Read `package.json` files and workspace scripts to determine the correct install, dev, build, and test commands.
   - Check `git status -sb` and preserve unrelated user changes.
   - Use `rg`/targeted file reads to find the real implementation path.

3. Discover and start the reproduction entry yourself.
   - Treat the DingDing first column as the primary page clue, such as `航班列表页`, `首页`, `详情页`, or `预订页`.
   - Map that page clue to the project route by reading router files, page directories, app entry files, and existing links.
   - Start the relevant local dev server using the scripts discovered from `package.json`. If the default port is occupied, use the next available port and record the final URL.
   - Use Playwright/Playwriter to open the local page, interact with it, inspect console/network state, and capture screenshots.
   - If data is needed to reproduce the issue, prefer existing mocks, local API routes, intercepted network responses, or minimal browser-only fixtures. Do not commit throwaway reproduction fixtures unless they are real tests or required project mocks.
   - Ask the user only when reproduction requires external credentials, captcha/manual verification, unavailable private data, or a decision that cannot be inferred safely.

4. Fix one bug at a time.
   - Before changing code, reproduce or inspect the issue in the real local page.
   - Capture a before screenshot and save it with a stable path such as `/tmp/<repo>-bug<N>-before.png`.
   - Make a surgical code change that directly addresses the bug. Do not bundle unrelated cleanup.
   - Capture an after screenshot, compare it yourself against the before screenshot, and iterate until the visual or behavioral problem is fixed.

5. Verify each bug before committing.
   - Run the smallest meaningful build and/or test check for the changed surface. For this Vue/Vite project, prefer `rtk pnpm build:domestic` or the relevant app build.
   - If a standard check fails for pre-existing environment reasons, capture the exact reason and continue only when the bug-specific verification is still sound.
   - Re-check `git diff` so the commit contains only this bug’s intended changes.

6. Update DingDing and commit immediately after each fixed bug.
   - Set the bug row’s `local` cell to `done`.
   - Read the row back and confirm `local` displays `done`.
   - Stage only the files for this bug.
   - Commit once, with the commit message exactly equal to the DingDing issue description.
   - Verify `git log -1 --oneline` and `git status -sb` before moving to the next bug.

7. Finish cleanly.
   - Repeat steps 3-6 for each requested bug.
   - Stop any local dev server you started.
   - Final response in Chinese: list each bug number, commit hash/message, verification command result, screenshot paths, DingDing `done` confirmation, and current git status.

## Requirements

- One fixed bug equals one commit. Never combine multiple requested bugs in one commit unless the user explicitly changes this requirement.
- Commit message must be the problem description from DingDing, not a generated summary.
- Before and after screenshots are mandatory. If a bug is not visually representable, capture the closest observable before/after state and explain it.
- Self-comparison of screenshots is mandatory. Do not ask the user to compare for you.
- Page/reproduction discovery is the agent's responsibility. Do not require the user to provide a URL when the page can be inferred from the DingDing first column and repository routes.
- Relevant build/test verification is mandatory before each commit.
- Do not mark DingDing `local` as `done` until the fix is implemented, visually/behaviorally checked, and the after screenshot is captured.
- Do not push unless the user explicitly asks.
