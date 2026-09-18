# 函数注释规范

**所有模式下生效。**

- **新建函数**：在函数定义正上方添加 JSDoc 注释，包含功能简述（第一行）、`@param`、`@returns`，并按需补充 `@throws`。无参数函数省略 `@param`。

## 推荐格式示例（TypeScript）

```typescript
/**
 * 根据用户ID获取用户名称
 *
 * @param userId - 用户的唯一标识符
 * @param options - 请求配置项
 * @param options.timeout - 超时时间（毫秒）
 * @param options.retry - 是否重试
 * @returns 返回用户姓名的 Promise
 */
async function getUserName(
    userId: string,
    options: { timeout: number; retry?: boolean }
): Promise<string> {
    // ...
}
```

对象形式的参数使用 `@param` 展开描述内部属性，如上例所示。

## 常用 JSDoc 标签速查

| 标签 | 含义 | 示例 |
| --- | --- | --- |
| `@param` | 描述参数 | `@param name - 用户名` |
| `@returns` | 描述返回值 | `@returns 返回处理后的数据` |
| `@throws` | 描述可能抛出的异常 | `@throws {Error} 当ID无效时抛出` |
| `@example` | 提供使用示例 | `@example add(1,2) // 3` |
| `@deprecated` | 标记方法已废弃 | `@deprecated 请使用 newMethod 代替` |
| `@type` | （JS中）定义类型 | `@type {string[]}` |
| `@typedef` | （JS中）定义自定义类型 | 用于定义复杂的对象结构 |
