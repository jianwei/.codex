# Playwriter 性能优化规则

## ⚡ 性能优化规则（避免超时）

> 根据实际执行经验，以下规则可大幅减少超时和等待时间。

### 🔑 核心规则：所有点击操作必须用 evaluate，禁止用 locator().click()

**不管什么情况，点击元素一律使用 `page.evaluate()` 调用原生 DOM click。**
`locator().click()` 会因 Playwright 内部的可交互性检查而超时，永远不要使用。

#### 按文字内容点击（最常用）

```javascript
// 精确匹配文字（叶子节点）
await page.evaluate((text) => {
  const all = document.querySelectorAll('div, a, button, span, li')
  for (const el of all) {
    if (el.textContent.trim() === text && el.children.length === 0) {
      el.click()
      return 'clicked'
    }
  }
  return 'not found'
}, '目标元素')
```

#### 按 CSS 选择器点击

```javascript
await page.evaluate((selector) => {
  const el = document.querySelector(selector)
  if (el) { el.click(); return 'clicked' }
  return 'not found'
}, 'img[alt="location"]')
```

#### 点击父元素

```javascript
await page.evaluate((selector) => {
  const el = document.querySelector(selector)
  if (el) { el.parentElement.click(); return 'clicked' }
  return 'not found'
}, 'img[alt="location"]')
```

#### 按链接文字点击

```javascript
await page.evaluate((text) => {
  const links = document.querySelectorAll('a')
  for (const link of links) {
    if (link.textContent.trim() === text) {
      link.click()
      return 'clicked'
    }
  }
  return 'not found'
}, '目标文字')
```

#### 输入文字（fill 同样可能超时，用 evaluate 代替）

```javascript
await page.evaluate((value) => {
  const input = document.querySelector('input[type="text"], input[type="search"]')
  if (input) {
    input.focus()
    input.value = value
    input.dispatchEvent(new Event('input', { bubbles: true }))
    input.dispatchEvent(new Event('change', { bubbles: true }))
  }
}, '目标文字')
```

---

### ❌ 常见慢操作 vs ✅ 正确做法

#### 1. 函数名必须用正确的

```javascript
// ❌ 错误：accessibilitySnapshot 不存在，会一直挂起直到超时
await accessibilitySnapshot({ page })

// ✅ 正确：使用以下两个之一
await screenshotWithAccessibilityLabels({ page })  // 截图 + 标签（视觉定位）
await snapshot({ page })                            // 纯文本无障碍快照（文字提取）
```

#### 2. 禁止用 waitForTimeout 硬等待

```javascript
// ❌ 慢：无论页面是否就绪都傻等
await page.waitForTimeout(1500)

// ✅ 快：等具体条件满足再继续
await page.waitForSelector('.result-list')                   // 等元素出现
await page.waitForSelector('.loading', { state: 'hidden' })  // 等 loading 消失
await page.waitForURL('**/your-page**')                           // 等 URL 变化
await page.waitForLoadState('networkidle')                   // 等网络空闲
// 注意：waitForSelector 仅用于等待，点击仍然用 evaluate
```

#### 3. 不要在同一个 execute 里堆太多操作

```javascript
// ❌ 慢：一次 execute 做太多事，任何一步慢都会整体超时
await page.click('text=目标城市')
await page.waitForTimeout(1500)
await accessibilitySnapshot({ page, search: /目标城市/ })

// ✅ 快：拆分成多次 execute，每次只做一件事
// 第一次：截图确认页面状态和元素文字
await screenshotWithAccessibilityLabels({ page })

// 第二次：用 evaluate 点击
await page.evaluate((text) => {
  const all = document.querySelectorAll('div, a, button, span, li')
  for (const el of all) {
    if (el.textContent.trim() === text && el.children.length === 0) {
      el.click(); return 'clicked'
    }
  }
}, '目标城市')

// 第三次：截图确认结果
await screenshotWithAccessibilityLabels({ page })
```

#### 4. 所有点击必须用 evaluate，不用任何 locator

```javascript
// ❌ 禁止：任何形式的 locator().click()
await page.locator('text=目标城市').first().click()
await page.locator('aria-ref=e12').click()

// ✅ 唯一正确方式：evaluate + 原生 DOM click
await page.evaluate((text) => {
  const all = document.querySelectorAll('div, a, button, span, li')
  for (const el of all) {
    if (el.textContent.trim() === text && el.children.length === 0) {
      el.click(); return 'clicked'
    }
  }
  return 'not found'
}, '目标城市')
```

#### 5. 等待用 waitForSelector，不用 waitForTimeout

```javascript
// 页面跳转/加载
await page.waitForLoadState('domcontentloaded')

// 等弹窗出现
await page.waitForSelector('.modal', { state: 'visible' })

// 等 loading 消失
await page.waitForSelector('.loading', { state: 'hidden' })
```

### 标准操作流程模板（推荐）

每次交互都遵循：**截图看状态 → evaluate 点击 → 等条件满足 → 截图确认结果 → 检查控制台**

```javascript
// Step 1: 截图，了解当前页面元素的文字内容
await screenshotWithAccessibilityLabels({ page })

// Step 2: 用 evaluate 点击目标元素
await page.evaluate((text) => {
  const all = document.querySelectorAll('div, a, button, span, li')
  for (const el of all) {
    if (el.textContent.trim() === text && el.children.length === 0) {
      el.click(); return 'clicked'
    }
  }
  return 'not found'
}, '目标文字')

// Step 3: 等待具体条件，而不是 waitForTimeout
await page.waitForSelector('.city-picker', { state: 'visible' })

// Step 4: 截图确认结果
await screenshotWithAccessibilityLabels({ page })

// Step 5: 检查控制台错误（每步操作后必须执行，不可跳过）
await getLatestLogs({ count: 20 })
```

---

### 🔴 每步操作后必须检查控制台错误

**每完成一个操作步骤，必须立即调用 `getLatestLogs` 检查控制台，不能跳过，不能攒到最后一起查。**

> 发现 `[error]` 时：记录错误内容和操作步骤，然后**继续测试后续用例，不要停止**。`[warn]` 忽略不记录。

#### 发现错误时的输出格式

发现 `[error]` 时，用以下格式在终端**醒目输出**，然后继续测试，**不停止**：

```javascript
const logs = await getLatestLogs({ count: 20 })
const errors = logs.filter(l => l.includes('[error]'))
if (errors.length > 0) {
  console.log('╔══════════════════════════════════════════════╗')
  console.log('║               ❌ 控制台错误                  ║')
  console.log('╠══════════════════════════════════════════════╣')
  console.log('║ 操作步骤：TCXXX - 点击「目标元素」Tab     ║')
  errors.forEach(e => console.log('║ ' + e))
  console.log('╚══════════════════════════════════════════════╝')
}
// 继续下一步，不停止
```

终端实际输出效果：
```
╔══════════════════════════════════════════════╗
║               ❌ 控制台错误                  ║
╠══════════════════════════════════════════════╣
║ 操作步骤：TCXXX - 点击「目标元素」Tab     ║
║ [error] TypeError: Cannot read properties of null
╚══════════════════════════════════════════════╝
```

#### 完整操作模板（含控制台检查）

```javascript
// 1. 执行操作
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

// 2. 截图确认页面变化
await screenshotWithAccessibilityLabels({ page: state.myPage })

// 3. 立即检查控制台 error（[warn] 忽略）
const logs = await getLatestLogs({ count: 20 })
const errors = logs.filter(l => l.includes('[error]'))
if (errors.length > 0) {
  console.log('╔══════════════════════════════════════════════╗')
  console.log('║               ❌ 控制台错误                  ║')
  console.log('╠══════════════════════════════════════════════╣')
  console.log('║ 操作步骤：当前 TC 编号和操作描述             ║')
  errors.forEach(e => console.log('║ ' + e))
  console.log('╚══════════════════════════════════════════════╝')
}
// 继续下一步，不停止
```

### ⛔ 幻觉函数黑名单（这些函数不存在，调用必超时）

> ⚠️ 特别警告：`accessibilitySnapshot` 是出现频率最高的幻觉函数，**每次调用都会导致 20s 超时**，严禁使用。

以下函数是 Claude **凭空捏造**的，在 Playwriter 沙盒中**不存在**，调用后会一直挂起直到超时：

| 幻觉函数（禁止使用）| 正确替代方案 |
|-------------------|------------|
| `accessibilitySnapshot({ page })` | `snapshot({ page })` 或 `screenshotWithAccessibilityLabels({ page })` |
| `getCleanHTML({ locator, search })` | `await locator.innerHTML()` 或 `await page.content()` |
| `getPageSnapshot()` | `snapshot({ page })` |
| `getAccessibilityTree()` | `snapshot({ page })` |

### ⛔ 错误的 Playwright 定位语法

```javascript
// ❌ 错误：Playwright 不支持这种 role 属性选择器语法，会一直等待超时
page.locator('role=button[name="目标元素"]')

// ✅ 唯一正确方式：用 evaluate 直接调用原生 click
await page.evaluate((text) => {
  const all = document.querySelectorAll('div, a, button, span, li')
  for (const el of all) {
    if (el.textContent.trim() === text && el.children.length === 0) {
      el.click(); return 'clicked'
    }
  }
  return 'not found'
}, '目标元素')
```

### ⛔ getLatestLogs 参数错误

```javascript
// ❌ 错误：getLatestLogs 不接受 page 参数
await getLatestLogs({ page: state.myPage, count: 30 })

// ✅ 正确：只接受 count 和 search
await getLatestLogs({ count: 30 })
await getLatestLogs({ search: /error/i })
```

### ⛔ 获取已有页面的正确方式

> 注意：执行 `playwriter - reset` 后，`state` 会被清空，`state.myPage` 会变成 `undefined`，
> 下一次 execute 必须先重新赋值，否则会报 `Cannot read properties of undefined (reading 'locator')`。

```javascript
// ❌ 错误：find + newPage 会在找不到时创建新 Tab（违反禁止规则）
state.myPage = context.pages().find(p => p.url() === 'about:blank') ?? await context.newPage()

// ✅ 正确：直接取已有页面，绝不创建新页面
state.myPage = context.pages()[0]

// ✅ 取指定 URL 的页面（找不到时回退到当前 page，不创建新页面）
state.myPage = context.pages().find(p => p.url().includes('your-app-host')) ?? page
```