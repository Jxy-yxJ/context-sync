# Context Sync System

跨设备、跨模型、跨Agent的Context同步系统。

## 核心特性

- **跨设备同步** - 多台机器无缝共享Context
- **跨模型兼容** - Claude/GPT/Gemini都能解析
- **跨Agent共享** - 不同AI助手间传递上下文
- **GitHub存储** - 版本控制 + 免费托管
- **Markdown优先** - 人类可读，LLM友好

## 快速开始

### 1. 创建GitHub仓库

```bash
# 创建私有仓库
curl -X POST -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -d '{"name":"my-context-sync","private":true}' \
  https://api.github.com/user/repos

# 克隆到本地
git clone https://github.com/YOUR_USERNAME/my-context-sync.git ~/context-sync
cd ~/context-sync

# 创建目录结构
mkdir -p .context sessions memory projects tasks/shared
```

### 2. 安装CLI工具

```bash
pip install click pyyaml gitpython

# 复制CLI工具到PATH
cp scripts/context-sync.py /usr/local/bin/context-sync
chmod +x /usr/local/bin/context-sync
```

### 3. 配置

创建 `~/context-sync/.context/config.yml`:

```yaml
version: "1.0.0"
user:
  id: "your-github-username"
  email: "your@email.com"
  
sync:
  mode: "hybrid"
  auto_push: true
  auto_pull: true
```

### 4. 使用

```bash
# 创建Context
context-sync create "完成了用户登录功能实现" --type session --tags auth

# 搜索Context
context-sync search "login"

# 同步到GitHub
context-sync sync
```

## Context格式

```markdown
---
context_id: "uuid-v4"
context_type: "session"
version: "1.0.0"
created_at: "2026-04-07T10:30:00Z"
updated_at: "2026-04-07T11:45:00Z"
source:
  device_id: "device-hash"
  user_id: "username"
  agent_type: "claude-code"
  model: "claude-opus-4-6"
tags: ["project-x", "feature-y"]
relations:
  - type: "parent"
    context_id: "parent-uuid"
---

# Context内容

支持完整Markdown语法。
```

## 项目结构

```
context-sync-system/
├── task_plan.md          # 任务计划
├── findings.md           # 研究发现
├── SCHEMA.md            # Context Schema定义
├── IMPLEMENTATION.md    # 详细实现指南
└── scripts/
    └── context-sync.py  # CLI工具
```

## 下一步

1. 阅读 [SCHEMA.md](./SCHEMA.md) 了解Context格式
2. 阅读 [IMPLEMENTATION.md](./IMPLEMENTATION.md) 获取完整实现代码
3. 按照指南设置你的GitHub仓库
4. 开始同步Context！

## 集成示例

### Claude Code Hook

在 `CLAUDE.md` 中添加:

```markdown
After completing a task:
- Run: context-sync create "Summary: ${summary}" --type session
- Run: context-sync sync

Before starting work:
- Run: context-sync sync --direction pull
- Read relevant context from ~/context-sync/memory/
```

### 其他Agent

任何支持以下格式的Agent都能使用:
- 读取: Markdown + YAML frontmatter
- 写入: 同样的格式
- 同步: git push/pull

## License

MIT
