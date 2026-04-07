# Obsidian 自动同步指南

将 Obsidian Vault 中的 context 自动同步到 GitHub 私有仓库。

## 🚀 快速开始

### 1. 手动同步（推荐）

```bash
# 进入项目目录
cd D:\Coding\context-sync-system

# 手动同步一次
python obsidian-sync.py --once

# 或使用 batch 脚本
obsidian-sync.bat --once
```

### 2. 自动监控模式

```bash
# 启动后台监控（文件变化自动同步）
python obsidian-sync.py --daemon

# 或使用 batch 脚本
obsidian-sync.bat --watch
```

## ⚙️ 配置说明

### 同步的文件

默认同步 `context/context.md`，可以在脚本中修改 `SYNC_FILES` 配置：

```python
SYNC_FILES = {
    "context/context.md": {
        "type": "memory",
        "subtype": "user_profile",
        "tags": ["user-profile", "global-context", "personal"],
        "priority": "high"
    }
}
```

### 路径配置

脚本会自动检测以下路径：
- **Obsidian Vault**: `D:/Embodied AI/Embodied AI with obsidian`
- **Context 文件夹**: `context/`
- **GitHub 仓库**: `D:/Coding/context-sync-data`

如需修改，编辑脚本中的路径配置。

## 📋 同步流程

1. **监控变化**: 检测 Obsidian 文件修改
2. **格式转换**: 添加 YAML frontmatter，转换为 Context Sync 格式
3. **本地保存**: 保存到 `memory/user/` 目录
4. **Git 提交**: 自动 commit
5. **推送到 GitHub**: 自动 push 到私有仓库

## 🖥️ Windows 快捷方式

创建桌面快捷方式：

1. 右键 `obsidian-sync.bat`
2. 发送到 → 桌面快捷方式
3. （可选）修改快捷方式属性，添加 `--once` 参数

## 🔧 故障排除

### 依赖安装

```bash
pip install watchdog
```

### 权限问题

如果推送失败，检查 GitHub 认证：
```bash
gh auth status
```

### 编码问题

Windows 默认使用 UTF-8，脚本已自动处理编码。

## 📝 示例输出

```
==================================================
🔄 Obsidian → GitHub 手动同步
==================================================

同步: context/context.md
  ✓ 已转换: 191356-obsidian-context.md
  ✓ 已推送到 GitHub

==================================================
✅ 同步完成
```

## 🔄 与其他工具集成

### Obsidian 插件

可以配合 **Obsidian Git** 插件使用：
1. Obsidian Git 提交到本地仓库
2. obsidian-sync 同步到 GitHub Context 仓库

### 自动化工作流

使用 Windows 任务计划程序定期运行：

```powershell
# 每小时同步一次
schtasks /create /tn "Obsidian Sync" /tr "D:\Coding\context-sync-system\obsidian-sync.bat --once" /sc hourly
```
