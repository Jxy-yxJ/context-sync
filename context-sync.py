#!/usr/bin/env python3
"""
Context Sync - 跨设备、跨模型、跨Agent的Context同步工具
Quick Start Version
"""

import os
import sys
import yaml
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Windows编码修复
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

class ContextSync:
    """Context同步核心类"""

    CONTEXT_TYPES = ["session", "memory", "project", "task", "agent", "feature", "bugfix"]

    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self._init_dirs()

    def _init_dirs(self):
        """初始化目录结构"""
        dirs = ["sessions/2026/04", "memory/user", "memory/projects", "projects", "tasks/active", ".context"]
        for d in dirs:
            (self.repo_path / d).mkdir(parents=True, exist_ok=True)

    def create_context(self, content, context_type="session", tags=None, title=None):
        """创建新的Context"""
        if context_type not in self.CONTEXT_TYPES:
            context_type = "session"

        context_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # 构建metadata
        meta = {
            "context_id": context_id,
            "context_type": context_type,
            "version": "1.0.0",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "source": {
                "device_id": hashlib.sha256(os.getenv("USER", "unknown").encode()).hexdigest()[:16],
                "user_id": os.getenv("USER", "unknown"),
                "agent_type": "claude-code",
            },
            "tags": tags or [],
            "metadata": {
                "size_bytes": len(content.encode('utf-8')),
                "checksum": hashlib.sha256(content.encode()).hexdigest()[:16],
            }
        }

        # 确定存储路径
        if context_type == "session":
            context_dir = self.repo_path / "sessions" / now.strftime("%Y/%m/%d")
        elif context_type == "memory":
            context_dir = self.repo_path / "memory" / "user"
        else:
            context_dir = self.repo_path / "sessions" / now.strftime("%Y/%m/%d")

        context_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = now.strftime("%H%M%S")
        safe_title = f"-{title.replace(' ', '-').lower()[:20]}" if title else ""
        filename = f"{timestamp}-{context_id[:8]}{safe_title}.md"
        file_path = context_dir / filename

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            yaml.dump(meta, f, default_flow_style=False, allow_unicode=True)
            f.write("---\n\n")
            if title:
                f.write(f"# {title}\n\n")
            f.write(content)

        print(f"[OK] Created: {file_path.relative_to(self.repo_path)}")
        print(f"     Context ID: {context_id}")
        return context_id

    def search(self, query, context_type=None):
        """搜索Context"""
        results = []
        search_paths = [self.repo_path / "sessions", self.repo_path / "memory", self.repo_path / "projects"]

        query_lower = query.lower()

        for base_path in search_paths:
            if not base_path.exists():
                continue
            for md_file in base_path.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    if query_lower in content.lower():
                        results.append({
                            "path": str(md_file.relative_to(self.repo_path)),
                            "preview": content[:100].replace('\n', ' '),
                        })
                except:
                    continue

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Context Sync Tool')
    parser.add_argument('--repo', default='~/context-sync', help='Repository path')

    subparsers = parser.add_subparsers(dest='command')

    # Create
    create_parser = subparsers.add_parser('create', help='Create context')
    create_parser.add_argument('content', help='Content')
    create_parser.add_argument('--type', default='session', choices=ContextSync.CONTEXT_TYPES)
    create_parser.add_argument('--tags', nargs='*', default=[])
    create_parser.add_argument('--title', default=None)

    # Search
    search_parser = subparsers.add_parser('search', help='Search context')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', choices=ContextSync.CONTEXT_TYPES)

    args = parser.parse_args()

    repo_path = os.path.expanduser(args.repo)
    sync = ContextSync(repo_path)

    if args.command == 'create':
        sync.create_context(args.content, args.type, args.tags, args.title)
    elif args.command == 'search':
        results = sync.search(args.query, args.type)
        print(f"\nFound {len(results)} result(s):\n")
        for r in results:
            print(f"  {r['path']}")
            print(f"  Preview: {r['preview'][:60]}...\n")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
