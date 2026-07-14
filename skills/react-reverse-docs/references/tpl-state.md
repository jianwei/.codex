# 状态管理文档模板（tpl-state）

```markdown
# 状态管理文档

> 方案：Redux Toolkit / Zustand / Context | 生成时间：2026-03-05 09:16:18

## Store 结构总览

\`\`\`
store/
├── userSlice    → 用户信息、登录状态
├── orderSlice   → 订单数据
└── uiSlice      → 全局 UI 状态
\`\`\`

## [sliceName] 详细说明

### State 字段

| 字段 | 类型 | 初始值 | 说明 |
|------|------|--------|------|

### Actions

| Action | 参数 | 功能 |
|--------|------|------|

### Async Thunks

| Thunk | 接口 | 成功行为 | 失败行为 |
|-------|------|---------|---------|

### Selectors

| Selector | 返回值 | 使用场景 |
|----------|--------|---------|

## 数据流图

\`\`\`mermaid
flowchart LR
    Component -->|dispatch| Store
    Store -->|selector| Component
    Store -->|thunk| API
    API -->|response| Store
\`\`\`

## 组件-状态依赖关系

| 组件 | 读取 State | 触发 Action |
|------|-----------|------------|
```

---