# Playwriter 工具函数 & 操作示例

## 完整工具 & 函数列表

Playwriter MCP **只暴露 1 个 MCP 工具**，其余均为 `execute` 沙盒内的内置辅助函数。

### MCP 工具（仅 1 个）

| 工具名 | 说明 |
|--------|------|
| `execute` | 执行任意 Playwright JS 代码片段，是唯一的 MCP 工具入口 |

### execute 沙盒内置变量

| 变量名 | 类型 | 说明 |
|--------|------|------|
| `page` | `Page` | 当前活跃的 Playwright Page 对象 |
| `context` | `BrowserContext` | 当前浏览器 Context |
| `browser` | `Browser` | 浏览器实例（通过 CDP 连接） |
| `cdp` | `CDPSession \| null` | CDP 会话（需先调用 `getCDPSession` 获取） |
| `state` | `object` | 跨多次 execute 调用持久化的状态对象（如 `state.results = []`，下次调用仍可访问）|

### execute 沙盒内置函数

#### 截图 & 页面感知

| 函数 | 说明 |
|------|------|
| `screenshotWithAccessibilityLabels({ page })` | 截图并叠加 Vimium 风格交互元素标签，同时返回无障碍快照（推荐用于元素定位） |
| `snapshot({ page })` | 获取页面无障碍快照（纯文本，不含截图） |

#### CDP & 调试器

| 函数 | 说明 |
|------|------|
| `getCDPSession({ page })` | 获取当前页面的 CDP 会话 |
| `createDebugger({ cdp })` | 创建 JS 调试器实例，支持断点和变量检查 |
| `dbg.setBreakpoint({ file, line })` | 在指定文件行设置断点 |
| `dbg.inspectLocalVariables()` | 断点暂停时检查当前作用域局部变量 |

#### 代码编辑器

| 函数 | 说明 |
|------|------|
| `createEditor({ cdp })` | 创建实时脚本编辑器实例 |
| `editor.enable()` | 启用编辑器 |
| `editor.edit({ url, oldString, newString })` | 实时替换页面脚本内容（无需刷新） |

#### 样式 & React

| 函数 | 说明 |
|------|------|
| `getStylesForLocator({ locator, cdp })` | 获取元素的完整 CSS 样式（类似 DevTools Styles 面板） |
| `getReactSource({ locator })` | 定位 React 组件对应源文件和行号，返回 `{ fileName, lineNumber }` |

#### 日志

| 函数 | 说明 |
|------|------|
| `getLatestLogs({ count?, search? })` | 获取控制台日志，支持按数量或正则过滤 |
| `clearAllLogs()` | 清除所有已存储的控制台日志 |

### aria-ref 选择器

`screenshotWithAccessibilityLabels` 返回的截图中，每个可交互元素都有标签编号（如 `e5`）。
**用途：通过截图识别元素的文字内容，然后用 `evaluate` 点击，不要用 `locator('aria-ref=...').click()`。**

---

---


## 常用操作示例

### 基础操作

```javascript
// 导航（替代打开新标签页）
await page.goto('https://example.com')

// 截图保存（确保 tmp 目录存在）
require('fs').mkdirSync('./tmp', { recursive: true })
await page.screenshot({ path: './tmp/screenshot.png' })

// ✅ 点击：一律用 evaluate
await page.evaluate((text) => {
  const all = document.querySelectorAll('div, a, button, span, li')
  for (const el of all) {
    if (el.textContent.trim() === text && el.children.length === 0) {
      el.click(); return 'clicked'
    }
  }
  return 'not found'
}, '提交')

// ✅ 输入：用 evaluate 触发框架的响应式更新
await page.evaluate((value) => {
  const input = document.querySelector('input[name="email"]')
  if (input) {
    input.focus()
    input.value = value
    input.dispatchEvent(new Event('input', { bubbles: true }))
    input.dispatchEvent(new Event('change', { bubbles: true }))
  }
}, 'user@example.com')

// 等待元素出现（waitForSelector 可以继续使用）
await page.waitForSelector('.result-list')

// 获取文本
const text = await page.evaluate(() => document.querySelector('h1')?.textContent)
```

### 可视化元素定位

```javascript
// 先截图，查看页面元素和标签编号，了解元素的文字/选择器
await screenshotWithAccessibilityLabels({ page })

// 根据截图中看到的文字，用 evaluate 点击
await page.evaluate((text) => {
  const all = document.querySelectorAll('div, a, button, span, li')
  for (const el of all) {
    if (el.textContent.trim() === text && el.children.length === 0) {
      el.click(); return 'clicked'
    }
  }
  return 'not found'
}, '目标文字')

// 截图确认结果
await screenshotWithAccessibilityLabels({ page })
```

**标签颜色含义：**

| 颜色 | 元素类型 |
|------|---------|
| 黄色 | 链接 |
| 橙色 | 按钮 |
| 珊瑚色 | 文本输入框 |
| 粉色 | 复选框、单选框、开关 |
| 桃色 | 滑块 |
| 三文鱼色 | 菜单项 |
| 琥珀色 | 标签页、选项 |

### 高级 DevTools 功能

```javascript
// 获取 CDP 会话（使用高级功能前必须先执行）
const cdpSession = await getCDPSession({ page })

// 调试器断点
const dbg = createDebugger({ cdp: cdpSession })
await dbg.setBreakpoint({ file: 'app.js', line: 42 })
await dbg.inspectLocalVariables()

// 实时编辑脚本
const editor = createEditor({ cdp: cdpSession })
await editor.enable()
await editor.edit({ url: 'app.js', oldString: 'DEBUG=false', newString: 'DEBUG=true' })

// 检查 CSS 样式
const styles = await getStylesForLocator({ locator: page.locator('.btn'), cdp: cdpSession })

// 定位 React 组件源码
const source = await getReactSource({ locator: page.locator('aria-ref=e5') })
// => { fileName: 'Button.tsx', lineNumber: 42 }
```

---

---