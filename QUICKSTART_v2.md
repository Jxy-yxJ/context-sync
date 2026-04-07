# Memory OS v2.0 快速上手指南

> 5分钟掌握 v2.0 核心工作流

---

## 🎯 核心概念（1分钟）

### 三层架构

```
LOGS (日志)          →  CANDIDATE (候选)      →  MEMORY (记忆)
sessions/               candidate/pending/        memory/core/
summaries/              (待审核)                  memory/active/
milestones/                                       memory/archive/

对话记录                AI提取的候选              审核后的长期记忆
短期保留                必须人工审核              稳定认知
```

**关键原则**：AI 不能直接写 memory，必须先创建 candidate，经过审核才能 promote 到 memory。

---

## 🚀 5分钟快速开始

### Step 1: 初始化（如果还没做）

```bash
cd D:\Coding\context-sync-system

# 创建 v2 目录结构
python scripts/init-memory-os-v2.py

# 或者从 v1 迁移
python scripts/migrate-v1-to-v2.py
```

### Step 2: 完成工作，创建候选

```bash
# 完成一个功能后
python auto-sync.py suggest "完成了用户登录功能，决定使用JWT认证"

# 输出示例：
# ============================================================
# 🧠 Memory OS v2.0 - Smart Suggestion
# ============================================================
# Importance Score: 90%
# Reason: Keywords: ['完成', '决定']; Files: 4 changed
# ------------------------------------------------------------
#   📝 候选: candidate-20260407-194955-956e3c2a.md
#
# ✅ 已创建候选记忆 (ID: 956e3c2a)
#    类型: decision
#    重要性: 9/10
#    置信度: 0.90
#
# 💡 运行 'auto-sync.py review' 进行审核
# ============================================================
```

### Step 3: 审核候选

```bash
# 方式1：交互式审核（推荐）
python auto-sync.py review

# 显示：
# ============================================================
# 🔍 Memory OS v2.0 - Review Candidates
# ============================================================
#
# [候选 1/1]
# 类型: decision
# 重要性: 9/10
# 置信度: 0.90
# 内容: 完成了用户登录功能，决定使用JWT认证
#
# [a]pprove / [r]eject / [m]odify / [s]kip? a
#
# ✅ 审核完成: 1 通过, 0 拒绝
# ============================================================

# 方式2：自动审核（高置信度自动通过）
python auto-sync.py review --auto
```

**审核通过后会自动：**
- ✅ 创建 `memory/core/decisions/decision-xxx.md`
- ✅ 归档到 `candidate/approved/`
- ✅ 推送到 GitHub

### Step 4: 设置焦点（可选但推荐）

```bash
# 开始新项目/任务时
python auto-sync.py focus set --project my-project --goal "实现用户认证模块"

# 查看当前焦点
python auto-sync.py focus get

# 输出：
# 🎯 Active Context Status
# [Focus]
#   Type: project
#   Project: my-project
#   Goal: 实现用户认证模块
# [Token Budget]
#   Max total: 8000
#   Memory: 40% (3200 tokens)
#   Context: 60% (4800 tokens)
```

### Step 5: 构建上下文

```bash
# 根据焦点动态构建上下文
python auto-sync.py context

# 输出保存到：.context/state/built-context.md
```

---

## 📋 日常工作流

### 标准工作流

```bash
# 1. 开始工作
python auto-sync.py focus set --project X --goal "具体目标"

# 2. 工作中...（正常对话）

# 3. 完成重要工作
python auto-sync.py suggest "做了什么 + 任何决策/偏好"

# 4. 审核（可以攒几个一起审）
python auto-sync.py review

# 5. 结束会话
python auto-sync.py summary

# 6. 运行维护（每周一次）
python auto-sync.py maintenance --dry-run  # 先看看
python auto-sync.py maintenance            # 执行

# 7. 推送
python auto-sync.py push
```

---

## 🔍 查询和管理

### 查看记忆

```bash
# 列出所有语义记忆
python auto-sync.py memory list

# 输出：
# [CORE]
#   • [decision    ] 使用JWT认证...
#   • [preference  ] 喜欢使用Python...
# [ACTIVE]
#   • [fact        ] API文档地址...
# 总计: 3 个语义记忆

# 统计信息
python auto-sync.py memory stats

# 输出：
# [Semantic Memory]
#   总计: 3 个
#   Core: 2 个
#   Active: 1 个
# [按类型]
#   decision: 1 个
#   preference: 1 个
#   fact: 1 个
# [Candidate Queue]
#   待审核: 0 个
```

---

## 🛡️ Memory 写入准则

### ✅ 应该写入 Memory

| 类型 | 示例 |
|------|------|
| **preference** | "我喜欢使用Python"、"偏好VS Code" |
| **decision** | "决定使用JWT认证"、"选择PostgreSQL" |
| **principle** | "代码简洁优先"、"DRY原则" |
| **fact** | "API限制100req/s"、"数据库地址是xxx" |
| **goal** | "目标是申请TUD"、"计划3个月完成" |

### ❌ 不应该写入 Memory

| 类型 | 说明 | 存到哪里 |
|------|------|---------|
| 对话记录 | "刚才讨论的内容" | `logs/sessions/` |
| 临时信息 | "今天天气" | 不存 |
| 待办事项 | "明天要修复bug" | `tasks/` |
| 未完成想法 | "可能可以用xxx" | 不存 |
| 代码片段 | 具体实现代码 | `logs/sessions/` |

---

## 🔧 维护命令

### 定期维护（每周/每月）

```bash
# 试运行（查看会发生什么）
python auto-sync.py maintenance --dry-run

# 输出示例：
# 🔧 Memory Maintenance Report
# Total memories: 10
# Duplicates found: 2
# Expired memories: 1
# Size overflow: 0
# Actions:
#   - merged 2 duplicate pairs
#   - archived: abc123 (expired)

# 执行维护
python auto-sync.py maintenance
```

---

## 📁 目录结构速查

```
context-sync-data/
├── logs/
│   ├── sessions/      # 对话记录
│   ├── summaries/     # 会话总结
│   ├── milestones/    # 里程碑
│   └── auto/          # 自动日志
│
├── candidate/         # 候选（待审核）
│   ├── pending/       # 待审核 ← suggest 创建到这里
│   ├── approved/      # 已批准 ← review 后归档
│   └── rejected/      # 已拒绝 ← review 后归档
│
├── memory/            # 语义记忆（长期）
│   ├── core/          # 必须加载
│   │   ├── preferences/   # 稳定偏好
│   │   ├── decisions/     # 关键决策
│   │   └── principles/    # 核心原则
│   ├── active/        # 动态加载
│   │   ├── facts/         # 稳定事实
│   │   └── goals/         # 当前目标
│   └── archive/       # 历史归档
│
└── .context/
    └── state/
        ├── active-context.yaml  # 当前焦点配置
        └── built-context.md     # 构建的上下文
```

---

## ❓ 常见问题

### Q: 为什么 suggest 不直接创建 memory？

A: 这是 v2.0 的核心设计。AI 不能直接污染长期记忆，必须经过审核。这样可以：
- 防止低质量记忆进入
- 确保记忆确实重要
- 给用户完全控制权

### Q: 审核太麻烦了，可以自动吗？

A: 可以！高置信度（>0.9）和重要度（>8）的候选会自动通过：

```bash
python auto-sync.py review --auto
```

### Q: 现有的 v1 memory 怎么办？

A: 运行迁移脚本：

```bash
python scripts/migrate-v1-to-v2.py
```

### Q: 如何修改已创建的 memory？

A: 直接编辑文件，然后 push：

```bash
# 文件位置
memory/core/decisions/decision-xxx.md
memory/active/facts/fact-xxx.md

# 编辑后
python auto-sync.py push
```

### Q: 可以删除 memory 吗？

A: 移动到 archive/ 或直接删除：

```bash
# 方式1: 移到归档
mv memory/core/decisions/xxx.md memory/archive/decisions/

# 方式2: 直接删除
rm memory/core/decisions/xxx.md

python auto-sync.py push
```

---

## 📖 更多文档

- [MEMORY_OS_DESIGN.md](./MEMORY_OS_DESIGN.md) - 完整设计文档
- [MEMORY_OS_ARCHITECTURE.md](./MEMORY_OS_ARCHITECTURE.md) - 架构图
- [SCHEMA_v2.md](./SCHEMA_v2.md) - Schema规范

---

**🎉 恭喜！你已掌握 Memory OS v2.0！**

记住核心口诀：**suggest → review → memory**，养成习惯即可。
