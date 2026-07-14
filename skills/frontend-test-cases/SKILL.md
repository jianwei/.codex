---
name: frontend-test-cases
description: 自动分析 Vue 或 React 前端项目，为每个页面生成完整的测试用例文档。当用户想要为前端项目生成测试用例、测试文档、QA文档时，必须使用此 Skill。触发关键词：生成测试用例、写测试用例、测试文档、QA文档、分析页面测试、前端测试、为项目写测试。即使用户说"帮我分析一下项目然后写测试"也要触发此 Skill。支持 Vue (Vue 2/3, Nuxt) 和 React (CRA, Next.js, Vite) 项目。
---

# Frontend Test Cases Generator

自动扫描 Vue 或 React 前端项目，深度分析每个页面的功能、交互逻辑和数据流，按照标准测试用例模板输出每个页面的完整测试文档。

---

## 执行流程

### Step 1: 项目探测

首先识别项目类型与结构：

```bash
# 检测框架类型
cat package.json | grep -E '"vue"|"react"|"nuxt"|"next"'

# Vue 项目：扫描页面目录
find . -path ./node_modules -prune -o -name "*.vue" -print | grep -E "(pages|views)/" | head -50

# React 项目：扫描页面目录
find . -path ./node_modules -prune -o -name "*.tsx" -o -name "*.jsx" -print | grep -E "(pages|views|app)/" | head -50

# 查看路由配置
find . -path ./node_modules -prune -o -name "router*" -o -name "routes*" -print | head -10
cat src/router/index.ts 2>/dev/null || cat src/router/index.js 2>/dev/null || cat src/routes.ts 2>/dev/null
```

**识别项目信息**：
- 框架：Vue 2 / Vue 3 / Nuxt 2 / Nuxt 3 / React / Next.js
- 状态管理：Vuex / Pinia / Redux / Zustand / Context
- UI 库：Element UI / Ant Design / Vant / MUI 等
- 认证方式：Token / Session / OAuth

---

### Step 2: 页面清单梳理

构建完整的页面清单表：

| 页面名称 | 文件路径 | URL路径 | 是否需要认证 | 功能概述 |
|---------|---------|---------|------------|---------|

**优先级排序原则**（先处理高优先级页面）：
1. 核心业务页面（首页、详情页、结果页）
2. 用户流程页面（登录、注册、个人中心）
3. 表单页面（创建、编辑、提交）
4. 列表/数据展示页面
5. 配置/设置页面

---

### Step 3: 深度分析每个页面

对每个页面文件执行以下分析：

#### 3.1 读取页面源码
```bash
cat [page_file_path]
```

#### 3.2 提取关键信息

**Vue 页面分析要点**：
- `<template>` 中的表单元素、按钮、列表、弹窗、Tab 组件
- `<script>` 中的 data/ref 数据字段、computed 计算属性
- methods/setup 中的事件处理函数
- API 调用（axios/fetch 请求）
- router-link 跳转和 `$router.push` 导航
- props 接收的参数
- watch 监听的数据变化

**React 页面分析要点**：
- JSX 中的表单元素、按钮、列表、Modal、Tabs 组件
- useState/useReducer 管理的状态
- useEffect 中的副作用和数据获取
- 事件处理函数（handleXxx、onXxx）
- API 调用（fetch/axios/SWR/React Query）
- Link 组件和 navigate/router.push 导航
- Props 接收的参数

#### 3.3 分析维度

```
功能维度:
- 页面主要展示什么数据？
- 用户可以执行哪些操作？
- 有哪些表单需要填写？
- 有哪些查询/筛选条件？
- 有哪些弹窗/抽屉/对话框？
- 页面间的跳转关系？

数据维度:
- 初始化时加载哪些接口？
- 提交/保存调用哪些接口？
- 有哪些必填字段？
- 有哪些字段验证规则？

权限维度:
- 是否需要登录？
- 是否有角色/权限控制？
- 不同角色看到的内容是否不同？
```

---

### Step 4: 生成测试用例文档

为每个页面生成独立的测试用例 Markdown 文件。

**严格遵循模板格式**（见 `assets/TEMPLATE_test.md`），填充规则：

#### 页面信息填充
```markdown
- **文件路径**: 实际文件路径，如 `src/views/user/Login.vue`
- **URLPATH**: 路由路径，如 `/user/login`
- **是否需要认证**: 根据路由守卫分析填写
```

#### 功能概述
1-2 句精准描述页面的核心用途。

#### 测试用例编写规范

**P0 核心测试（必须包含）**：
- 页面初始加载（接口调用、数据渲染）
- 主要业务流程（正常路径）
- 关键提交操作

**P1 主要功能测试**：
- 每个主要用户交互
- 表单验证（必填、格式、长度限制）
- 数据查询/筛选
- 弹窗/对话框操作

**P2 次要功能测试**：
- 分页/加载更多
- 排序/筛选组合
- 样式响应式

**边界测试**：
- 空数据状态（列表为空）
- 超长文本输入
- 特殊字符输入
- 网络异常/接口失败

**性能测试**：
- 大数据量渲染
- 频繁操作防抖

**安全测试**（如页面涉及）：
- 未授权访问跳转
- XSS 输入过滤
- 越权操作拦截

---

### Step 5: 输出文件

#### 文件命名规范
```
test_[页面名称].md

示例：
test_login.md
test_user_profile.md
test_order_list.md
test_product_detail.md
```

#### 输出目录结构
```
test-cases/
├── README.md          # 测试用例索引总览
├── test_login.md
├── test_register.md
├── test_home.md
└── ...
```

#### README.md 索引格式
```markdown
# 项目测试用例索引

## 项目信息
- 框架: Vue 3 / React
- 总页面数: X
- 生成时间: YYYY-MM-DD

## 页面清单

| 页面 | 文件 | P0用例数 | P1用例数 | 优先级 |
|-----|-----|---------|---------|-------|
| 登录页 | test_login.md | 3 | 5 | 高 |
...
```

---

## 输出质量标准

每个测试用例必须满足：

✅ **步骤可操作**：测试步骤具体到"点击哪个按钮"、"输入什么内容"，不使用模糊表述  
✅ **预期结果可验证**：预期结果有明确的通过/失败判断标准  
✅ **覆盖异常路径**：每个功能至少有一个异常/错误场景  
✅ **数据真实**：使用符合业务场景的真实测试数据示例  
✅ **前置条件完整**：明确说明测试前需要满足的条件  

---

## 特殊场景处理

### 大型项目（页面 > 20 个）
先输出索引 README，询问用户优先生成哪些页面，或按模块批量生成。

### 组件复用
若多个页面共用表单组件，在各自的测试用例中分别描述，不做抽象合并。

### 微前端/多应用
分应用扫描，每个子应用独立生成测试用例集。

---

## 模板文件

完整的测试用例模板位于：`assets/TEMPLATE_test.md`

在生成每个页面的测试文档时，必须以此模板为基础进行填充，不得随意改变结构。