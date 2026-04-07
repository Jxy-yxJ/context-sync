#!/usr/bin/env python3
"""
Context Sync - Cross-device, cross-model, cross-agent context synchronization
跨设备、跨模型、跨Agent的Context同步工具

Usage:
    context-sync create "content" --type session --tags tag1,tag2
    context-sync sync [--direction push|pull|both]
    context-sync search "query" [--type TYPE]
"""

import os
import sys
import json
import yaml
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any

# Optional imports - graceful degradation
try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    print("Warning: 'click' not installed. Using argparse fallback.")

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("Warning: 'gitpython' not installed. Git operations disabled.")


# Windows encoding fix
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    """Context元数据结构"""
    context_id: str
    context_type: str = "session"
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    relations: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextSync:
    """Context同步核心类"""

    CONTEXT_TYPES = ["session", "memory", "project", "task", "agent", "feature", "bugfix"]

    def __init__(self, repo_path: Optional[str] = None, config_path: Optional[str] = None):
        """初始化ContextSync

        Args:
            repo_path: Context仓库路径，默认 ~/context-sync
            config_path: 配置文件路径，默认 ~/.context-sync.yml
        """
        self.repo_path = Path(repo_path or os.path.expanduser("~/context-sync"))
        self.config_path = config_path or os.path.expanduser("~/.context-sync.yml")
        self.config = self._load_config()
        self._init_repo()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "version": "1.0.0",
            "user": {
                "id": os.getenv("USER", os.getenv("USERNAME", "unknown")),
                "email": os.getenv("EMAIL", ""),
            },
            "sync": {
                "mode": "hybrid",
                "auto_push": True,
                "auto_pull": True,
                "poll_interval": 300,
            },
            "storage": {
                "provider": "github",
                "branch": "main",
            },
            "security": {
                "encrypt_sensitive": False,
                "exclude_patterns": ["*.secret", "*password*", "*.env", "*token*"],
            }
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                    # 深度合并配置
                    self._deep_merge(default_config, user_config)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        return default_config

    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """深度合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _init_repo(self) -> None:
        """初始化Git仓库"""
        if not GIT_AVAILABLE:
            return

        if not (self.repo_path / ".git").exists():
            print(f"Initializing git repo at {self.repo_path}")
            self.repo_path.mkdir(parents=True, exist_ok=True)
            self.repo = git.Repo.init(self.repo_path)
            # 创建初始结构
            self._create_initial_structure()
        else:
            self.repo = git.Repo(self.repo_path)

    def _create_initial_structure(self) -> None:
        """创建初始目录结构"""
        dirs = [
            ".context",
            "sessions/2026/04",
            "memory/user",
            "memory/projects",
            "projects",
            "tasks/active",
            "tasks/archive",
            "shared/templates",
            "shared/schemas",
        ]
        for d in dirs:
            (self.repo_path / d).mkdir(parents=True, exist_ok=True)

        # 创建示例配置
        config_example = self.repo_path / ".context" / "config.example.yml"
        with open(config_example, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def _get_device_id(self) -> str:
        """获取设备唯一标识"""
        device_file = self.repo_path / ".context" / "device.yml"
        if device_file.exists():
            try:
                with open(device_file) as f:
                    data = yaml.safe_load(f) or {}
                    return data.get("device_id", "unknown")
            except:
                pass

        # 生成新ID
        device_id = hashlib.sha256(
            f"{os.getenv('USER')}@{os.uname().nodename if hasattr(os, 'uname') else 'unknown'}".encode()
        ).hexdigest()[:16]

        with open(device_file, 'w') as f:
            yaml.dump({"device_id": device_id, "name": "auto-generated"}, f)

        return device_id

    def create_context(self,
                       content: str,
                       context_type: str = "session",
                       tags: Optional[List[str]] = None,
                       title: Optional[str] = None) -> str:
        """创建新的Context

        Args:
            content: Context内容（Markdown格式）
            context_type: Context类型
            tags: 标签列表
            title: 标题（可选）

        Returns:
            Context ID
        """
        if context_type not in self.CONTEXT_TYPES:
            print(f"Warning: Unknown context type '{context_type}', using 'session'")
            context_type = "session"

        context_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # 构建metadata
        metadata = ContextMetadata(
            context_id=context_id,
            context_type=context_type,
            source={
                "device_id": self._get_device_id(),
                "user_id": self.config["user"]["id"],
                "agent_type": os.getenv("AGENT_TYPE", "unknown"),
                "model": os.getenv("MODEL", "unknown"),
            },
            tags=tags or [],
            metadata={
                "size_bytes": len(content.encode('utf-8')),
                "checksum": hashlib.sha256(content.encode()).hexdigest()[:16],
            }
        )

        # 确定存储路径
        if context_type == "session":
            date_path = now.strftime("%Y/%m/%d")
            context_dir = self.repo_path / "sessions" / date_path
        elif context_type == "memory":
            context_dir = self.repo_path / "memory" / "user"
        elif context_type in ["project", "task"]:
            context_dir = self.repo_path / context_type / "active"
        else:
            context_dir = self.repo_path / "sessions" / now.strftime("%Y/%m/%d")

        context_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = now.strftime("%H%M%S")
        safe_title = "" if not title else f"-{title.replace(' ', '-').lower()[:30]}"
        filename = f"{timestamp}-{context_id[:8]}{safe_title}.md"
        file_path = context_dir / filename

        # 构建完整内容
        full_content = self._build_context_file(metadata, content, title)

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

        print(f"[OK] Created: {file_path.relative_to(self.repo_path)}")

        # 自动提交
        if self.config["sync"]["auto_push"] and GIT_AVAILABLE:
            self._commit_and_push(file_path, f"Add {context_type}: {title or context_id[:8]}")

        return context_id

    def _build_context_file(self, metadata: ContextMetadata, content: str, title: Optional[str]) -> str:
        """构建Context文件内容"""
        lines = ["---"]

        # YAML frontmatter
        meta_dict = asdict(metadata)
        yaml_content = yaml.dump(meta_dict, default_flow_style=False, allow_unicode=True)
        lines.append(yaml_content.strip())
        lines.append("---")
        lines.append("")

        # 标题
        if title:
            lines.append(f"# {title}")
            lines.append("")

        # 内容
        lines.append(content)
        lines.append("")

        return "\n".join(lines)

    def _commit_and_push(self, file_path: Path, message: str) -> bool:
        """提交并推送更改"""
        if not GIT_AVAILABLE:
            return False

        try:
            self.repo.index.add([str(file_path.relative_to(self.repo_path))])
            self.repo.index.commit(message)

            # 检查是否有远程仓库
            if self.repo.remotes:
                origin = self.repo.remote("origin")
                origin.push()
                print(f"[OK] Pushed to {origin.url}")
            return True
        except Exception as e:
            print(f"[ERR] Git operation failed: {e}")
            return False

    def sync(self, direction: str = "both") -> None:
        """执行同步

        Args:
            direction: push, pull, or both
        """
        if not GIT_AVAILABLE:
            print("GitPython not available. Cannot sync.")
            return

        if not self.repo.remotes:
            print("No remote configured. Run:")
            print(f"  cd {self.repo_path}")
            print("  git remote add origin <your-github-repo-url>")
            return

        origin = self.repo.remote("origin")

        if direction in ["pull", "both"]:
            try:
                origin.pull()
                print("[OK] Pulled latest changes")
            except Exception as e:
                print(f"[ERR] Pull failed: {e}")

        if direction in ["push", "both"]:
            if self.repo.is_dirty():
                try:
                    self.repo.index.add(["*"])
                    self.repo.index.commit(f"Sync from {self._get_device_id()}")
                    origin.push()
                    print("[OK] Pushed local changes")
                except Exception as e:
                    print(f"[ERR] Push failed: {e}")
            else:
                print("[OK] No local changes to push")

    def search(self, query: str, context_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索Context

        Args:
            query: 搜索关键词
            context_type: 按类型过滤

        Returns:
            匹配结果列表
        """
        results = []
        search_paths = [
            self.repo_path / "sessions",
            self.repo_path / "memory",
            self.repo_path / "projects",
            self.repo_path / "tasks",
        ]

        query_lower = query.lower()

        for base_path in search_paths:
            if not base_path.exists():
                continue

            for md_file in base_path.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding='utf-8')

                    # 解析metadata
                    meta = self._parse_frontmatter(content)

                    # 类型过滤
                    if context_type and meta.get("context_type") != context_type:
                        continue

                    # 搜索匹配
                    if query_lower in content.lower():
                        # 提取预览（排除frontmatter）
                        preview = self._extract_preview(content)

                        results.append({
                            "id": meta.get("context_id", "unknown"),
                            "type": meta.get("context_type", "unknown"),
                            "path": str(md_file.relative_to(self.repo_path)),
                            "created": meta.get("created_at", ""),
                            "tags": meta.get("tags", []),
                            "preview": preview[:150] + "..." if len(preview) > 150 else preview,
                        })
                except Exception as e:
                    continue

        # 按时间排序
        results.sort(key=lambda x: x.get("created", ""), reverse=True)
        return results

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """解析YAML frontmatter"""
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    return yaml.safe_load(parts[1]) or {}
            except:
                pass
        return {}

    def _extract_preview(self, content: str) -> str:
        """提取预览文本（去掉frontmatter）"""
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content


# CLI界面
if CLICK_AVAILABLE:
    @click.group()
    @click.option('--repo', default=None, help='Context repository path')
    @click.option('--config', default=None, help='Config file path')
    @click.pass_context
    def cli(ctx, repo, config):
        """Context Sync - 跨设备、跨模型、跨Agent的Context同步工具"""
        ctx.ensure_object(dict)
        ctx.obj['sync'] = ContextSync(repo, config)

    @cli.command()
    @click.argument('content')
    @click.option('--type', default='session', type=click.Choice(ContextSync.CONTEXT_TYPES),
                  help='Context type')
    @click.option('--tags', multiple=True, help='Tags (can be used multiple times)')
    @click.option('--title', default=None, help='Context title')
    @click.pass_context
    def create(ctx, content, type, tags, title):
        """创建新的Context"""
        sync = ctx.obj['sync']
        context_id = sync.create_context(content, type, list(tags), title)
        print(f"\nContext ID: {context_id}")

    @cli.command()
    @click.option('--direction', type=click.Choice(['push', 'pull', 'both']),
                  default='both', help='Sync direction')
    @click.pass_context
    def sync(ctx, direction):
        """同步Context到/从GitHub"""
        sync = ctx.obj['sync']
        sync.sync(direction)

    @cli.command()
    @click.argument('query')
    @click.option('--type', type=click.Choice(ContextSync.CONTEXT_TYPES),
                  help='Filter by context type')
    @click.pass_context
    def search(ctx, query, type):
        """搜索Context"""
        sync = ctx.obj['sync']
        results = sync.search(query, type)

        if not results:
            print("No results found")
            return

        print(f"\nFound {len(results)} result(s):\n")
        for i, r in enumerate(results, 1):
            print(f"[{i}] [{r['type'].upper()}] {r['id'][:8]}")
            print(f"    Path: {r['path']}")
            print(f"    Tags: {', '.join(r['tags']) if r['tags'] else 'none'}")
            print(f"    Preview: {r['preview'][:80]}...")
            print()

    @cli.command()
    @click.pass_context
    def status(ctx):
        """显示当前状态"""
        sync = ctx.obj['sync']
        print(f"Repository: {sync.repo_path}")
        print(f"Config: {sync.config_path}")
        print(f"User: {sync.config['user']['id']}")
        print(f"Auto-push: {sync.config['sync']['auto_push']}")

        if GIT_AVAILABLE and sync.repo:
            print(f"Git branch: {sync.repo.active_branch}")
            print(f"Is dirty: {sync.repo.is_dirty()}")

else:
    # Argparse fallback
    import argparse

    def main():
        parser = argparse.ArgumentParser(description='Context Sync Tool')
        parser.add_argument('--repo', default=None, help='Repository path')
        parser.add_argument('--config', default=None, help='Config path')

        subparsers = parser.add_subparsers(dest='command')

        # Create
        create_parser = subparsers.add_parser('create', help='Create context')
        create_parser.add_argument('content', help='Content')
        create_parser.add_argument('--type', default='session', choices=ContextSync.CONTEXT_TYPES)
        create_parser.add_argument('--tags', nargs='*', default=[])
        create_parser.add_argument('--title', default=None)

        # Sync
        sync_parser = subparsers.add_parser('sync', help='Sync context')
        sync_parser.add_argument('--direction', choices=['push', 'pull', 'both'], default='both')

        # Search
        search_parser = subparsers.add_parser('search', help='Search context')
        search_parser.add_argument('query', help='Search query')
        search_parser.add_argument('--type', choices=ContextSync.CONTEXT_TYPES)

        args = parser.parse_args()

        sync = ContextSync(args.repo, args.config)

        if args.command == 'create':
            cid = sync.create_context(args.content, args.type, args.tags, args.title)
            print(f"Created: {cid}")
        elif args.command == 'sync':
            sync.sync(args.direction)
        elif args.command == 'search':
            results = sync.search(args.query, args.type)
            for r in results:
                print(f"[{r['type']}] {r['id'][:8]}: {r['preview'][:60]}...")
        else:
            parser.print_help()

    cli = main


if __name__ == '__main__':
    if CLICK_AVAILABLE:
        cli()
    else:
        cli()
