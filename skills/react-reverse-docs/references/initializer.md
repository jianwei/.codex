# Initializer Agent — 完整提示模板

## 前置说明

用户已在启动时完成了一次性确认，提供了：
- 项目根目录路径
- 特别注意事项（如有）

**本 Agent 全程自动执行，不向用户提任何问题。**
执行完成后自动衔接 Coding Agent，无需等待用户指令。

---

## Step 0：自动识别模型名，确定目录名

```bash
# Agent 自我声明（最高优先级）：
# 你（Agent）直接使用自己已知的模型标准名称，转小写，空格和斜杠替换为 -
# 例如：Claude Sonnet 4.6 → claude-sonnet-4-6
#       GPT-4o           → gpt-4o
#       Kimi K2          → kimi-k2
#       DeepSeek V3      → deepseek-v3

# 若无法自我声明，按顺序读取以下环境变量：
MODEL_NAME="${ANTHROPIC_MODEL:-${OPENAI_MODEL:-${MODEL_NAME_ENV:-}}}"

# 仍为空则扫描配置文件：
if [ -z "$MODEL_NAME" ]; then
  for f in .env .env.local .cursorrules .claude.json; do
    [ -f "$f" ] && MODEL_NAME=$(grep -i "^model" "$f" 2>/dev/null | head -1 | sed 's/.*[:=]\s*//' | tr -d '"' | xargs) && [ -n "$MODEL_NAME" ] && break
  done
fi

# 兜底
MODEL_NAME="${MODEL_NAME:-unknown-model}"
MODEL_NAME=$(echo "$MODEL_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[ /]/-/g')

# 目录名永远只用模型名，不加日期不加后缀
# 已存在则直接覆盖，不新建新目录
DOCS_DIR="project-docs-${MODEL_NAME}"
mkdir -p "$DOCS_DIR"

echo "模型：$MODEL_NAME  →  目录：$DOCS_DIR"
```

---

## Step 1：扫描项目结构

```bash
# 切换到用户在启动时确认的项目根目录
cd [启动时用户提供的项目路径]

find src -type f \( -name "*.jsx" -o -name "*.tsx" -o -name "*.js" -o -name "*.ts" \) | sort
cat package.json
cat src/router/index.js 2>/dev/null || cat src/App.jsx 2>/dev/null
ls src/api/ 2>/dev/null || ls src/services/ 2>/dev/null
ls src/store/ 2>/dev/null || ls src/redux/ 2>/dev/null || ls src/zustand/ 2>/dev/null
```

遇到目录不存在时跳过，不停下来询问，继续扫描其他路径。

---

## Step 2：生成 doc-tasks.json

基于扫描结果生成完整任务清单，写入项目根目录 `doc-tasks.json`（**不在** $DOCS_DIR 内，放根目录方便 Coding Agent 直接读取）。

任务分类与优先级：

| 类别 | priority | 说明 |
|------|---------|------|
| architecture | 1 | 整体架构，最先做 |
| state | 2 | 状态管理 |
| api | 3 | 接口文档，每个文件一个任务 |
| page | 4 | 页面PRD，每个路由一个任务 |
| component | 5 | 重要复用组件 |
| tech-debt | 6 | 技术债务，最后做 |

每个任务字段：
- `seq`：从 1 递增，仅展示
- `id`：唯一标识（arch-001 / api-003 等）
- `category`：类别
- `description`：中文一句话说明
- `target_file`：以 `$DOCS_DIR/` 开头的输出路径
- `source_files`：要分析的源文件列表
- `priority`：数字
- `passes`：初始 false
- `created_at`：`date +"%Y-%m-%d %H:%M:%S"` 统一写入
- `completed_at`：初始 null

根节点必须包含：
```json
{
  "project": "（package.json 中的 name）",
  "model": "（$MODEL_NAME）",
  "docs_dir": "（$DOCS_DIR）",
  "created_at": "（当前时间）",
  "total": 0,
  "completed": 0,
  "tasks": []
}
```

⚠️ 每个 api 文件、每个页面、每个重要组件各自独立任务，不合并。
⚠️ 用户若指定了"忽略某些目录"，扫描时跳过，不生成对应任务。

**写入 doc-tasks.json 必须用 bash，写完验证：**

```bash
cat > doc-tasks.json << 'JSONEOF'
{
  "project": "...",
  "model": "...",
  "docs_dir": "...",
  "created_at": "（当前时间）",
  "session_started_at": "（当前时间，与 created_at 相同）",
  "total": N,
  "completed": 0,
  "tasks": [...]
}
JSONEOF

# 验证写入成功
ls -lh doc-tasks.json
python3 -c "import json; d=json.load(open('doc-tasks.json')); print(f'✅ 任务数：{d[\"total\"]}，session_started_at：{d[\"session_started_at\"]}')"
```

> `session_started_at`：本次初始化时间，**用于下次启动时判断是否超过 1 小时**。
> 全新开始时更新此字段，继续执行时保持不变。

---

## Step 3：生成 $DOCS_DIR/doc-progress.md

**必须用 bash `cat >` 写文件，写完用 `ls -lh` 验证：**

```bash
cat > "$DOCS_DIR/doc-progress.md" << 'PROGRESSEOF'
# 文档生成进度

## 项目信息
- 项目名：（package.json name）
- 使用模型：（$MODEL_NAME）
- 文档目录：（$DOCS_DIR）
- 初始化时间：（当前时间 2026-03-05 09:16:18）
- 总任务数：N
- 已完成：0

## 技术栈概览
（从 package.json 提取：React版本、路由库、状态管理、UI库、构建工具等）

## 会话记录
### Session 1（Initializer）- （当前时间）
- ✅ 自动识别模型：（$MODEL_NAME）
- ✅ 确定文档目录：（$DOCS_DIR）
- ✅ 完成项目扫描
- ✅ 生成 doc-tasks.json（N 个任务）
- ✅ 建立目录结构
- ✅ 自动衔接 Coding Agent 开始生成文档
PROGRESSEOF

# 写完验证
ls -lh "$DOCS_DIR/doc-progress.md" || echo "❌ 写入失败，重试"
```

---

## Step 4：编写 $DOCS_DIR/init.sh

根据项目实际情况自行编写，必须包含：

1. 显示当前时间和文档目录名
2. 读取根目录 `doc-tasks.json`，输出总数/已完成/待完成及百分比
3. 按 seq 逐行展示所有任务状态：
   - `[seq/total] ✅ #id description（耗时 N 分钟）`
   - `[seq/total] ⏳ #id description  ← 下一个`
   - `[seq/total] ○  #id description`
4. 输出 doc-progress.md 最近 20 行

注意：`doc-tasks.json` 在项目根目录，脚本路径用 `SCRIPT_DIR` 自适应。

---

## Step 5：建立 $DOCS_DIR/ 目录结构

```bash
mkdir -p $DOCS_DIR/api $DOCS_DIR/pages $DOCS_DIR/components $DOCS_DIR/state
touch $DOCS_DIR/architecture.md $DOCS_DIR/tech-debt.md
```

---

## Step 6：生成 run-docs.sh 和 .coding-agent-prompt.txt

**两个文件都必须生成，run-docs.sh 读取 .coding-agent-prompt.txt 作为每轮子进程的 prompt。**

### 6a：生成 .coding-agent-prompt.txt

```bash
cat > .coding-agent-prompt.txt << 'PROMPTEOF'
你是 React 项目文档生成专家。当前工作目录已包含 doc-tasks.json。

请严格按照以下步骤执行，完成 1 个文档任务后立即退出，不要继续下一个任务。

## Step 0：读状态 + 时间差检查

```bash
python3 << 'PYEOF'
import json, datetime, sys
d = json.load(open('doc-tasks.json'))
started = d.get('session_started_at','')
remaining = [t for t in d['tasks'] if not t['passes']]
done = d['total'] - len(remaining)
print(f'进度：{done}/{d["total"]}  目录：{d["docs_dir"]}')
if not remaining:
    print('ALL_DONE')
    sys.exit(0)
if started:
    delta = datetime.datetime.now() - datetime.datetime.strptime(started,'%Y-%m-%d %H:%M:%S')
    if delta.total_seconds() > 3600:
        print(f'TIMEOUT: {int(delta.total_seconds()/60)} 分钟，请重新运行 /react-reverse-docs')
        sys.exit(0)
t = sorted(remaining, key=lambda x:(x['priority'],x['seq']))[0]
print(f'下一个：[{t["seq"]}/{d["total"]}] #{t["id"]} {t["description"]}')
PYEOF
```

若输出 ALL_DONE 或 TIMEOUT，直接停止，不做任何操作。

## Step 1：检查上次遗留

验证最近一个 passes=true 的任务其 target_file 是否存在且非空。
文件缺失则重新生成，然后继续。

## Step 2：选取本次任务（只选 1 个）

从 doc-tasks.json 选 passes=false、priority 最小、seq 最小的任务。

## Step 3：读模板 + 读源文件 + 生成文档

先读取对应模板（references/ 目录下），再读源文件，生成完整文档内容。

写文件：
```bash
mkdir -p "$(dirname TARGET_FILE)"
cat > TARGET_FILE << 'DOCEOF'
[完整文档内容]
DOCEOF
ls -lh TARGET_FILE
```

禁止使用 Write 工具，只用 bash cat >。

## Step 4：验证

```bash
ls -lh TARGET_FILE
wc -l TARGET_FILE
```

必须看到 ls 实际输出才能继续。

## Step 5：更新 doc-tasks.json

```bash
python3 << 'PYEOF'
import json, subprocess
d = json.load(open('doc-tasks.json'))
now = subprocess.check_output('date +"%Y-%m-%d %H:%M:%S"', shell=True).decode().strip()
for t in d['tasks']:
    if t['id'] == 'TASK_ID_PLACEHOLDER':
        t['passes'] = True
        t['completed_at'] = now
        print(f"✅ #{t['id']} 完成")
d['completed'] = sum(1 for t in d['tasks'] if t['passes'])
json.dump(d, open('doc-tasks.json','w'), ensure_ascii=False, indent=2)
print(f"📊 {d['completed']}/{d['total']}")
PYEOF
```

## Step 6：更新 doc-progress.md

```bash
DOCS_DIR=$(python3 -c "import json; print(json.load(open('doc-tasks.json'))['docs_dir'])")
NOW=$(date +"%Y-%m-%d %H:%M:%S")
echo "" >> "$DOCS_DIR/doc-progress.md"
echo "### $NOW" >> "$DOCS_DIR/doc-progress.md"
echo "- ✅ 完成 #TASK_ID：TASK_DESC" >> "$DOCS_DIR/doc-progress.md"
echo "- 📄 TARGET_FILE" >> "$DOCS_DIR/doc-progress.md"
```

## Step 7：git commit

```bash
git add -A
git commit -m "docs(CATEGORY): TASK_DESC

- #TASK_ID  进度：M/N
- $(date +'%Y-%m-%d %H:%M:%S')"
git log --oneline -1
echo "✅ commit 完成"
```

## Step 8：输出结束标记，停止

```bash
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
```

⚠️ 输出 TASK_DONE 或 ALL_DONE 后立即停止，不要继续下一个任务。
PROMPTEOF

ls -lh .coding-agent-prompt.txt
echo "✅ .coding-agent-prompt.txt 已生成"
```

### 6b：生成 run-docs.sh

```bash
cat > run-docs.sh << 'RUNDOCSEOF'
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
print(f'📋 {d[\"project\"]}  📁 {d[\"docs_dir\"]}  进度：{done}/{d[\"total\"]}')
"
echo ""

while [ $COUNT -lt $MAX_TASKS ]; do
  COUNT=$((COUNT + 1))

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

  python3 -c "
import json
d = json.load(open('doc-tasks.json'))
done = d['total'] - $REMAINING
r = sorted([t for t in d['tasks'] if not t['passes']], key=lambda t:(t['priority'],t['seq']))[0]
print(f'--- [{done+1}/{d[\"total\"]}] #{r[\"id\"]}：{r[\"description\"]}')
"

  # 用 -p 直接传 prompt 文本，启动全新子进程，不依赖任何 slash command
  OUTPUT=$(claude -p "$(cat .coding-agent-prompt.txt)" \
    --allowedTools "Bash,Read" 2>&1)
  EXIT_CODE=$?

  echo "$OUTPUT" | grep -E "^(✅|❌|📊|TASK_DONE|ALL_DONE|⚠️|📄|\[docs)" | tail -8

  if echo "$OUTPUT" | grep -q "ALL_DONE"; then
    echo "🎉 全部完成"
    break
  fi

  if echo "$OUTPUT" | grep -q "TIMEOUT"; then
    echo "⚠️ 超过1小时，停止。请重新运行 /react-reverse-docs。"
    break
  fi

  if [ $EXIT_CODE -ne 0 ]; then
    echo "⚠️ 子进程异常 (exit $EXIT_CODE)，继续下一个..."
  fi

  echo ""
done

echo "✅ run-docs.sh 结束（共 $COUNT 轮）"
RUNDOCSEOF

chmod +x run-docs.sh
ls -lh run-docs.sh
echo "✅ run-docs.sh 已生成"
```

---

## Step 7：初始 git commit

```bash
git add -A
git commit -m "docs: 初始化 $DOCS_DIR/ 文档生成环境

- 模型：$MODEL_NAME
- 新建目录：$DOCS_DIR/
- 生成 doc-tasks.json（N 个任务）
- 生成 doc-progress.md / init.sh / run-docs.sh
- 建立子目录：api/ pages/ components/ state/

运行方式：bash run-docs.sh（全自动，无需介入）"
git log --oneline -1
```

---

## Step 8：提示用户启动

Initializer 完成后，输出：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 初始化完成！

📁 文档目录：$DOCS_DIR
📋 任务总数：N 个
🤖 生成模型：$MODEL_NAME

▶ 在终端运行以下命令开始全自动生成：

   bash run-docs.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```