# Context Sync - GitHub + CLAUDE.md 配置完成

## 已完成配置

### 1. 自动同步脚本
**路径**: `D:\Coding\context-sync-system\auto-sync.py`

**功能**:
- `python auto-sync.py push` - 推送本地更改到GitHub
- `python auto-sync.py pull` - 拉取GitHub最新更改
- `python auto-sync.py sync` - 先pull再push
- `python auto-sync.py create "内容" --type session --title "标题"` - 创建context并推送

### 2. CLAUDE.md集成
**路径**: `C:\Users\交响乐\.claude\CLAUDE.md`

已添加Context Sync配置区块，包含：
- 环境变量
- Hook触发规则（完成工作时创建、启动时拉取）
- 命令模板

---

## 下一步：连接GitHub

### 步骤1：创建GitHub仓库

访问 https://github.com/new 创建私有仓库，例如 `my-context-sync`

### 步骤2：添加远程仓库

```bash
cd "D:\Coding\context-sync-data"
git remote add origin https://github.com/YOUR_USERNAME/my-context-sync.git
```

或使用GitHub CLI：
```bash
gh repo create my-context-sync --private --source=. --push
```

### 步骤3：首次推送

```bash
cd "D:\Coding\context-sync-data"
git add .
git commit -m "Initial context sync setup"
git push -u origin main
```

---

## 日常使用

### 手动创建Context
```bash
python "D:\Coding\context-sync-system\auto-sync.py" create \
  "完成了用户登录功能，使用JWT token验证" \
  --type session \
  --title "登录功能实现" \
  --tags auth,jwt,backend
```

### 手动同步
```bash
# 拉取最新（启动时）
python "D:\Coding\context-sync-system\auto-sync.py" pull

# 推送更改（完成工作后）
python "D:\Coding\context-sync-system\auto-sync.py" push

# 双向同步
python "D:\Coding\context-sync-system\auto-sync.py" sync
```

### 搜索Context
```bash
python "D:\Coding\context-sync-system\context-sync.py" \
  --repo "D:\Coding\context-sync-data" \
  search "JWT"
```

---

## Claude Code自动触发

当你在Claude Code中工作时，现在可以使用这些命令：

**完成工作后**（Claude会自动提示）：
```
python D:\Coding\context-sync-system\auto-sync.py create "摘要" --type session
```

**启动新会话时**：
```
python D:\Coding\context-sync-system\auto-sync.py pull
```

---

## 跨设备/跨Agent使用

### 另一台设备
1. 克隆仓库: `git clone https://github.com/YOUR_USERNAME/my-context-sync.git`
2. 安装依赖: `pip install pyyaml`
3. 复制脚本: 使用相同的 `auto-sync.py` 和 `context-sync.py`

### 其他AI Agent（Cursor、Continue等）
直接读取文件：`D:\Coding\context-sync-data\sessions\2026\04\07\*.md`
格式：Markdown + YAML frontmatter，任何LLM都能解析

---

## 文件结构

```
D:\Coding\context-sync-data\
├── .context\config.yml          # 配置文件
├── sessions\2026\04\07\         # 会话历史（按日期）
├── memory\user\                 # 长期记忆
├── memory\projects\             # 项目记忆
├── projects\                    # 项目上下文
└── tasks\active\                # 任务状态
```

---

## 验证清单

- [x] 依赖安装: `click`, `pyyaml`, `gitpython`
- [x] 数据目录: `D:\Coding\context-sync-data`
- [x] CLI工具: `context-sync.py`
- [x] 自动同步: `auto-sync.py`
- [x] CLAUDE.md配置
- [ ] GitHub远程仓库（需要你创建）
- [ ] 首次推送（配置远程后执行）

准备好后告诉我，我可以帮你完成GitHub连接！
