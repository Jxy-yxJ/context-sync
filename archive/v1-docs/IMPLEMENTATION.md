# Context Sync - Implementation Guide

## 快速开始

### 1. 创建GitHub仓库

```bash
# 创建私有仓库用于存储context
curl -X POST -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -d '{"name":"my-context-sync","private":true}' \
  https://api.github.com/user/repos
```

### 2. 目录结构

```
my-context-sync/
├── .context/
│   ├── config.yml          # 同步配置
│   └── devices.yml         # 设备注册表
├── sessions/               # 会话历史
│   └── YYYY/MM/DD/
├── memory/                 # 长期记忆
│   ├── user/              # 用户偏好
│   └── projects/          # 项目记忆
├── projects/              # 项目上下文
│   └── {project-name}/
│       ├── context.md
│       └── decisions.md
├── tasks/                 # 任务状态
│   └── active/
│   └── archive/
└── shared/                # 共享资源
    ├── templates/
    └── schemas/
```

### 3. 配置文件模板

**`.context/config.yml`**:
```yaml
version: "1.0.0"
user:
  id: "github-username"
  email: "user@example.com"
  
sync:
  mode: "hybrid"  # push-on-change, pull-on-start, poll
  auto_push: true
  auto_pull: true
  poll_interval: 300  # seconds
  
storage:
  provider: "github"
  repo: "username/my-context-sync"
  branch: "main"
  
security:
  encrypt_sensitive: true
  gpg_key: "key-id"  # optional
  exclude_patterns:
    - "*.secret"
    - "*password*"
    - "*.env"
    
devices:
  this_device:
    id: "auto-generated"
    name: "work-macbook"
    type: "desktop"
```

### 4. 核心CLI工具 (Python)

创建 `context-sync` CLI工具:

```python
#!/usr/bin/env python3
"""Context Sync - Cross-device context synchronization"""

import os
import json
import yaml
import hashlib
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
import click
import git

@dataclass
class ContextMetadata:
    context_id: str
    context_type: str
    version: str = "1.0.0"
    created_at: str = None
    updated_at: str = None
    source: Dict = None
    tags: List[str] = None
    relations: List[Dict] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        if self.updated_at is None:
            self.updated_at = self.created_at

class ContextSync:
    def __init__(self, repo_path: str, config_path: str = None):
        self.repo_path = Path(repo_path)
        self.config = self._load_config(config_path)
        self.repo = git.Repo(repo_path)
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                return yaml.safe_load(f)
        # 默认配置
        return {
            "user": {"id": os.getenv("USER", "unknown")},
            "sync": {"auto_push": True}
        }
    
    def create_context(self, context_type: str, content: str, 
                       tags: List[str] = None) -> str:
        """创建新的context"""
        import uuid
        
        context_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        metadata = ContextMetadata(
            context_id=context_id,
            context_type=context_type,
            source={
                "device_id": self._get_device_id(),
                "user_id": self.config["user"]["id"],
                "agent_type": "claude-code",
                "model": os.getenv("CLAUDE_MODEL", "unknown")
            },
            tags=tags or []
        )
        
        # 构建文件路径
        date_path = now.strftime("%Y/%m/%d")
        context_dir = self.repo_path / "sessions" / date_path
        context_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = context_dir / f"{now.strftime('%H%M%S')}-{context_id[:8]}.md"
        
        # 写入文件
        self._write_context_file(file_path, metadata, content)
        
        # 自动提交
        if self.config["sync"]["auto_push"]:
            self._commit_and_push(file_path, f"Add context: {context_type}")
        
        return str(context_id)
    
    def _write_context_file(self, path: Path, metadata: ContextMetadata, content: str):
        """写入context文件（Markdown + YAML frontmatter）"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            yaml.dump(asdict(metadata), f, default_flow_style=False, allow_unicode=True)
            f.write("---\n\n")
            f.write(content)
    
    def _get_device_id(self) -> str:
        """获取或创建设备ID"""
        device_file = self.repo_path / ".context" / "devices.yml"
        if device_file.exists():
            with open(device_file) as f:
                devices = yaml.safe_load(f)
                return devices.get("this_device", {}).get("id", "unknown")
        return "unknown"
    
    def _commit_and_push(self, file_path: Path, message: str):
        """提交并推送到GitHub"""
        self.repo.index.add([str(file_path)])
        self.repo.index.commit(message)
        origin = self.repo.remote("origin")
        origin.push()
    
    def sync(self, direction: str = "both"):
        """执行同步"""
        if direction in ["pull", "both"]:
            self.repo.remotes.origin.pull()
            click.echo("✓ Pulled latest changes")
        
        if direction in ["push", "both"]:
            if self.repo.is_dirty():
                self.repo.index.add(["*"])
                self.repo.index.commit(f"Sync from {self._get_device_id()}")
                self.repo.remotes.origin.push()
                click.echo("✓ Pushed local changes")
            else:
                click.echo("✓ No local changes to push")
    
    def search(self, query: str, context_type: str = None) -> List[Dict]:
        """搜索context"""
        results = []
        search_paths = [
            self.repo_path / "sessions",
            self.repo_path / "memory",
            self.repo_path / "projects"
        ]
        
        for base_path in search_paths:
            if not base_path.exists():
                continue
            for md_file in base_path.rglob("*.md"):
                content = md_file.read_text(encoding='utf-8')
                if query.lower() in content.lower():
                    # 解析metadata
                    metadata = self._parse_frontmatter(content)
                    if context_type and metadata.get("context_type") != context_type:
                        continue
                    results.append({
                        "id": metadata.get("context_id"),
                        "type": metadata.get("context_type"),
                        "path": str(md_file.relative_to(self.repo_path)),
                        "preview": content[:200]
                    })
        
        return results
    
    def _parse_frontmatter(self, content: str) -> Dict:
        """解析YAML frontmatter"""
        if content.startswith("---"):
            _, frontmatter, _ = content.split("---", 2)
            return yaml.safe_load(frontmatter) or {}
        return {}


# CLI Commands
@click.group()
@click.option('--repo', default="~/context-sync", help='Context repository path')
@click.option('--config', default=None, help='Config file path')
@click.pass_context
def cli(ctx, repo, config):
    """Context Sync - 跨设备context同步工具"""
    repo_path = os.path.expanduser(repo)
    ctx.ensure_object(dict)
    ctx.obj['sync'] = ContextSync(repo_path, config)

@cli.command()
@click.argument('content')
@click.option('--type', default='session', help='Context type')
@click.option('--tags', multiple=True, help='Tags')
@click.pass_context
def create(ctx, content, type, tags):
    """创建新的context"""
    sync = ctx.obj['sync']
    context_id = sync.create_context(type, content, list(tags))
    click.echo(f"✓ Created context: {context_id}")

@cli.command()
@click.option('--direction', type=click.Choice(['push', 'pull', 'both']), default='both')
@click.pass_context
def sync(ctx, direction):
    """同步context到/从GitHub"""
    sync = ctx.obj['sync']
    sync.sync(direction)

@cli.command()
@click.argument('query')
@click.option('--type', help='Filter by context type')
@click.pass_context
def search(ctx, query, type):
    """搜索context"""
    sync = ctx.obj['sync']
    results = sync.search(query, type)
    
    if not results:
        click.echo("No results found")
        return
    
    for r in results:
        click.echo(f"\n[{r['type']}] {r['id'][:8]}")
        click.echo(f"  Path: {r['path']}")
        click.echo(f"  Preview: {r['preview'][:100]}...")

if __name__ == '__main__':
    cli()
```

### 5. 安装依赖

```bash
pip install click pyyaml gitpython
```

### 6. 使用示例

```bash
# 初始化仓库
git clone https://github.com/username/my-context-sync.git ~/context-sync

# 创建context
context-sync create "实现了用户登录功能" --type feature --tags auth,backend

# 同步
context-sync sync

# 搜索
context-sync search "login" --type feature
```

### 7. Claude Code集成

在 `CLAUDE.md` 中添加hook:

```markdown
## Context Sync Hook

After each significant task completion:
1. Run `context-sync create "Summary: ${task_summary}" --type session`
2. Run `context-sync sync`

When starting a new session:
1. Run `context-sync sync --direction pull`
2. Check `~/context-sync/memory/` for relevant context
```

或者使用MCP服务器方式:

```python
# mcp_context_sync.py
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("context-sync")

@app.tool()
async def save_context(content: str, context_type: str = "session") -> str:
    """Save context to sync repository"""
    sync = ContextSync(os.path.expanduser("~/context-sync"))
    context_id = sync.create_context(context_type, content)
    return f"Context saved: {context_id}"

@app.tool()
async def search_context(query: str) -> list:
    """Search for relevant context"""
    sync = ContextSync(os.path.expanduser("~/context-sync"))
    return sync.search(query)
```

---

## 高级功能

### 自动同步Hook

创建 `~/.claude/hooks/context-sync.sh`:

```bash
#!/bin/bash
# 在Claude Code操作后自动同步

REPO_PATH="$HOME/context-sync"

# 检查是否有更新
if [ -d "$REPO_PATH" ]; then
    cd "$REPO_PATH"
    git add -A
    if ! git diff --cached --quiet; then
        git commit -m "Auto-sync: $(date -Iseconds)"
        git push origin main
    fi
fi
```

### Context压缩

对于大型会话，实现分片和压缩:

```python
import gzip
import json

def compress_context(content: str) -> bytes:
    """压缩context内容"""
    return gzip.compress(content.encode('utf-8'))

def decompress_context(data: bytes) -> str:
    """解压context内容"""
    return gzip.decompress(data).decode('utf-8')
```
