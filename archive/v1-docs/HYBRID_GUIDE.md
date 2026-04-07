# Context Sync - 混合模式使用指南

## 什么是混合模式？

**混合模式** = **智能识别** + **会话总结** + **手动控制**

自动判断重要性，但保留最终决定权。

---

## 核心命令

### 1. 开始工作 - 标记会话起点

```bash
python "D:\Coding\context-sync-system\auto-sync.py" start
```

记录会话开始时间，用于后续统计工作时长。

---

### 2. 智能建议 - 判断是否需要创建Context

**方式A：描述你的工作**
```bash
python "D:\Coding\context-sync-system\auto-sync.py" suggest "完成了用户登录功能"
```

**方式B：自动分析当前Git状态**
```bash
python "D:\Coding\context-sync-system\auto-sync.py" check
```

### 输出示例

```
==================================================
CONTEXT SYNC - Smart Suggestion
==================================================
Importance Score: 85%
Reason: Keywords: ['完成']; Files: 3; Lines: +156/-23
Suggested Tags: feature, auth, substantial
--------------------------------------------------
Recommendation: STRONG - Auto-create and push
Command: auto-sync.py create "your summary" --type memory --tags feature,auth,substantial
==================================================
```

### 置信度解释

| 分数 | 建议 | 操作 |
|------|------|------|
| 85%+ | STRONG | 强烈建议创建 |
| 60-84% | MODERATE | 考虑创建 |
| <60% | LOW | 继续工作 |

---

### 3. 创建Context（可选自动推送）

```bash
# 仅创建本地
python "D:\Coding\context-sync-system\auto-sync.py" create \
  "完成了用户登录功能，使用JWT+Redis" \
  --type memory \
  --title "登录功能" \
  --tags feature,auth

# 创建并立即推送
python "D:\Coding\context-sync-system\auto-sync.py" create \
  "完成了用户登录功能" \
  --type memory \
  --title "登录功能" \
  --tags feature,auth
# 然后手动推送:
python "D:\Coding\context-sync-system\auto-sync.py" push
```

---

### 4. 会话结束 - 自动生成总结

```bash
python "D:\Coding\context-sync-system\auto-sync.py" summary
```

自动生成包含以下内容的会话总结：
- 工作时长
- 文件变更统计
- 最近的commits
- 自动推送到GitHub

---

### 5. 同步命令

```bash
# 拉取最新
python "D:\Coding\context-sync-system\auto-sync.py" pull

# 推送本地
python "D:\Coding\context-sync-system\auto-sync.py" push

# 双向同步
python "D:\Coding\context-sync-system\auto-sync.py" sync
```

---

## 完整工作流示例

### 场景：开发一个新功能

```bash
# === 开始工作 ===
python "D:\Coding\context-sync-system\auto-sync.py" start
python "D:\Coding\context-sync-system\auto-sync.py" pull

# ... 写代码 ...

# === 完成一个小功能 ===
python "D:\Coding\context-sync-system\auto-sync.py" suggest "完成了用户登录API"
# 系统提示: Importance Score: 82% (MODERATE)

# 决定创建
python "D:\Coding\context-sync-system\auto-sync.py" create \
  "完成了用户登录API，使用JWT token" \
  --type memory \
  --title "登录API" \
  --tags feature,auth,jwt

# ... 继续工作 ...

# === 完成整个模块 ===
python "D:\Coding\context-sync-system\auto-sync.py" suggest "完成了用户认证模块"
# 系统提示: Importance Score: 91% (STRONG)

# 高置信度，创建并推送
python "D:\Coding\context-sync-system\auto-sync.py" create \
  "完成了完整的用户认证模块，包含登录/注册/密码重置" \
  --type project \
  --title "认证模块完成" \
  --tags milestone,auth,complete

python "D:\Coding\context-sync-system\auto-sync.py" push

# === 会话结束 ===
python "D:\Coding\context-sync-system\auto-sync.py" summary
# 自动生成总结并推送
```

---

## 智能识别规则

系统根据以下因素计算重要性分数：

| 因素 | 加分 | 说明 |
|------|------|------|
| 关键词 | +30% | "完成", "fix", "refactor" 等 |
| 修改行数 | +25% | 超过30行 |
| 影响文件数 | +25% | 超过2个文件 |
| 关键文件 | +10% | 修改了配置/文档文件 |

### 配置阈值

在 `.context/config.yml` 中调整：

```yaml
hybrid:
  heuristic:
    confidence_threshold: 0.6      # 建议阈值
    high_confidence_threshold: 0.85  # 高置信度阈值
    auto_push_high_confidence: true  # 高置信度自动推送
    min_lines_changed: 30
    min_files_affected: 2
    keywords:
      - "完成"
      - "fix"
      - "refactor"
      # ... 添加更多
```

---

## 什么时候不需要创建？

**系统会自动跳过的情况：**
- 修改少于30行
- 只改了1个文件
- 描述中没有关键词
- 工作时长少于15分钟

**手动判断：**
- 简单的格式调整
- 拼写错误修复
- 临时测试代码
- 还在探索的想法

---

## 搜索已有Context

```bash
python "D:\Coding\context-sync-system\context-sync.py" \
  --repo "D:\Coding\context-sync-data" \
  search "JWT"
```

---

## 提示

1. **善用 suggest** - 不确定时先运行 suggest，让系统帮你判断
2. **关键词很重要** - 在描述中包含 "完成/fix/refactor" 等关键词
3. **批量推送** - 可以创建多个context后再统一 push
4. **会话总结必做** - 每次会话结束时运行 summary，自动记录全貌
