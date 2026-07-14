# Coding Agent — 完整提示模板

## 核心设计：run-docs.sh 用 `-p` 传 prompt，每个 task 独立子进程

`run-docs.sh` 通过 `claude -p "..."` 每次启动全新子进程处理一个 task。
**不依赖任何 slash command**，prompt 直接作为参数传入。

```
bash run-docs.sh
    │
    while 还有未完成任务:
        claude -p "$(cat .coding-agent-prompt.txt)"   ← 新子进程，全新上下文
            └── 完成 1 个 task → git commit → 输出 TASK_DONE → exit 0
    └── 读到 TASK_DONE → 继续循环
    └── 读到 ALL_DONE  → 结束
```

---

## run-docs.sh 模板（Initializer 负责生成此文件）

```bash
#!/bin/bash
# run-docs.sh — 全自动文档生成驱动脚本
# 用法：bash run-docs.sh

cd "$(dirname "$0")"
MAX_TASKS=200
COUNT=0

echo "🚀 启动全自动文档生成..."
python3 -c "
import json
d = json.load(open('doc-tasks.json'))
done = sum(1 for t in d['tasks'] if t['passes'])
print(f'📋 项目：{d[\"project\"]}  |  📁 目录：{d[\"docs_dir\"]}  |  进度：{done}/{d[\"total\"]}')
"
echo ""

while [ $COUNT -lt $MAX_TASKS ]; do
  COUNT=$((COUNT + 1))

  # 检查剩余任务
  REMAINING=$(python3 -c "
import json
d = json.load(open('doc-tasks.json'))
print(len([t for t in d['tasks'] if not t['passes']]))
")

  if [ "$REMAINING" -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════╗"
    echo "║           🎉 全部文档任务已完成！                 ║"
    echo "╚══════════════════════════════════════════════════╝"
    python3 -c "
import json
d = json.load(open('doc-tasks.json'))
print(f'📁 {d[\"docs_dir\"]}  🤖 {d[\"model\"]}  📊 {d[\"total\"]}/{d[\"total\"]} 个任务')
"
    break
  fi

  # 显示下一个任务
  python3 -c "
import json
d = json.load(open('doc-tasks.json'))
done = d['total'] - $REMAINING
r = sorted([t for t in d['tasks'] if not t['passes']], key=lambda t:(t['priority'],t['seq']))[0]
print(f'--- [{done+1}/{d[\"total\"]}] #{r[\"id\"]}：{r[\"description\"]}')
"

  # 用 -p 直接传 prompt，启动全新子进程
  # --allowedTools 限定工具范围
  OUTPUT=$(claude -p "$(cat .coding-agent-prompt.txt)" \
    --allowedTools "Bash,Read" 2>&1)
  EXIT_CODE=$?

  # 打印关键输出行
  echo "$OUTPUT" | grep -E "^(✅|❌|📊|TASK_DONE|ALL_DONE|⚠️|📄|\[docs)" | tail -8

  if echo "$OUTPUT" | grep -q "ALL_DONE"; then
    echo "🎉 全部完成"
    break
  fi

  if echo "$OUTPUT" | grep -q "TIMEOUT"; then
    echo "⚠️ 超过1小时，停止。重新运行 /react-reverse-docs 选择是否继续。"
    break
  fi

  if [ $EXIT_CODE -ne 0 ]; then
    echo "⚠️ 子进程异常 (exit $EXIT_CODE)，跳过继续..."
  fi

  echo ""
done

echo "✅ run-docs.sh 结束（共 $COUNT 轮）"
```

---

## .coding-agent-prompt.txt（Initializer 负责生成此文件）

`run-docs.sh` 读取此文件作为每次子进程的 prompt。内容如下：

```
你是 React 项目文档生成专家。当前工作目录已包含 doc-tasks.json。

请严格按照以下步骤执行，完成 1 个文档任务后立即退出，不要继续下一个：

## Step 0：读状态 + 时间差检查

执行：
python3 -c "
import json, datetime, sys
d = json.load(open('doc-tasks.json'))
started = d.get('session_started_at','')
remaining = [t for t in d['tasks'] if not t['passes']]
done = d['total'] - len(remaining)
print(f'进度：{done}/{d[\"total\"]}  目录：{d[\"docs_dir\"]}')
if not remaining:
    print('ALL_DONE')
    sys.exit(0)
if started:
    import datetime
    delta = datetime.datetime.now() - datetime.datetime.strptime(started,'%Y-%m-%d %H:%M:%S')
    if delta.total_seconds() > 3600:
        print(f'TIMEOUT: {int(delta.total_seconds()/60)} 分钟')
        sys.exit(1)
t = sorted(remaining, key=lambda x:(x['priority'],x['seq']))[0]
print(f'下一个：[{t[\"seq\"]}/{d[\"total\"]}] #{t[\"id\"]} {t[\"description\"]}')
print(f'TASK_ID={t[\"id\"]}')
print(f'DOCS_DIR={d[\"docs_dir\"]}')
"

若输出 ALL_DONE 或 TIMEOUT，直接 exit，不做任何操作。

## Step 1：检查上次遗留文件

验证最近一个 passes=true 的任务其 target_file 是否存在且非空。
文件缺失则重新生成，然后继续。

## Step 2：选取本次任务（1个）

从 doc-tasks.json 选 passes=false、priority 最小、seq 最小的任务。

## Step 3：读源文件，生成文档

- 先读取对应模板文件（路径在 references/ 下）
- 再读取 source_files 中的源文件
- 用 bash cat > 写入 target_file，写完用 ls -lh 验证
- 禁止使用 Write 工具
- 确保目录存在：mkdir -p $(dirname target_file)

## Step 4：bash 验证

必须执行：
ls -lh [target_file]
wc -l [target_file]

没看到 ls 实际输出不允许继续。

## Step 5：更新 doc-tasks.json

python3 << 'PYEOF'
import json, subprocess
d = json.load(open('doc-tasks.json'))
now = subprocess.check_output('date +"%Y-%m-%d %H:%M:%S"', shell=True).decode().strip()
for t in d['tasks']:
    if t['id'] == 'TASK_ID_HERE':
        t['passes'] = True
        t['completed_at'] = now
d['completed'] = sum(1 for t in d['tasks'] if t['passes'])
json.dump(d, open('doc-tasks.json','w'), ensure_ascii=False, indent=2)
print(f"📊 {d['completed']}/{d['total']}")
PYEOF

## Step 6：更新 doc-progress.md

cat >> DOCS_DIR/doc-progress.md << EOF
### $(date +"%Y-%m-%d %H:%M:%S")
- ✅ 完成 #TASK_ID：TASK_DESC
- 📄 TARGET_FILE
- 📊 M/N 完成
EOF

## Step 7：git commit

git add -A
git commit -m "docs(CATEGORY): TASK_DESC

- #TASK_ID  进度：M/N
- $(date +'%Y-%m-%d %H:%M:%S')"

git log --oneline -1

## Step 8：输出状态后退出

python3 -c "
import json
d = json.load(open('doc-tasks.json'))
r = [t for t in d['tasks'] if not t['passes']]
if r:
    nxt = sorted(r, key=lambda t:(t['priority'],t['seq']))[0]
    print(f'TASK_DONE 还剩 {len(r)} 个，下一个 #{nxt[\"id\"]}')
else:
    print('ALL_DONE')
"

⚠️ 完成以上步骤后立即停止，不要自行继续下一个任务。
```

---

## 每次子进程执行规则

- **只完成 1 个 task，然后退出**
- 写文件必须用 `bash cat >`，禁用 Write 工具
- 自检必须看到 `ls -lh` 的实际输出
- 末尾必须输出 `TASK_DONE` 或 `ALL_DONE`，供 `run-docs.sh` 判断

## 模板对照表

| category | 模板路径 |
|---------|---------|
| architecture | references/tpl-architecture.md |
| api | references/tpl-api.md |
| page | references/tpl-prd.md |
| component | references/tpl-component.md |
| state | references/tpl-state.md |
| tech-debt | references/tpl-tech-debt.md |

## 异常处理

- 文件写入失败：`mkdir -p` 确保目录，重试最多 3 次，仍失败则跳过记录 error
- 源文件不存在：文档中注明，基于已有信息生成，task 加 `warning` 字段
- 子进程崩溃：`run-docs.sh` 捕获非零退出码，打印警告，继续循环