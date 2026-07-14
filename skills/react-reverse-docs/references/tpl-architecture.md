# 架构文档模板（tpl-architecture）

## 输出格式

```markdown
# [项目名] 系统架构文档

> 生成时间：2026-03-05 09:16:18 | 来源：AI 逆向分析

## 1. 技术栈

| 层次 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | React | 18.x | |
| 状态管理 | Redux Toolkit | x.x | |
| 路由 | React Router | v6 | |
| UI 组件库 | Ant Design | 5.x | |
| HTTP | Axios | x.x | 封装在 src/utils/request.ts |
| 构建 | Vite | 4.x | |

## 2. 目录结构职责

\`\`\`
src/
├── api/          # HTTP 请求封装，按业务模块分文件
├── assets/       # 静态资源（图片、字体）
├── components/   # 公共组件（跨页面复用）
├── hooks/        # 自定义 Hook
├── pages/        # 页面组件（与路由一一对应）
├── router/       # 路由配置
├── store/        # 状态管理
├── utils/        # 工具函数
└── App.jsx       # 根组件
\`\`\`

## 3. 系统分层架构

\`\`\`mermaid
graph TB
  subgraph 展示层
    P[页面 Pages]
    C[公共组件 Components]
  end
  subgraph 业务层
    H[自定义 Hooks]
    S[状态管理 Store]
  end
  subgraph 数据层
    A[API 请求层]
    R[请求拦截器/响应拦截器]
  end
  subgraph 工具层
    U[Utils 工具函数]
  end
  P --> C
  P --> H
  H --> S
  H --> A
  A --> R
  R --> U
\`\`\`

## 4. 路由结构

| 路由路径 | 页面组件 | 需要登录 | 说明 |
|---------|---------|---------|------|
| /login | LoginPage | 否 | 登录页 |
| /dashboard | DashboardPage | 是 | 首页看板 |

## 5. 数据流向

\`\`\`mermaid
sequenceDiagram
  participant U as 用户操作
  participant C as 组件
  participant S as Store(Redux)
  participant A as API层
  participant B as 后端

  U->>C: 触发事件
  C->>S: dispatch action/thunk
  S->>A: 调用请求函数
  A->>B: HTTP 请求
  B-->>A: 响应数据
  A-->>S: 更新 state
  S-->>C: selector 触发重渲染
  C-->>U: 展示最新数据
\`\`\`

## 6. 关键设计决策

列出项目中重要的架构决策，例如：
- 为什么选择 Redux 而非 Zustand
- 是否有微前端拆分
- 是否有代码分割（lazy loading）
- 权限控制方案

## 7. 外部依赖

| 依赖 | 用途 | 文档链接 |
|------|------|---------|
| xxx | xxx | |
```