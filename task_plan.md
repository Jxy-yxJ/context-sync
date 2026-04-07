# Context Sync System - Task Plan

## Goal
设计并实现一个跨设备、跨模型、跨agent的context同步系统，使用GitHub作为中央存储。

## Requirements
1. **跨设备同步** - 多台机器上的Claude Code/Prompt/Agent能访问相同context
2. **跨模型兼容** - Claude、GPT、Gemini、本地模型都能解析
3. **跨agent共享** - 不同AI agent之间能无缝传递context
4. **版本控制** - GitHub存储，支持历史回溯
5. **实时/准实时** - 同步延迟可接受（秒级或分钟级）

## Design Phases

### Phase 1: Context Schema Design
- [x] 设计通用context格式（Markdown + YAML frontmatter）
- [x] 定义core context types: session, project, memory, task, agent
- [x] 设计metadata结构（timestamp, source, version, relations）
- [x] 定义compression/encoding策略（gzip可选）

### Phase 2: Storage Architecture
- [x] GitHub repo结构设计（single-repo方案）
- [x] 文件组织（by-date/by-project/by-type）
- [x] 加密/隐私考虑（GPG可选，exclude patterns）

### Phase 3: Client Implementation
- [x] CLI工具设计（Python + Click）
- [x] Claude Code integration方案（MCP/hook）
- [x] Auto-sync机制（hybrid: push-on-change + pull-on-start）
- [ ] 实际代码实现
- [ ] 测试验证

### Phase 4: Multi-Model Adapter
- [ ] OpenAI format adapter
- [ ] Anthropic format adapter
- [ ] Generic LLM format adapter
- [ ] Context pruning/summarization

### Phase 5: Testing & Validation
- [ ] Cross-device sync test
- [ ] Cross-model compatibility test
- [ ] Performance benchmark
- [ ] Documentation

## Current Status
- Status: Phase 3 - 架构设计完成，待实现
- Started: 2026-04-07
- Last Updated: 2026-04-07
- Completed: Phase 1, Phase 2 设计文档

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-07 | Use GitHub as central store | Universal access, version control, free |
