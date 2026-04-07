# Context Sync System - Findings

## Research Findings

### Context Format Options

| Format | Pros | Cons | Verdict |
|--------|------|------|---------|
| **Markdown** | Human readable, LLM友好, 支持frontmatter | 结构化数据需解析 | ✅ 主格式 |
| **JSON** | 机器友好，类型安全 | 对人类不友好，大文件难读 | ✅ 元数据 |
| **YAML** | 可读性好，支持注释 | 解析复杂，缩进敏感 | ⚠️ 可选 |
| **SQLite** | 查询高效 | 二进制，版本控制困难 | ❌ 不考虑 |

### GitHub存储策略

**Option A: Single Repo (推荐)**
```
context-sync/
├── sessions/
│   ├── 2026/
│   │   ├── 04/
│   │   │   ├── 07-session-uuid.md
│   │   │   └── 07-session-uuid.json
├── projects/
│   ├── project-name/
│   │   ├── context.md
│   │   └── memory.json
├── shared/
│   ├── templates/
│   └── schemas/
└── .sync-config.yml
```

**Option B: Multi-Repo**
- 每个项目一个repo
- 更隔离，但更复杂

### Context Types Identified

1. **Session Context** - 单次对话的完整历史
2. **Working Memory** - 当前任务的状态、待办
3. **Long-term Memory** - 用户偏好、项目知识
4. **Project Context** - 代码库状态、架构决策
5. **Agent State** - Agent的配置、能力、工具状态

### Sync Protocol Ideas

**Webhook-based (Event-driven)**
- GitHub webhook → 触发sync
- 需要服务器或serverless function

**Polling-based (Simple)**
- 定期pull
- 修改后push
- 实现简单，延迟较高

**Hybrid (推荐)**
- 本地修改立即push
- 启动时pull
- 定时背景sync

### Security Considerations

- 敏感信息加密（可选GPG）
- GitHub token权限最小化
- 私有仓库
- 支持`.gitignore`模式过滤敏感文件

## Technical Decisions

| Aspect | Decision |
|--------|----------|
| Primary Format | Markdown with JSON frontmatter |
| Storage | Single private GitHub repo |
| Sync Mode | Hybrid (push-on-change + pull-on-start) |
| Identity | Device ID + User ID |
| Conflict | Last-write-wins + manual merge option |

## Open Questions

1. 如何处理大型context（>10MB）的压缩和分片？
2. 是否需要端到端加密？
3. 离线模式如何设计？
4. 版本冲突的自动解决策略？
