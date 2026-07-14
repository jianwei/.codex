# Playwriter 实战经验 & 问题排查

## 🔧 从实战日志提炼的优化规则

> 以下规则来自真实测试执行中反复出现的问题，必须严格遵守。

### 1. reset 后必须立即恢复 state.myPage，且只用一行

每次 `playwriter - reset` 后，`state` 被清空，下一个 execute **第一行**必须重新赋值：

```javascript
// reset 后的第一个 execute，第一行必须是这个
state.myPage = context.pages().find(p => p.url().includes('your-app-host')) ?? page
```

不要把 reset 后的恢复和其他操作混在一起，单独一次 execute 完成恢复和验证：

```javascript
// ✅ reset 后专门用一次 execute 恢复
state.myPage = context.pages().find(p => p.url().includes('your-app-host')) ?? page
console.log('页面恢复:', state.myPage.url())
```

---

### 2. evaluate 操作必须有返回值，不能依赖"no output"判断结果

```javascript
// ❌ 无法判断操作是否成功
await state.myPage.evaluate(() => {
  const input = document.querySelector('input[placeholder="选择表单字段"]')
  if (input) input.click()
})
// 结果：Code executed successfully (no output) ← 不知道有没有点到

// ✅ 必须返回操作结果
const result = await state.myPage.evaluate(() => {
  const input = document.querySelector('input[placeholder="选择表单字段"]')
  if (input) { input.click(); return 'clicked' }
  return 'not found'
})
console.log('点击结果:', result)
// 如果返回 'not found'，立即截图排查，不要继续往下执行
```

---

### 3. 操作失败后先截图，不要盲目重试

```javascript
// ❌ 表单字段选择失败后，盲目换选择器重试 3 次
// 第1次失败 → 换选择器 → 第2次失败 → 再换 → 第3次...

// ✅ 失败后立即截图，看清楚当前页面状态再决定下一步
const result = await state.myPage.evaluate(...)
if (result === 'not found') {
  // 先截图看清楚状态
  await screenshotWithAccessibilityLabels({ page: state.myPage })
  // 再根据截图决定怎么操作
}
```

---

### 4. 禁止用 page.goBack()，用 page.goto() 代替

```javascript
// ❌ goBack() 会超时
await state.myPage.goBack()

// ✅ 直接导航回目标页面
await state.myPage.goto('http://your-app-host/your-page', { waitUntil: 'domcontentloaded' })
```

---

### 5. snapshot 和操作不要合并在同一个 execute

```javascript
// ❌ 操作 + snapshot 合并，任一步超时整体失败
await state.myPage.evaluate(() => { ... })
await state.myPage.waitForTimeout(500)
await accessibilitySnapshot({ page: state.myPage })  // 幻觉函数 + 超时风险

// ✅ 操作一次 execute，查看结果单独一次 execute
// execute 1: 执行操作
const result = await state.myPage.evaluate(() => { ... })
console.log(result)

// execute 2: 确认结果
await screenshotWithAccessibilityLabels({ page: state.myPage })
```

---

### 6. waitForTimeout 全面替换对照表

| 场景 | ❌ 禁止 | ✅ 替代 |
|------|--------|--------|
| 等弹窗出现 | `waitForTimeout(500)` | `waitForSelector('.modal', { state: 'visible' })` |
| 等弹窗关闭 | `waitForTimeout(300)` | `waitForSelector('.modal', { state: 'hidden' })` |
| 等页面跳转 | `waitForTimeout(1500)` | `waitForURL('**/target**')` 或 `waitForLoadState('domcontentloaded')` |
| 等内容更新 | `waitForTimeout(200)` | `waitForFunction(() => document.querySelector('.result')?.textContent !== '')` |
| 无明确等待目标 | `waitForTimeout(任意值)` | 截图确认当前状态，改用条件等待 |

---

### 7. 两次 execute 获取 snapshot 可以合并

```javascript
// ❌ 浪费：操作后先 execute 一次，再 execute 一次拿 snapshot
// execute 1
await state.myPage.evaluate(() => { el.click() })
// execute 2  
await screenshotWithAccessibilityLabels({ page: state.myPage })

// ✅ 如果操作本身不会超时，可以在同一个 execute 里完成操作 + 截图
const result = await state.myPage.evaluate(() => { el.click(); return 'clicked' })
console.log(result)
await screenshotWithAccessibilityLabels({ page: state.myPage })
```

---

---

### 9. 控制上下文体积，避免溢出

> ⚠️ 重要认知：`clearAllLogs()` 和清理 `state` **只清空 Playwriter 内部缓存**，
> 无法清空 Claude Code 自身的对话上下文。
> Claude 的上下文是累积的，每一轮的代码、返回值、截图、日志都会占用空间，**无法主动清空**。

**能真正减少上下文占用的方式：**

#### ① 每个 TC 结束后清理 Playwriter 内部缓存（有限效果）

```javascript
// TC 结束后执行
clearAllLogs()
const _page = state.myPage
Object.keys(state).forEach(k => delete state[k])
state.myPage = _page
```

#### ② 减少每次 execute 的输出量（效果显著）

```javascript
// ❌ 会产生大量上下文：打印整个数组、整段 HTML
console.log(await state.myPage.evaluate(() => document.body.innerHTML))
const logs = await getLatestLogs({ count: 50 })

// ✅ 只打印关键信息
console.log('表单字段:', destValue)
const logs = await getLatestLogs({ count: 10 })  // 够用就行，不要贪多
```

#### ③ snapshot 加 search 过滤，不要返回整棵树

```javascript
// ❌ 返回完整 snapshot，文本量巨大
await snapshot({ page: state.myPage })

// ✅ 用 search 只返回关键部分
await snapshot({ page: state.myPage, search: /关键词1|关键词2/ })
// 或直接用截图代替，图片比文本更紧凑
await screenshotWithAccessibilityLabels({ page: state.myPage })
```

#### ④ 分批执行测试用例（最有效）

Claude Code 的上下文一旦满了无法清空，**最根本的办法是分批执行**：

```
第一次对话：执行 TCXXX - TCxxx
第二次对话：执行 TCxxx - TCxxx  ← 新对话，上下文干净
第三次对话：执行 TCxxx - TCxxx  ← 新对话，上下文干净
```

每次新对话前，告诉 Claude 当前页面 URL 和需要测试的 TC 范围即可。

### 8. 找不到元素时的排查步骤

当 evaluate 返回 `not found` 时，按以下顺序排查：

```javascript
// Step 1: 截图看当前页面状态
await screenshotWithAccessibilityLabels({ page: state.myPage })

// Step 2: 打印目标区域的 HTML 结构
const html = await state.myPage.evaluate(() => document.body.innerHTML.slice(0, 3000))
console.log(html)

// Step 3: 检查元素是否存在但选择器写错
const found = await state.myPage.evaluate((keyword) => {
  const all = document.querySelectorAll('*')
  const matches = []
  for (const el of all) {
    if (el.textContent.trim() === keyword) {
      matches.push({ tag: el.tagName, class: el.className, children: el.children.length })
    }
  }
  return matches
}, '目标文字')
console.log('匹配到的元素:', found)
```


## 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `claude mcp list` 看不到 playwriter | 配置未生效 | 确认 `.mcp.json` 在当前目录，或重新执行 `claude mcp add` |
| 图标无法变绿 | 扩展未启用或页面限制 | 刷新页面后重新点击图标 |
| 页面 URL 都是 `about:blank` | Chrome 缓存 bug | 完全重启 Chrome 浏览器 |
| 连接后页面变为浅色模式 | Playwright CDP 自动发送媒体模拟命令 | 已知问题，见 [playwright#37627](https://github.com/microsoft/playwright/issues/37627) |
| WSL 中无法连接 | Native Messaging 不支持 WSL | 按远程配置步骤，用 WebSocket :19988 连接 |
| 自动化被网站检测到 | CDP 标志暴露 | 临时断开扩展变灰，通过检测后重连变绿 |

---