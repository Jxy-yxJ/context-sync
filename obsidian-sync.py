#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian Vault Auto-Sync
监控 Obsidian Context 文件夹并自动同步到 GitHub

使用方法:
1. 直接运行: python obsidian-sync.py
2. 后台运行: python obsidian-sync.py --daemon
3. 手动同步: python obsidian-sync.py --once
4. 指定文件: python obsidian-sync.py --file context/context.md
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Windows编码修复
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 配置路径
OBSIDIAN_VAULT = Path("D:/Embodied AI/Embodied AI with obsidian")
CONTEXT_FOLDER = OBSIDIAN_VAULT / "context"
SYNC_REPO = Path("D:/Coding/context-sync-data")
MEMORY_FOLDER = SYNC_REPO / "memory" / "user"

# 需要同步的文件列表
SYNC_FILES = {
    "context/context.md": {
        "type": "memory",
        "subtype": "user_profile",
        "tags": ["user-profile", "global-context", "personal"],
        "priority": "high"
    }
}


class ObsidianSyncHandler(FileSystemEventHandler):
    """处理 Obsidian 文件变化"""

    def __init__(self):
        self.last_sync = 0
        self.debounce_seconds = 5  # 防抖时间

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        relative_path = file_path.relative_to(OBSIDIAN_VAULT)

        # 检查是否在同步列表中
        if str(relative_path) in SYNC_FILES:
            current_time = time.time()
            if current_time - self.last_sync > self.debounce_seconds:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检测到变化: {relative_path}")
                self.sync_file(str(relative_path))
                self.last_sync = current_time

    def on_created(self, event):
        self.on_modified(event)

    def sync_file(self, relative_path: str):
        """同步单个文件"""
        try:
            source_file = OBSIDIAN_VAULT / relative_path
            config = SYNC_FILES[relative_path]

            # 读取内容
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 转换为 Context Sync 格式
            sync_content = self.convert_to_sync_format(
                content, relative_path, config
            )

            # 生成目标文件名
            timestamp = datetime.now().strftime("%H%M%S")
            target_filename = f"{timestamp}-obsidian-{Path(relative_path).stem}.md"
            target_file = MEMORY_FOLDER / target_filename

            # 写入文件
            target_file.write_text(sync_content, encoding='utf-8')
            print(f"  ✓ 已转换: {target_filename}")

            # Git 提交推送
            self.git_push(target_filename)

        except Exception as e:
            print(f"  ✗ 同步失败: {e}")

    def convert_to_sync_format(self, content: str, source_path: str, config: dict) -> str:
        """转换为 Context Sync 格式"""
        now = datetime.now(timezone.utc).isoformat()

        frontmatter = f"""---
context_id: "obsidian-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
context_type: "{config['type']}"
subtype: "{config.get('subtype', 'general')}"
version: "1.0.0"
created_at: "{now}"
updated_at: "{now}"
source:
  device_id: "local"
  user_id: "Jxy-yxJ"
  agent_type: "obsidian"
  vault: "Embodied AI with obsidian"
  file_path: "{source_path}"
tags: {config.get('tags', [])}
priority: "{config.get('priority', 'normal')}"
relations:
  - type: "source"
    context_id: "obsidian-vault"
---

"""
        return frontmatter + content

    def git_push(self, filename: str):
        """Git 提交并推送"""
        import subprocess

        try:
            os.chdir(SYNC_REPO)

            # 添加文件
            subprocess.run(
                ["git", "add", f"memory/user/{filename}"],
                check=True, capture_output=True
            )

            # 提交
            commit_msg = f"Obsidian sync: {filename}\n\n- Auto-sync from Obsidian vault\n- Source: {OBSIDIAN_VAULT}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                check=True, capture_output=True
            )

            # 推送
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"  ✓ 已推送到 GitHub")
            else:
                print(f"  ✗ 推送失败: {result.stderr}")

        except subprocess.CalledProcessError as e:
            print(f"  ✗ Git 操作失败: {e}")
        except Exception as e:
            print(f"  ✗ 错误: {e}")


def sync_once():
    """手动同步一次"""
    print("=" * 50)
    print("🔄 Obsidian → GitHub 手动同步")
    print("=" * 50)

    handler = ObsidianSyncHandler()

    for relative_path in SYNC_FILES:
        source_file = OBSIDIAN_VAULT / relative_path
        if source_file.exists():
            print(f"\n同步: {relative_path}")
            handler.sync_file(relative_path)
        else:
            print(f"\n✗ 文件不存在: {relative_path}")

    print("\n" + "=" * 50)
    print("✅ 同步完成")


def start_daemon():
    """启动守护进程监控变化"""
    print("=" * 50)
    print("👁️  Obsidian 自动同步守护进程")
    print("=" * 50)
    print(f"监控路径: {CONTEXT_FOLDER}")
    print(f"同步目标: {SYNC_REPO}")
    print("\n按 Ctrl+C 停止\n")

    # 确保目录存在
    CONTEXT_FOLDER.mkdir(parents=True, exist_ok=True)
    MEMORY_FOLDER.mkdir(parents=True, exist_ok=True)

    # 启动监控
    event_handler = ObsidianSyncHandler()
    observer = Observer()
    observer.schedule(event_handler, str(CONTEXT_FOLDER), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n🛑 已停止监控")

    observer.join()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Obsidian Vault Auto-Sync')
    parser.add_argument('--once', action='store_true', help='手动同步一次')
    parser.add_argument('--daemon', action='store_true', help='后台监控模式')
    parser.add_argument('--file', type=str, help='同步指定文件')

    args = parser.parse_args()

    if args.once:
        sync_once()
    elif args.file:
        handler = ObsidianSyncHandler()
        handler.sync_file(args.file)
    else:
        start_daemon()


if __name__ == "__main__":
    main()
