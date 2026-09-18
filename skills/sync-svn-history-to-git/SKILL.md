---
name: sync-svn-history-to-git
description: 将一段 SVN 修订历史转换为基于指定 Git 提交的本地历史，保留每次有效修订的作者、日期和提交说明，并可创建新分支或安全快进既有目标分支。用于 SVN 到 Git 的增量迁移、补录历史，或在不切换当前工作树的前提下重建 Git 历史；不用于自动推送远端。
---

<!-- @author Codex (gpt-5.6-sol) -->

# SVN 历史同步到 Git

先确定交付目标，再预检、运行脚本并验证结果。整个流程不切换主工作树，也不推送。

## 确定目标

- 用户明确要求新建同步分支时，直接按用户指定的 `--base-ref` 和 `--new-branch` 执行。
- 用户没有要求新建分支时，先询问：`同步完成后合并到哪个分支？直接回车默认 master`。用户未填写或输入为空时，将目标设为 `master`，并显式传 `--merge-target master`。
- 快进既有目标前，脚本要求工作区干净、目标分支未在任何工作树检出，且目标提交是候选历史的祖先。若无法快进或需要 merge commit，停止并请用户确认后续方案；不得自动 merge、改写历史或 force。

## 预检

1. 确认当前目录属于目标 Git 仓库，且 `git`、`svn` 可用。
2. 确认 `--base-ref` 指向正确的基线提交，`--new-branch` 尚不存在。
3. 确认修订范围和访问权限。只给一个修订号时，它是起始修订，脚本通过 `svn info -r HEAD` 将结束修订解析为目标 SVN URL 当前 HEAD；给两个修订号时，它们是包含两端的闭区间，且第一个必须小于或等于第二个。
4. 默认排除 MTUNIU 的 `site`、`sitemap`、`topic`、`downloads` 四个顶层目录；额外目录每个传一次 `--exclude-root`。

## 执行

在目标 Git 仓库中运行：

```bash
python3 ~/.codex/skills/sync-svn-history-to-git/scripts/sync_svn_history.py \
  --base-ref <基线提交或引用> \
  --new-branch <新分支名> \
  --svn-url <SVN目录URL> \
  --revision <起始修订号> [结束修订号] \
  --exclude-root <可选的顶层目录>
```

`--revision` 接受 `r281571` 或 `281571` 格式。只填写一个值时，同步该修订到 SVN HEAD 的闭区间；填写两个值时，同步两者之间的闭区间。反序范围会明确报错。

旧参数 `--start <起始修订号> --end <结束修订号>` 继续兼容，但必须成对出现，且不能与 `--revision` 混用。

若要快进既有分支，用 `--merge-target <目标分支>` 替代 `--new-branch`；`--merge-target` 不带值时脚本默认使用 `master`。也可同时指定二者，在同一个引用事务中创建同步分支并快进目标。

默认排除集合为 `site,sitemap,topic,downloads`，重复使用 `--exclude-root` 会在该集合上追加。通用仓库若要取消这四项，显式添加 `--no-default-excludes`；此时仍可用 `--exclude-root <目录>` 添加自定义排除项。例如只排除 `generated`：

```bash
python3 ~/.codex/skills/sync-svn-history-to-git/scripts/sync_svn_history.py \
  --base-ref <基线> --new-branch <新分支> \
  --svn-url <SVN目录URL> --revision <起始> [结束] \
  --no-default-excludes --exclude-root generated
```

脚本通过临时 Git index 读取基线，对 SVN 的 A/M/D 变更逐次建树，并用 Git plumbing 命令在全部处理和内部验证成功后原子创建引用。目录复制会在对应修订完整物化；`svn:executable` 映射为 `100755`，`svn:special` 符号链接映射为 `120000`。非排除路径的纯属性修订也会保留为空提交；只包含排除目录或不影响该 SVN URL 的修订不会生成提交。Git 作者邮箱按 `<SVN作者>@<SVN仓库UUID>` 生成。

## 验证

```bash
git log --reverse --format='%H %an %aI %s' <base-ref>..<new-branch>
git diff --stat <base-ref>..<new-branch>
git ls-tree -r <new-branch>
git status --short
```

核对提交数量、作者、日期、说明、最终文件内容与模式，并确认基线引用和工作树未变化。若待新建分支已存在，脚本会拒绝执行。

推送属于独立的外部写操作。只有用户另行明确授权目标 remote 和 branch 后，才可执行 `git push`；本 Skill 和脚本均不自动推送。
