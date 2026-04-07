# Context Schema v1.0

## Core Design Principles
1. **Model Agnostic** - 任何LLM都能理解
2. **Extensible** - 支持自定义字段
3. **Versioned** - 向前/向后兼容
4. **Human Readable** - Markdown为主格式

---

## Base Context Format

```markdown
---
context_id: "uuid-v4"
context_type: "session" | "memory" | "project" | "task" | "agent"
version: "1.0.0"
created_at: "2026-04-07T10:30:00Z"
updated_at: "2026-04-07T11:45:00Z"
source: {
  device_id: "device-fingerprint",
  user_id: "github-username",
  agent_type: "claude-code" | "cursor" | "continue" | "custom",
  model: "claude-opus-4-6"
}
tags: ["project-x", "feature-y", "urgent"]
relations: [
  { type: "parent", context_id: "parent-uuid" },
  { type: "related", context_id: "related-uuid" }
]
metadata: {
  checksum: "sha256-hash",
  size_bytes: 1024,
  encrypted: false,
  compression: "none" | "gzip"
}
---

# Context Content

## Summary
一句话描述当前context的核心内容。

## Details
详细内容，支持完整的Markdown语法。

## Action Items
- [ ] 待办事项1
- [x] 已完成事项

## Key Decisions
| Decision | Rationale | Date |
|----------|-----------|------|
| 决策1 | 原因 | 2026-04-07 |

## Code Snippets
```python
# 相关代码示例
print("hello")
```

## Attachments
- [file.txt](attachments/file.txt)
