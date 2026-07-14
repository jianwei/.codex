---
name: git-commit
description: 提交代码到 Git 版本库的完整工作流 Skill。当用户需要提交代码、推送代码、创建 commit、查看 git 状态、暂存文件、推送到远程仓库、创建分支、切换分支等任何 git 操作时，必须使用此 Skill。触发关键词：git commit、提交代码、push 代码、暂存文件、git add、推送到远程、创建分支、合并代码、git 操作、版本控制、代码提交、commit message。即使用户只是说"帮我提交一下"或"把代码推上去"也要触发此 Skill。
---

# Git Commit Skill

帮助用户将代码安全、规范地提交到 Git 版本库，包括状态检查、暂存、提交、推送等完整工作流。

---

## 工作流程概览

```
1. 检查 Git 环境   →   2. 查看状态        →   3. 暂存文件
        ↓
4. 撰写 Commit 信息   →   5. 执行提交    →   6. 推送到远程（必须）
        ↓
        7. 创建 Pull Request（可选，Fork 仓库时适用）
```

> **重要**：完整的提交流程必须包含 push 到远程仓库。仅执行本地 commit 而不 push，代码不会同步到远程，团队成员无法看到变更。只有在用户明确说"只需要本地提交"时才跳过 push。
>
> **第七步触发条件**：检测到仓库是 Fork 时（`git remote -v` 存在 `upstream` 远程，或用户明确提到 fork），push 完成后主动询问是否需要创建 PR 合回上游。

---

## 第一步：确认 Git 环境

```bash
# 确认是否在 git 仓库中
git rev-parse --is-inside-work-tree

# 查看当前分支
git branch --show-current

# 查看远程仓库配置
git remote -v
```

如果不在 Git 仓库中，提示用户先初始化：
```bash
git init
git remote add origin <仓库URL>
```

---

## 第二步：查看当前状态

```bash
# 查看整体状态
git status

# 查看具体变更内容
git diff          # 未暂存的变更
git diff --staged # 已暂存的变更
```

**解读状态输出：**
- `M` = 修改的文件
- `A` = 新增的文件
- `D` = 删除的文件
- `?? ` = 未跟踪的新文件
- `红色` = 未暂存，`绿色` = 已暂存

---

## 第三步：暂存文件（git add）

根据用户需求选择暂存策略：

```bash
# 暂存所有变更（最常用）
git add .

# 暂存指定文件
git add <文件路径> [文件路径2] ...

# 暂存指定目录
git add <目录路径>/

# 交互式暂存（精细选择）
git add -p

# 暂存已跟踪文件的所有变更（不含新文件）
git add -u
```

**注意事项：**
- 检查 `.gitignore` 是否已忽略不需要提交的文件（如 `node_modules/`、`.env`、构建产物等）
- 如果 `.gitignore` 不存在，提醒用户创建

---

## 第四步：撰写 Commit 信息

### Commit 信息规范（Conventional Commits）

格式：`<类型>(<范围>): <简短描述>`

**类型说明：**
| 类型 | 含义 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档变更 |
| `style` | 代码格式（不影响逻辑） |
| `refactor` | 代码重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具/依赖更新 |
| `perf` | 性能优化 |
| `ci` | CI/CD 配置 |

**示例：**
```
feat(auth): 添加 JWT 登录功能
fix(api): 修复用户列表分页错误
docs(readme): 更新安装说明
refactor(utils): 重构日期格式化工具函数
```

### 辅助用户生成 Commit 信息

如果用户没有提供 commit 信息，分析 `git diff --staged` 的内容，自动建议合适的 commit 信息，并询问用户确认或修改。

---

## 第五步：执行提交

```bash
# 标准提交
git commit -m "<commit信息>"

# 带详细描述的提交
git commit -m "<简短标题>" -m "<详细说明>"

# 修改最后一次提交（未推送时）
git commit --amend -m "<新的commit信息>"

# 跳过暂存，直接提交所有已跟踪文件的变更
git commit -am "<commit信息>"
```

提交后验证：
```bash
# 查看最新提交
git log --oneline -5
```

---

## 第六步：推送到远程仓库（必须执行）

**这是工作流的最后一步，必须完成才算真正提交成功。**

```bash
# 推送到当前分支对应的远程（最常用）
git push

# 首次推送，设置上游分支
git push -u origin <分支名>

# 推送到指定远程和分支
git push <远程名> <分支名>

# 强制推送（危险！仅在确认安全时使用）
git push --force-with-lease
```

推送后验证：
```bash
# 确认本地与远程同步
git status
# 应显示：Your branch is up to date with 'origin/<分支名>'
```

**推送失败常见原因及处理：**
- `rejected` / `non-fast-forward`：远程有新提交，需先 `git pull --rebase` 再重新 push
- `no upstream branch`：首次推送，改用 `git push -u origin <分支名>`
- 认证失败：检查 SSH key 或 Personal Access Token 是否配置正确

---

## 第七步：创建 Pull Request（可选，Fork 仓库适用）

### 7.1 检测是否为 Fork 仓库

```bash
# 查看远程配置，若存在 upstream 则为 fork 仓库
git remote -v

# 典型 fork 仓库的输出：
# origin    https://github.com/你的用户名/项目名.git (fetch)
# origin    https://github.com/你的用户名/项目名.git (push)
# upstream  https://github.com/原作者/项目名.git (fetch)
# upstream  https://github.com/原作者/项目名.git (push)
```

如果检测到 `upstream` 远程，或用户明确提到这是 fork 仓库，push 完成后**主动询问**用户是否需要创建 PR。

---

### 7.2 自动生成 PR Message

**在提交 PR 之前，必须先自动生成 PR Message，无需等待用户提供。**

收集以下信息作为生成依据：

```bash
# 1. 获取与上游的 commit 差异
git log upstream/main..HEAD --oneline

# 2. 获取完整代码变更
git diff upstream/main...HEAD

# 3. 获取当前分支名（可作为功能上下文线索）
git branch --show-current

# 4. 查看项目结构（辅助理解变更范围）
ls -la
```

根据以上信息，**严格按照以下模板**自动生成完整的 PR Message：

```markdown
# 创建 PR

## 背景
[根据 git diff 和 commit 历史，分析并阐述：当前存在的具体问题、用户需求或技术债务；
引发本次改动的业务背景、线上异常、交互缺陷、性能瓶颈等；
旧有方案的不足、影响面和本次变更的推动力；
如有历史方案演进信息，一并补充。]

## 目的
[列举本次 PR 需解决的全部问题和实现目标，包括：
功能新增、现有功能优化、Bug 修复、性能提升、代码重构等；
预期达成的业务/技术效果、用户收益；
安全性、易用性、稳定性等多角度目标。]

## 实现方案
[细致说明实现思路，包括：
- 主要技术选型及替换原因
- 重要数据结构、核心算法的设计说明
- 涉及的核心模块及其关系
- 关键实现流程（如有时序图、流程图等，用 Markdown 表示）
- 兼容性或扩展性考虑
如有关键代码片段，可适当摘录说明。]

## 测试 / 影响范围
[说明测试措施，包括：
- 单元测试、集成测试覆盖范围
- 主要测试用例和核心验证点
- 影响的业务模块、用户场景、上下游依赖
- 风险点、预期表现和边界条件
- 灰度发布或监控方案（如适用）]

---
提交人：<git config user.name>
提交日期：<当前日期 YYYY-MM-DD>
分支：<当前分支名>
```

生成后，向用户展示完整内容，并询问是否需要修改，确认后再进行后续步骤。

---

### 7.3 将 PR Message 追加写入 PR.md

PR Message 确认后，**必须**将内容追加写入项目根目录的 `PR.md` 文件：

```bash
# 检查 PR.md 是否存在
ls PR.md

# 追加写入（保留历史记录，用分隔线区分）
cat >> PR.md << 'EOF'

---

<此处填入完整 PR Message 内容>
EOF

# 验证写入成功
tail -20 PR.md
```

**写入规则：**
- 每条 PR 记录之间用 `---` 分隔线区分
- 追加方式写入，**绝不覆盖**已有内容
- 写入后将 `PR.md` 一并提交到本地仓库（`git add PR.md && git commit --amend --no-edit`）

---

### 7.4 提交 PR

确认 PR Message 并写入 PR.md 后，选择以下方式提交：

**方式一：GitHub CLI（推荐）**

```bash
# 检查是否安装
gh --version

# 从 fork 分支 → 上游默认分支创建 PR
gh pr create \
  --repo <上游用户名>/<仓库名> \
  --head <你的用户名>:<分支名> \
  --base main \
  --title "<从 PR Message 提取的标题>" \
  --body-file PR.md
```

**方式二：GitLab CLI**

```bash
glab mr create \
  --source-branch <分支名> \
  --target-branch main \
  --title "<PR 标题>" \
  --description "$(cat PR.md | tail -n +<本次PR起始行>)"
```

**方式三：生成网页链接（CLI 不可用时）**

输出以下链接，引导用户点击并粘贴已生成的 PR Message：

```
# GitHub
https://github.com/<上游用户名>/<仓库名>/compare/main...<你的用户名>:<分支名>

# GitLab
https://gitlab.com/<上游用户名>/<仓库名>/-/merge_requests/new?merge_request[source_branch]=<分支名>
```

---

## 常见场景处理

### 场景一：存在冲突
```bash
# 先拉取远程最新代码
git pull --rebase origin <分支名>

# 解决冲突后继续
git rebase --continue

# 或者中止 rebase
git rebase --abort
```

### 场景二：误提交敏感信息
```bash
# 撤销最后一次提交（保留文件变更）
git reset --soft HEAD~1

# 从暂存中移除敏感文件
git reset HEAD <敏感文件>

# 重新提交
git commit -m "..."
```

### 场景三：需要创建新分支再提交
```bash
# 创建并切换到新分支
git checkout -b <新分支名>

# 或 (git >= 2.23)
git switch -c <新分支名>

# 再执行暂存和提交...
```

### 场景四：临时保存工作进度
```bash
# 暂存当前工作（不提交）
git stash push -m "<描述>"

# 切换分支处理其他事项后恢复
git stash pop
```

---

## 安全检查清单

在提交前，建议检查以下事项：

- [ ] `.env` 等环境变量文件已在 `.gitignore` 中
- [ ] 没有硬编码的密码、API Key、Token
- [ ] 没有提交不必要的大文件（如二进制、日志）
- [ ] commit 信息清晰描述了变更内容
- [ ] 代码已经过基本测试

---

## 参考：常用 Git 命令速查

```bash
git status                    # 查看状态
git log --oneline --graph     # 查看提交历史（图形化）
git diff HEAD                 # 查看所有未提交变更
git show <commit-hash>        # 查看某次提交详情
git tag -a v1.0 -m "版本1.0" # 创建标签
git push origin --tags        # 推送所有标签
```

---

## 执行原则

1. **push 是必须的**：每次提交后默认执行 `git push`，确保代码同步到远程。只有用户明确说"只本地提交"才跳过
2. **展示结果**：每步操作后展示命令输出，让用户了解发生了什么
3. **错误处理**：遇到错误时解释原因并提供解决方案，不要静默失败
4. **force push 需确认**：`--force` 或 `--force-with-lease` 等破坏性操作执行前必须向用户确认
5. **最小权限**：默认只对用户明确指定的文件/分支进行操作