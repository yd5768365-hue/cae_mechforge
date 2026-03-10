# 代码审查检查清单

## 提交前自检

### 代码规范
- [ ] 代码符合 ESLint 规范 (`npm run lint`)
- [ ] 代码已格式化 (`npm run format`)
- [ ] 没有 console.log 调试代码
- [ ] 没有未使用的变量和导入
- [ ] 没有 TODO/FIXME 未处理

### 代码质量
- [ ] 函数长度不超过 50 行
- [ ] 文件长度不超过 500 行
- [ ] 使用 const/let，不使用 var
- [ ] 使用 === 而不是 ==
- [ ] 使用箭头函数保持上下文
- [ ] 使用解构赋值简化代码
- [ ] 使用模板字符串替代拼接

### 文档注释
- [ ] 公共 API 有 JSDoc 注释
- [ ] 复杂逻辑有注释说明
- [ ] 函数参数和返回值有类型说明
- [ ] 有使用示例（如适用）

### 错误处理
- [ ] 异步操作有 try/catch
- [ ] 错误有适当的处理
- [ ] 用户输入有验证
- [ ] 边界情况已处理

### 性能优化
- [ ] 没有内存泄漏风险
- [ ] 事件监听器有清理
- [ ] 大数组操作已优化
- [ ] DOM 操作已优化

### 测试
- [ ] 新功能有测试覆盖
- [ ] 现有测试仍然通过
- [ ] 手动测试通过

## 审查要点

### 架构设计
- [ ] 代码结构清晰
- [ ] 职责单一
- [ ] 模块间耦合度低
- [ ] 可扩展性好

### 可读性
- [ ] 命名清晰有意义
- [ ] 代码逻辑清晰
- [ ] 注释准确有用
- [ ] 没有魔法数字/字符串

### 安全性
- [ ] 没有 XSS 风险
- [ ] 没有注入风险
- [ ] 敏感信息未暴露
- [ ] 输入已验证

### 兼容性
- [ ] 浏览器兼容性已考虑
- [ ] 降级方案已准备
- [ ] 特性检测已使用

## 审查流程

1. **自我审查**
   - 作者根据检查清单自检
   - 确保代码质量达标

2. **自动化检查**
   - ESLint 检查
   - 代码质量检查
   - 测试运行

3. **人工审查**
   - 代码逻辑审查
   - 架构设计审查
   - 性能影响评估

4. **反馈处理**
   - 记录审查意见
   - 作者修改代码
   - 重新审查确认

5. **合并发布**
   - 审查通过
   - 合并到主分支
   - 更新文档

## 审查标准

### 必须修复（Blocker）
- 安全漏洞
- 功能缺陷
- 性能严重问题
- 内存泄漏

### 建议修复（Warning）
- 代码风格问题
- 可读性问题
- 潜在风险
- 缺少文档

### 可选优化（Suggestion）
- 代码简化
- 性能优化
- 更好的实现方式

## 常见代码异味

### 函数过长
```javascript
// Bad: 函数做太多事情
function processUser(user) {
  // 100+ lines of code
}

// Good: 拆分成小函数
function processUser(user) {
  validateUser(user);
  enrichUserData(user);
  saveUser(user);
  notifyUser(user);
}
```

### 嵌套过深
```javascript
// Bad: 深层嵌套
if (a) {
  if (b) {
    if (c) {
      // do something
    }
  }
}

// Good: 提前返回
if (!a) return;
if (!b) return;
if (!c) return;
// do something
```

### 重复代码
```javascript
// Bad: 重复逻辑
if (type === 'A') processA(data);
if (type === 'B') processB(data);
if (type === 'C') processC(data);

// Good: 使用映射
const processors = { A: processA, B: processB, C: processC };
processors[type]?.(data);
```

### 魔法值
```javascript
// Bad: 魔法数字
if (status === 3) {
  // do something
}

// Good: 使用常量
const STATUS_COMPLETED = 3;
if (status === STATUS_COMPLETED) {
  // do something
}
```

## 工具使用

```bash
# 代码规范检查
npm run lint

# 自动修复
npm run lint:fix

# 代码质量检查
npm run quality

# 代码格式化
npm run format

# 完整检查
npm run quality:check
```

## 参考资源

- [Code Review Best Practices](https://github.com/lydiahallie/javascript-questions)
- [Clean Code JavaScript](https://github.com/ryanmcdermott/clean-code-javascript)
- [JavaScript Style Guide](https://github.com/airbnb/javascript)
