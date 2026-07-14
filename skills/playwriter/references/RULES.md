# Playwriter 强制规则

> 所有规则必须严格遵守，违反会导致超时或错误。
> 开始测试前必须重新阅读本文件。

## ⚠️ 行为限制规则（强制执行）

**以下操作被严格禁止，在任何情况下都不得执行：**

```
❌ 禁止打开新的浏览器窗口
   → 禁止使用：browser.newContext() / chromium.launch() 等

❌ 禁止打开新的标签页（Tab）
   → 禁止使用：context.newPage() / window.open() / page.waitForEvent('popup') 等
   → 注意：page.waitForEvent('download') 用于等待文件下载，不涉及新标签页，允许使用
   → 禁止点击 target="_blank" 的链接
   → 禁止使用 Ctrl+T / Cmd+T 快捷键

✅ 正确做法：所有操作只在当前已连接的标签页（绿色图标）内进行
✅ 需要访问新 URL 时，使用 page.goto('url') 在当前页面内导航
```

---

## 🚨 反复违反的规则（必须牢记，零容忍）

以下规则在实际执行中被反复违反，**每次开始测试前必须重新确认**：

### 违规 1：使用 `context.newPage()` 创建新标签页

```javascript
// ❌ 绝对禁止，无论任何写法
state.myPage = context.pages().find(...) ?? await context.newPage()

// ✅ 唯一正确写法
state.myPage = context.pages().find(p => p.url().includes('localhost')) ?? page
```

### 违规 2：调用 `accessibilitySnapshot`（不存在的幻觉函数）

```javascript
// ❌ 绝对禁止，每次调用必超时 20s
await accessibilitySnapshot({ page })
await accessibilitySnapshot({ page, showDiffSinceLastCall: false })

// ✅ 唯一正确写法
await screenshotWithAccessibilityLabels({ page: state.myPage })  // 截图
await snapshot({ page: state.myPage })                           // 纯文本快照
```

### 违规 3：使用 `locator().click()` 任何形式

```javascript
// ❌ 绝对禁止，所有 locator click 都会超时
await page.locator('text=目标元素').click()
await page.locator('text=目标元素').first().click()
await page.locator('role=button[name="xxx"]').click()

// ✅ 唯一正确写法
await state.myPage.evaluate((text) => {
  const all = document.querySelectorAll('div, a, button, span, li')
  for (const el of all) {
    if (el.textContent.trim() === text && el.children.length === 0) {
      el.click(); return 'clicked'
    }
  }
  return 'not found'
}, '目标元素')
```

### 违规 4：`page` 和 `state.myPage` 混用

```javascript
// ❌ 禁止混用，容易造成操作对象不一致
await page.locator(...)           // 用的是默认 page
await state.myPage.evaluate(...)  // 用的是 state.myPage

// ✅ 统一只用 state.myPage，初始化后始终如一
state.myPage = context.pages().find(p => p.url().includes('localhost')) ?? page
// 之后所有操作全部用 state.myPage，永远不直接用 page
await state.myPage.evaluate(...)
await screenshotWithAccessibilityLabels({ page: state.myPage })
await snapshot({ page: state.myPage })
```

### 违规 5：evaluate 没有 return 值

```javascript
// ❌ 无法判断操作是否成功
await state.myPage.evaluate(() => {
  document.querySelectorAll('*').forEach(el => {
    if (el.textContent === '目标元素') el.click()
  })
})
// 输出：Code executed successfully (no output) ← 不知道有没有点到

// ✅ 必须有明确的 return
const result = await state.myPage.evaluate((text) => {
  const all = document.querySelectorAll('div, a, button, span, li')
  for (const el of all) {
    if (el.textContent.trim() === text && el.children.length === 0) {
      el.click(); return 'clicked: ' + text
    }
  }
  return 'not found: ' + text
}, '目标元素')
console.log(result)
```

---