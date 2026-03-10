# MechForge AI - 代码质量规范

## 概述

本文档定义了 MechForge AI 项目的代码质量标准，旨在提高代码的可读性、可维护性和性能。

## 代码规范

### 1. 命名规范

- **变量**: 使用 `camelCase`，如 `userName`, `particleCount`
- **常量**: 使用 `UPPER_SNAKE_CASE`，如 `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`
- **函数**: 使用 `camelCase`，动词开头，如 `getUserData()`, `calculateScore()`
- **类/构造函数**: 使用 `PascalCase`，如 `UserManager`, `ParticleSystem`
- **私有方法/变量**: 使用 `_` 前缀，如 `_privateMethod()`, `_internalState`
- **布尔值**: 使用 `is`, `has`, `can` 前缀，如 `isVisible`, `hasError`

### 2. 代码风格

- **缩进**: 2个空格
- **引号**: 单引号
- **分号**: 必须
- **行尾**: Unix 风格 (LF)
- **最大行宽**: 建议 100 字符
- **尾随逗号**: 不允许

### 3. JSDoc 注释规范

所有公共 API 必须包含 JSDoc 注释：

```javascript
/**
 * 函数描述
 * @param {string} param1 - 参数1描述
 * @param {number} [param2=10] - 可选参数，默认值10
 * @param {Object} options - 配置选项
 * @param {boolean} options.enabled - 是否启用
 * @returns {Promise<Object>} 返回结果描述
 * @throws {Error} 错误情况描述
 * @example
 * const result = await myFunction('test', 20, { enabled: true });
 */
```

### 4. 错误处理

- 使用 `try/catch` 捕获异步错误
- 错误对象必须包含描述性消息
- 使用自定义错误类区分错误类型
- 记录错误日志，但避免暴露敏感信息

```javascript
try {
  await riskyOperation();
} catch (error) {
  Logger.error('Operation failed:', error.message);
  throw new AppError('USER_ACTION_FAILED', '操作失败，请重试');
}
```

### 5. 性能优化

- 使用 `const` 和 `let`，避免 `var`
- 优先使用 `const`，只在需要重新赋值时使用 `let`
- 使用箭头函数保持上下文
- 使用解构赋值简化代码
- 使用模板字符串替代字符串拼接
- 避免在循环中创建函数

### 6. 异步编程

- 优先使用 `async/await` 替代回调
- 使用 `Promise.all()` 并行执行独立操作
- 添加超时处理避免长时间等待
- 使用 `AbortController` 取消请求

```javascript
// 好的做法
async function fetchData() {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);
  
  try {
    const response = await fetch(url, { signal: controller.signal });
    return await response.json();
  } finally {
    clearTimeout(timeout);
  }
}

// 并行请求
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts()
]);
```

### 7. DOM 操作

- 使用 `DocumentFragment` 批量插入元素
- 使用事件委托减少监听器数量
- 使用 `requestAnimationFrame` 优化动画
- 使用 `IntersectionObserver` 处理可见性

### 8. 内存管理

- 及时清理事件监听器
- 使用 `WeakMap`/`WeakSet` 避免内存泄漏
- 断开 MutationObserver 和 IntersectionObserver
- 避免循环引用

## ESLint 配置

项目使用 `.eslintrc.json` 配置，包含以下规则：

- **基础规则**: eslint:recommended
- **代码风格**: 缩进、引号、分号等
- **最佳实践**: 变量声明、错误处理等
- **ES6+**: 箭头函数、解构、模板字符串等

运行检查：

```bash
npm run lint
npm run lint:fix  # 自动修复
```

## 代码审查清单

提交代码前请检查：

- [ ] 代码符合 ESLint 规范
- [ ] 所有公共 API 有 JSDoc 注释
- [ ] 错误处理完善
- [ ] 没有 console.log 调试代码
- [ ] 没有未使用的变量
- [ ] 性能敏感代码已优化
- [ ] 内存泄漏风险已处理

## 工具推荐

- **ESLint**: 代码规范检查
- **Prettier**: 代码格式化
- **JSDoc**: 文档生成
- **Chrome DevTools**: 性能分析

## 参考资源

- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)
- [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
