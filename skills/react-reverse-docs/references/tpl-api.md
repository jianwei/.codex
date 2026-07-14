# API 接口文档模板（tpl-api）

> ⚠️ 生成原则：
> 1. 从前端调用代码**反向推理**接口的完整数据结构——不只是"有这个字段"，而是每个字段的类型、含义、枚举值、是否可为空都要写清楚
> 2. 每个接口必须提供可直接运行的 **Mock 数据**，格式为标准 JSON，可直接用于 MSW / json-server / apifox
> 3. 分析代码时重点关注：解构赋值（能看出用了哪些字段）、条件渲染（能看出枚举值含义）、列表渲染（能看出数组结构）

```markdown
# [模块名称] 接口文档

> 源文件：`src/api/xxx.js`
> 生成时间：2026-03-05 09:16:18

---

## 模块概述

说明本模块负责哪块业务，包含几个接口，被哪些页面使用。

| 接口 | 方法 | 路径 | 用途 |
|------|------|------|------|
| getXxxList | GET | `/api/xxx/list` | 分页查询列表 |
| getXxxById | GET | `/api/xxx/:id` | 查询单条详情 |
| createXxx | POST | `/api/xxx` | 新增记录 |
| updateXxx | PUT | `/api/xxx/:id` | 修改记录 |
| deleteXxx | DELETE | `/api/xxx/:id` | 删除单条 |
| batchDeleteXxx | DELETE | `/api/xxx/batch` | 批量删除 |
| exportXxx | GET | `/api/xxx/export` | 导出 Excel |

---

## 接口详情

---

### getXxxList · 分页查询列表

**基本信息**

| 项目 | 内容 |
|------|------|
| 函数名 | `getXxxList` |
| 请求方式 | GET |
| 接口路径 | `/api/xxx/list` |
| 被调用位置 | `src/pages/XxxListPage.jsx` → `useEffect([], fetchList)` |

**请求参数**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|-------|------|
| page | number | ✅ | 1 | 页码，从 1 开始 |
| pageSize | number | ✅ | 20 | 每页条数，可选值：10 / 20 / 50 / 100 |
| keyword | string | ❌ | — | 名称模糊搜索，为空时不过滤 |
| status | number | ❌ | — | 状态筛选：1=正常 2=禁用，不传则查全部 |
| startTime | string | ❌ | — | 创建时间起始，格式：2026-03-05 09:16:18 |
| endTime | string | ❌ | — | 创建时间截止，格式：2026-03-05 09:16:18 |

**请求示例**
```
GET /api/xxx/list?page=1&pageSize=20&keyword=张三&status=1
```

**响应字段说明**

| 字段路径 | 类型 | 可为空 | 说明 |
|---------|------|-------|------|
| code | number | ❌ | 业务状态码：200=成功，其他见错误码表 |
| message | string | ❌ | 提示信息 |
| data.list | array | ❌ | 当前页数据，无数据时为 `[]` |
| data.list[].id | string | ❌ | 记录唯一ID，UUID格式 |
| data.list[].name | string | ❌ | 名称，1-50字 |
| data.list[].status | number | ❌ | 状态：1=正常 2=禁用 |
| data.list[].remark | string | ✅ | 备注，无备注时为空字符串或null |
| data.list[].createdBy | string | ❌ | 创建人姓名 |
| data.list[].createdAt | string | ❌ | 创建时间，格式：2026-03-05 09:16:18 |
| data.list[].updatedAt | string | ❌ | 最后修改时间，格式：2026-03-05 09:16:18 |
| data.total | number | ❌ | 符合条件的总条数（用于分页组件） |
| data.page | number | ❌ | 当前页码（原样返回） |
| data.pageSize | number | ❌ | 当前每页条数（原样返回） |

**数据来源推理**（从前端代码反向分析）

```js
// 前端代码中发现的字段使用：

// 表格列渲染 → 用到了哪些字段
{ title: '名称', dataIndex: 'name', render: (text, record) => <a onClick={() => navigate(`/detail/${record.id}`)}>{text}</a> }
// → 用到：id（跳转）、name（显示）

{ title: '状态', dataIndex: 'status', render: (val) => <Tag color={val === 1 ? 'green' : 'red'}>{val === 1 ? '正常' : '禁用'}</Tag> }
// → 推理：status 枚举值 1=正常 2=禁用

{ title: '操作', render: (_, record) => <><Button onClick={() => handleEdit(record.id)}>编辑</Button></>  }
// → 编辑只传了 id，说明编辑时会重新请求详情接口

// 分页组件 → 用到了 total
<Pagination total={data.total} current={data.page} pageSize={data.pageSize} />
// → total / page / pageSize 均由接口返回
```

**Mock 数据**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "name": "测试记录一",
        "status": 1,
        "remark": "这是备注内容",
        "createdBy": "张三",
        "createdAt": "2026-03-05 09:16:18",
        "updatedAt": "2026-03-05 10:20:30"
      },
      {
        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "name": "测试记录二",
        "status": 2,
        "remark": "",
        "createdBy": "李四",
        "createdAt": "2026-03-04 14:30:00",
        "updatedAt": "2026-03-04 14:30:00"
      },
      {
        "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
        "name": "测试记录三",
        "status": 1,
        "remark": null,
        "createdBy": "王五",
        "createdAt": "2026-03-03 08:00:00",
        "updatedAt": "2026-03-05 09:00:00"
      }
    ],
    "total": 58,
    "page": 1,
    "pageSize": 20
  }
}
```

**Mock 空数据场景**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

**错误响应**
```json
{ "code": 401, "message": "登录已过期，请重新登录", "data": null }
{ "code": 403, "message": "无访问权限", "data": null }
{ "code": 500, "message": "服务器内部错误", "data": null }
```

---

### getXxxById · 查询单条详情

**基本信息**

| 项目 | 内容 |
|------|------|
| 函数名 | `getXxxById` |
| 请求方式 | GET |
| 接口路径 | `/api/xxx/:id` |
| 被调用位置 | `src/pages/XxxListPage.jsx` → `handleEdit(id)` 点击编辑时触发 |

**请求参数**

| 字段 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | Path | string | ✅ | 记录ID，UUID格式 |

**请求示例**
```
GET /api/xxx/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**响应字段说明**

| 字段路径 | 类型 | 可为空 | 说明 |
|---------|------|-------|------|
| code | number | ❌ | 业务状态码 |
| data.id | string | ❌ | 记录ID |
| data.name | string | ❌ | 名称 |
| data.status | number | ❌ | 状态：1=正常 2=禁用 |
| data.remark | string | ✅ | 备注 |
| data.createdBy | string | ❌ | 创建人姓名 |
| data.createdAt | string | ❌ | 创建时间 |
| data.updatedAt | string | ❌ | 最后修改时间 |

**数据来源推理**

```js
// 前端编辑回填代码：
const handleEdit = async (id) => {
  setEditLoading(true)
  const res = await getXxxById(id)
  form.setFieldsValue({
    name: res.data.name,
    status: res.data.status,
    remark: res.data.remark
  })
  setEditLoading(false)
}
// → 推理：编辑表单只用到 name / status / remark 三个字段
// → id / createdBy / createdAt / updatedAt 在编辑弹窗中只展示不编辑
```

**Mock 数据**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "测试记录一",
    "status": 1,
    "remark": "这是备注内容",
    "createdBy": "张三",
    "createdAt": "2026-03-05 09:16:18",
    "updatedAt": "2026-03-05 10:20:30"
  }
}
```

**错误响应**
```json
{ "code": 404, "message": "记录不存在或已被删除", "data": null }
```

---

### createXxx · 新增记录

**基本信息**

| 项目 | 内容 |
|------|------|
| 函数名 | `createXxx` |
| 请求方式 | POST |
| 接口路径 | `/api/xxx` |
| Content-Type | `application/json` |
| 被调用位置 | `src/pages/XxxListPage.jsx` → 新增弹窗"确认"按钮 |

**请求体字段**

| 字段 | 类型 | 必填 | 校验规则 | 说明 |
|------|------|------|---------|------|
| name | string | ✅ | 1-50字，全局唯一 | 名称 |
| status | number | ✅ | 枚举：1 或 2 | 初始状态 |
| remark | string | ❌ | 最多200字 | 备注，不传或传空字符串均可 |

**数据来源推理**

```js
// 前端表单提交代码：
const handleAddSubmit = async () => {
  const values = await addForm.validateFields()
  // values = { name, status, remark }
  await createXxx(values)
  // → 推理：只提交表单的三个字段
  // → createdBy 由后端从 token 中解析当前用户，前端不传
  // → createdAt / updatedAt 由后端自动生成，前端不传
}
```

**请求示例**
```json
{
  "name": "新记录名称",
  "status": 1,
  "remark": "备注信息"
}
```

**响应字段说明**

| 字段路径 | 类型 | 说明 |
|---------|------|------|
| code | number | 200=成功 |
| data.id | string | 新创建记录的ID（用于后续跳转或刷新定位） |
| message | string | "新增成功" |

**Mock 数据**
```json
{
  "code": 200,
  "message": "新增成功",
  "data": {
    "id": "d4e5f6a7-b8c9-0123-defa-234567890123"
  }
}
```

**错误响应**
```json
{ "code": 400, "message": "名称不能为空", "data": null }
{ "code": 400, "message": "名称不能超过50字", "data": null }
{ "code": 409, "message": "名称已存在，请修改后重试", "data": null }
```

---

### updateXxx · 修改记录

**基本信息**

| 项目 | 内容 |
|------|------|
| 函数名 | `updateXxx` |
| 请求方式 | PUT |
| 接口路径 | `/api/xxx/:id` |
| Content-Type | `application/json` |
| 被调用位置 | `src/pages/XxxListPage.jsx` → 编辑弹窗"确认"按钮 |

**请求参数**

| 字段 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | Path | string | ✅ | 被修改记录的ID |
| name | Body | string | ✅ | 名称，1-50字 |
| status | Body | number | ✅ | 状态：1=正常 2=禁用 |
| remark | Body | string | ❌ | 备注，最多200字 |

**数据来源推理**

```js
// 前端编辑提交代码：
const handleEditSubmit = async () => {
  const values = await editForm.validateFields()
  await updateXxx(editingRecord.id, values)
  // → id 来自点击编辑时存入 editingRecord.id
  // → body 同新增，只有 name / status / remark
  // → updatedAt 由后端自动更新，前端不传
}
```

**请求示例**
```
PUT /api/xxx/a1b2c3d4-e5f6-7890-abcd-ef1234567890

{
  "name": "修改后的名称",
  "status": 2,
  "remark": "更新了备注"
}
```

**Mock 数据**
```json
{
  "code": 200,
  "message": "修改成功",
  "data": null
}
```

**错误响应**
```json
{ "code": 404, "message": "记录不存在或已被删除", "data": null }
{ "code": 409, "message": "名称已存在，请修改后重试", "data": null }
```

---

### deleteXxx · 删除单条

**基本信息**

| 项目 | 内容 |
|------|------|
| 函数名 | `deleteXxx` |
| 请求方式 | DELETE |
| 接口路径 | `/api/xxx/:id` |
| 被调用位置 | `src/pages/XxxListPage.jsx` → 列表行"删除"确认后 |

**请求参数**

| 字段 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | Path | string | ✅ | 被删除记录的ID |

**数据来源推理**

```js
// 前端删除代码：
const handleDelete = async (record) => {
  await deleteXxx(record.id)
  // → 只需要 id，其余字段不传
  // → 删除成功后，若当前页只剩1条，则 page - 1 再刷新
  if (listData.length === 1 && page > 1) {
    setPage(page - 1)
  } else {
    fetchList()
  }
}
```

**Mock 数据**
```json
{ "code": 200, "message": "删除成功", "data": null }
```

**错误响应**
```json
{ "code": 404, "message": "记录不存在或已被删除", "data": null }
{ "code": 403, "message": "无删除权限", "data": null }
```

---

### batchDeleteXxx · 批量删除

**基本信息**

| 项目 | 内容 |
|------|------|
| 函数名 | `batchDeleteXxx` |
| 请求方式 | DELETE |
| 接口路径 | `/api/xxx/batch` |
| Content-Type | `application/json` |
| 被调用位置 | `src/pages/XxxListPage.jsx` → 批量删除确认后 |

**请求体字段**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | string[] | ✅ | 要删除的ID数组，至少1个 |

**数据来源推理**

```js
// 前端批量删除代码：
const handleBatchDelete = async () => {
  await batchDeleteXxx({ ids: selectedRowKeys })
  // → selectedRowKeys 是表格 rowSelection 维护的已选行 key 数组
  // → key 对应 record.id
  setSelectedRowKeys([])   // 清空勾选
  fetchList()
}
```

**请求示例**
```json
{
  "ids": [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "b2c3d4e5-f6a7-8901-bcde-f12345678901"
  ]
}
```

**Mock 数据**
```json
{ "code": 200, "message": "已删除 2 条", "data": { "deletedCount": 2 } }
```

**错误响应**
```json
{ "code": 400, "message": "ids 不能为空", "data": null }
{ "code": 403, "message": "无删除权限", "data": null }
```

---

### exportXxx · 导出 Excel

**基本信息**

| 项目 | 内容 |
|------|------|
| 函数名 | `exportXxx` |
| 请求方式 | GET |
| 接口路径 | `/api/xxx/export` |
| 响应类型 | `blob`（文件流，非 JSON） |
| 被调用位置 | `src/pages/XxxListPage.jsx` → 点击"导出"按钮 |

**请求参数**（同搜索条件，无分页）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | ❌ | 名称关键词 |
| status | number | ❌ | 状态筛选 |
| startTime | string | ❌ | 创建时间起始 |
| endTime | string | ❌ | 创建时间截止 |

**数据来源推理**

```js
// 前端导出代码：
const handleExport = async () => {
  setExporting(true)
  const res = await exportXxx({ keyword, status, startTime, endTime })
  // → 导出条件与当前搜索条件完全一致
  // → 不传 page/pageSize，后端导出全量

  // 下载文件：
  const url = window.URL.createObjectURL(new Blob([res]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `xxx数据_${dayjs().format('YYYY-MM-DD HH:mm:ss')}.xlsx`)
  document.body.appendChild(link)
  link.click()
  // → 文件名格式：xxx数据_2026-03-05 09:16:18.xlsx
}
```

**响应说明**

> 本接口返回二进制文件流，响应头如下：
> - `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
> - `Content-Disposition: attachment; filename="xxx.xlsx"`

**导出文件列定义**（从前端列配置反推后端导出列）

| 列名（Excel表头） | 对应字段 | 格式 |
|----------------|---------|------|
| 名称 | name | 字符串 |
| 状态 | status | 文字："正常" / "禁用"（不是数字） |
| 备注 | remark | 字符串，空时显示"—" |
| 创建人 | createdBy | 字符串 |
| 创建时间 | createdAt | 2026-03-05 09:16:18 |

**Mock 说明**

> 导出接口返回 blob，无法用 JSON 表示。Mock 时建议：
> - 使用 MSW：返回 `HttpResponse.arrayBuffer(...)` 或直接返回一个空 xlsx 文件
> - 使用 json-server：配置 custom route 返回静态文件
> - 开发阶段可 mock 为：延迟 1s 后提示"导出成功"，跳过实际下载

---

## 统一响应结构规范

所有接口（除导出外）遵循统一响应格式：

```json
{
  "code": 200,       // number，业务状态码
  "message": "xxx",  // string，提示信息
  "data": {}         // any，业务数据，失败时为 null
}
```

**错误码汇总**

| code | HTTP状态码 | 含义 | 前端处理方式 |
|------|-----------|------|------------|
| 200 | 200 | 成功 | 正常处理 |
| 400 | 400 | 参数校验失败 | toast 显示 message |
| 401 | 401 | 未登录/token过期 | 跳转登录页 |
| 403 | 403 | 无权限 | toast 提示"无操作权限" |
| 404 | 404 | 资源不存在 | toast 提示 message |
| 409 | 409 | 数据冲突（如重名） | toast 显示 message |
| 413 | 413 | 数据量过大 | toast 提示"请缩小筛选范围" |
| 500 | 500 | 服务器错误 | toast 提示"服务器异常，请稍后重试" |

---

## Mock 方案说明

### 方案一：MSW（推荐，开发环境拦截）

```js
// src/mocks/handlers/xxx.js
import { http, HttpResponse } from 'msw'
import { xxxListMock, xxxDetailMock } from './data/xxx'

export const xxxHandlers = [
  http.get('/api/xxx/list', ({ request }) => {
    const url = new URL(request.url)
    const page = Number(url.searchParams.get('page')) || 1
    const pageSize = Number(url.searchParams.get('pageSize')) || 20
    return HttpResponse.json({
      code: 200,
      message: 'success',
      data: {
        list: xxxListMock.slice((page - 1) * pageSize, page * pageSize),
        total: xxxListMock.length,
        page,
        pageSize
      }
    })
  }),

  http.get('/api/xxx/:id', ({ params }) => {
    const item = xxxListMock.find(i => i.id === params.id)
    if (!item) return HttpResponse.json({ code: 404, message: '记录不存在', data: null }, { status: 404 })
    return HttpResponse.json({ code: 200, message: 'success', data: item })
  }),

  http.post('/api/xxx', async ({ request }) => {
    const body = await request.json()
    const newItem = { id: crypto.randomUUID(), ...body, createdBy: '当前用户', createdAt: new Date().toLocaleString(), updatedAt: new Date().toLocaleString() }
    xxxListMock.unshift(newItem)
    return HttpResponse.json({ code: 200, message: '新增成功', data: { id: newItem.id } })
  }),

  http.put('/api/xxx/:id', async ({ params, request }) => {
    const body = await request.json()
    const idx = xxxListMock.findIndex(i => i.id === params.id)
    if (idx === -1) return HttpResponse.json({ code: 404, message: '记录不存在', data: null })
    xxxListMock[idx] = { ...xxxListMock[idx], ...body, updatedAt: new Date().toLocaleString() }
    return HttpResponse.json({ code: 200, message: '修改成功', data: null })
  }),

  http.delete('/api/xxx/:id', ({ params }) => {
    const idx = xxxListMock.findIndex(i => i.id === params.id)
    if (idx === -1) return HttpResponse.json({ code: 404, message: '记录不存在', data: null })
    xxxListMock.splice(idx, 1)
    return HttpResponse.json({ code: 200, message: '删除成功', data: null })
  }),

  http.delete('/api/xxx/batch', async ({ request }) => {
    const { ids } = await request.json()
    ids.forEach(id => {
      const idx = xxxListMock.findIndex(i => i.id === id)
      if (idx !== -1) xxxListMock.splice(idx, 1)
    })
    return HttpResponse.json({ code: 200, message: `已删除 ${ids.length} 条`, data: { deletedCount: ids.length } })
  }),
]
```

### 方案二：Mock 数据文件（静态数据）

```js
// src/mocks/data/xxx.js
export const xxxListMock = [
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "测试记录一",
    "status": 1,
    "remark": "这是备注内容",
    "createdBy": "张三",
    "createdAt": "2026-03-05 09:16:18",
    "updatedAt": "2026-03-05 10:20:30"
  },
  {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "name": "测试记录二",
    "status": 2,
    "remark": "",
    "createdBy": "李四",
    "createdAt": "2026-03-04 14:30:00",
    "updatedAt": "2026-03-04 14:30:00"
  },
  {
    "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "name": "测试记录三",
    "status": 1,
    "remark": null,
    "createdBy": "王五",
    "createdAt": "2026-03-03 08:00:00",
    "updatedAt": "2026-03-05 09:00:00"
  }
  // 可按需扩展更多条数据
]
```

---

## 请求封装说明

> 如该文件使用了 axios 封装层，说明以下内容：

| 项目 | 说明 |
|------|------|
| baseURL | `process.env.REACT_APP_API_URL` 或 `/api` |
| 超时时间 | 10000ms（10秒） |
| 请求拦截 | 自动附加 `Authorization: Bearer <token>`（token 从 localStorage 读取） |
| 响应拦截 | code !== 200 时统一 reject；401 时清除 token 跳登录页 |
| 错误处理 | 网络错误 → toast "网络连接异常"；超时 → toast "请求超时，请重试" |
```