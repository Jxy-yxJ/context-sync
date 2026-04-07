# Context Sync - 里程碑式使用指南

## 核心原则

**只在重要时刻创建Context，避免噪音**

---

## 什么时候创建Context？

### ✅ 应该创建

| 场景 | type | 示例 |
|------|------|------|
| 完成功能/模块 | memory | "完成了用户认证模块，使用JWT+Redis" |
| 重要技术决策 | memory | "决定使用PostgreSQL而非MySQL，原因：..." |
| 解决棘手问题 | memory | "修复了内存泄漏，根因是..." |
| 会话结束总结 | session | "本次会话：完成X，待办Y，阻塞Z" |
| 项目里程碑 | project | "v1.0发布，包含功能A/B/C" |

### ❌ 不应该创建

- 简单的文件修改（改几行代码）
- 临时的探索性想法（还在思考中）
- 查询/搜索操作（没有产生新知识）
- 修复拼写错误
- 运行测试

---

## 工作流程

### 工作时（不频繁保存）
```bash
# 不需要每次执行这个！只在完成重要工作时执行
python "D:\Coding\context-sync-system\auto-sync.py" create \
  "完成了XX功能" \
  --type memory \
  --title "功能名称" \
  --tags feature,backend
```

### 会话结束时（批量推送）
```bash
# 1. 创建会话总结
python "D:\Coding\context-sync-system\auto-sync.py" create \
  "本次会话完成：1) 用户登录 2) JWT集成。下一步：权限控制" \
  --type session \
  --title "会话总结-日期"

# 2. 推送所有更改
python "D:\Coding\context-sync-system\auto-sync.py" push
```

### 启动新会话时
```bash
# 拉取最新
python "D:\Coding\context-sync-system\auto-sync.py" pull

# 搜索相关Context
python "D:\Coding\context-sync-system\context-sync.py" \
  --repo "D:\Coding\context-sync-data" \
  search "关键词"
```

---

## Context类型选择

| type | 用途 | 保留时间 |
|------|------|---------|
| session | 单次会话的总结 | 短期 |
| memory | 长期技术知识、决策 | 长期 |
| project | 项目里程碑、状态 | 项目周期 |
| task | 具体任务的进展 | 任务周期 |

**推荐比例**：memory 70% + session 20% + project 10%

---

## 示例模板

### 完成功能
```markdown
---
context_type: memory
tags: [feature, auth, backend]
---

# 用户登录功能

## 实现内容
- JWT token生成与验证
- Redis存储refresh token
- 登录接口 /api/auth/login

## 关键决策
使用RS256算法而非HS256，原因：
1. 私钥可轮换
2. 服务端不存储密钥

## 待办
- [ ] 权限控制
- [ ] Token过期处理
```

### 会话总结
```markdown
---
context_type: session
tags: [summary]
---

# 会话总结 - 2026-04-07

## 完成
- Context Sync系统配置
- GitHub仓库连接

## 待办
- 在另一台设备测试同步

## 阻塞
- 无
```

---

## 搜索技巧

```bash
# 按关键词搜索
python "D:\Coding\context-sync-system\context-sync.py" --repo "D:\Coding\context-sync-data" search "JWT"

# 按类型搜索（修改脚本实现）
# 在sessions/memory/projects目录中搜索
```

---

## 与Claude Code集成

CLAUCE.md已配置为里程碑式触发：

```markdown
After completing SIGNIFICANT work:
  - 完成功能/修复后创建context

Before ending session:
  - 创建会话总结
  - 执行 push
```

---

## 检查清单

创建Context前问自己：

- [ ] 这个信息3个月后我还需要吗？
- [ ] 其他设备/Agent需要知道这个吗？
- [ ] 这是一个"决策"还是"操作"？（只记录决策）
- [ ] 如果搜索相关关键词，我会期望找到这个吗？

如果≥2个是，就创建！
