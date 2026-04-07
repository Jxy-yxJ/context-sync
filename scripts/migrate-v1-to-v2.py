#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory OS v2.0 - Migration Script
Migrate from v1.x to v2.0
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    except:
        pass

REPO_PATH = Path("D:/Coding/context-sync-data")


def print_section(title):
    """打印章节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def check_v2_structure():
    """检查 v2 结构是否已存在"""
    v2_dirs = [
        REPO_PATH / "logs",
        REPO_PATH / "candidate",
        REPO_PATH / "memory" / "core",
        REPO_PATH / "memory" / "active",
    ]
    return all(d.exists() for d in v2_dirs)


def create_v2_structure():
    """创建 v2 目录结构"""
    print_section("Step 1: Creating v2 Directory Structure")

    dirs = [
        # Logs
        "logs/sessions",
        "logs/summaries",
        "logs/milestones",
        "logs/auto",

        # Candidate
        "candidate/pending",
        "candidate/approved",
        "candidate/rejected",

        # Memory - Core
        "memory/core/preferences",
        "memory/core/decisions",
        "memory/core/principles",

        # Memory - Active
        "memory/active/facts",
        "memory/active/goals",

        # Memory - Archive
        "memory/archive/preferences",
        "memory/archive/decisions",
        "memory/archive/principles",
        "memory/archive/facts",
        "memory/archive/goals",

        # State
        ".context/state",
    ]

    for dir_path in dirs:
        full_path = REPO_PATH / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")


def migrate_sessions():
    """迁移 sessions 到 logs/sessions"""
    print_section("Step 2: Migrating Sessions")

    sessions_dir = REPO_PATH / "sessions"
    if not sessions_dir.exists():
        print("  ⏭️  No sessions to migrate")
        return

    logs_sessions = REPO_PATH / "logs" / "sessions"

    # 移动所有 session 文件
    count = 0
    for session_file in sessions_dir.rglob("*.md"):
        # 保持目录结构
        relative = session_file.relative_to(sessions_dir)
        target = logs_sessions / relative
        target.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(session_file, target)
        count += 1

    print(f"  ✅ Migrated {count} session files")

    # 删除空目录
    if sessions_dir.exists():
        shutil.rmtree(sessions_dir)
        print(f"  🗑️  Removed old sessions/ directory")


def classify_memory(file_path: Path) -> tuple:
    """分类记忆到 semantic type"""
    try:
        content = file_path.read_text(encoding='utf-8')

        # 启发式分类
        content_lower = content.lower()

        # Preference
        if any(kw in content_lower for kw in [
            "喜欢", "偏好", "prefer", "favorite", "like to use",
            "习惯", "倾向于", "prefer to"
        ]):
            return "preference", "core"

        # Decision
        if any(kw in content_lower for kw in [
            "决定", "decide", "决策", "选择", "choose",
            "使用", "采用", "选型", "确定"
        ]):
            return "decision", "active"

        # Principle
        if any(kw in content_lower for kw in [
            "原则", "principle", "总是", "never", "should always",
            "最佳实践", "best practice"
        ]):
            return "principle", "core"

        # Goal
        if any(kw in content_lower for kw in [
            "目标", "goal", "计划", "plan to", "aim to",
            "希望完成", "想要"
        ]):
            return "goal", "active"

        # Default
        return "fact", "active"

    except Exception as e:
        print(f"  ⚠️  Error reading {file_path}: {e}")
        return "fact", "active"


def migrate_memories():
    """迁移 memories 到新结构"""
    print_section("Step 3: Migrating Memories")

    memory_user = REPO_PATH / "memory" / "user"
    if not memory_user.exists():
        print("  ⏭️  No memories to migrate")
        return

    # 统计
    stats = {"preference": 0, "decision": 0, "principle": 0, "fact": 0, "goal": 0}

    for mem_file in memory_user.rglob("*.md"):
        mem_type, tier = classify_memory(mem_file)

        # 目标目录
        target_dir = REPO_PATH / "memory" / tier / f"{mem_type}s"
        target_dir.mkdir(parents=True, exist_ok=True)

        # 移动文件
        target = target_dir / mem_file.name
        shutil.move(mem_file, target)

        stats[mem_type] = stats.get(mem_type, 0) + 1

    print(f"  ✅ Migrated memories:")
    for mem_type, count in stats.items():
        if count > 0:
            print(f"     - {mem_type}: {count}")

    # 删除空目录
    if memory_user.exists():
        shutil.rmtree(memory_user)
        print(f"  🗑️  Removed old memory/user/ directory")


def create_active_context_template():
    """创建 Active Context 模板"""
    print_section("Step 4: Creating Active Context Template")

    import yaml

    active_context = {
        "version": "2.0.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "focus": {
            "type": "maintenance",
            "project_id": None,
            "task_id": None,
            "goal": None,
            "started_at": None
        },
        "memory": {
            "core": ["memory/core/**/*"],
            "active": {
                "pattern": "memory/active/**/*",
                "filter": {
                    "tags": [],
                    "last_accessed_within": "30d",
                    "min_confidence": 0.0
                },
                "max_count": 50
            }
        },
        "token_budget": {
            "max_total": 8000,
            "memory_allocation": 0.4,
            "context_allocation": 0.6
        },
        "selection_strategy": "recency_relevance"
    }

    state_path = REPO_PATH / ".context" / "state" / "active-context.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)

    with open(state_path, 'w', encoding='utf-8') as f:
        yaml.dump(active_context, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"  ✅ Created: .context/state/active-context.yaml")


def backup_config():
    """备份配置文件"""
    print_section("Step 5: Backing Up Config")

    config_path = REPO_PATH / ".context" / "config.yml"
    if config_path.exists():
        backup_path = config_path.with_suffix('.yml.v1-backup')
        shutil.copy(config_path, backup_path)
        print(f"  ✅ Backed up config to: {backup_path.name}")


def print_next_steps():
    """打印下一步"""
    print_section("Migration Complete!")

    print("\n✅ Your context repository has been migrated to v2.0!")

    print("\n📋 What's New in v2.0:")
    print("  1. Three-layer architecture: logs → candidate → memory")
    print("  2. AI cannot directly write memory (must be reviewed)")
    print("  3. Active Context with dynamic memory selection")
    print("  4. Memory control: dedup, TTL, size limits")

    print("\n🚀 Next Steps:")
    print("  1. Review migrated memories:")
    print("     auto-sync.py memory list")
    print("")
    print("  2. Set your current focus:")
    print("     auto-sync.py focus set --project your-project")
    print("")
    print("  3. Test the new workflow:")
    print("     auto-sync.py suggest '完成了XX功能'")
    print("     auto-sync.py review")
    print("")
    print("  4. Run maintenance (dry-run first):")
    print("     auto-sync.py maintenance --dry-run")
    print("")
    print("  5. Push to GitHub:")
    print("     auto-sync.py push")

    print("\n📖 Documentation:")
    print("  - SCHEMA_v2.md: Schema specification")
    print("  - MEMORY_OS_DESIGN.md: Architecture design")
    print("  - MEMORY_OS_ROADMAP.md: Implementation plan")

    print("\n⚠️  Important Notes:")
    print("  - Old memories have been classified by heuristics")
    print("  - Review them with 'memory list' and move if needed")
    print("  - The old config is backed up as config.yml.v1-backup")

    print("\n" + "="*60)


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  Memory OS v2.0 Migration Tool")
    print("="*60)

    # 检查是否已经是 v2
    if check_v2_structure():
        print("\n✅ v2.0 structure already exists!")
        response = input("   Re-run migration? (y/N): ").lower()
        if response != 'y':
            print("  Aborted.")
            return 0

    # 确认
    print("\n⚠️  This will migrate your context repository to v2.0")
    print(f"   Repository: {REPO_PATH}")
    print("")
    response = input("   Continue? (y/N): ").lower()
    if response != 'y':
        print("  Aborted.")
        return 0

    try:
        # 执行迁移
        create_v2_structure()
        migrate_sessions()
        migrate_memories()
        create_active_context_template()
        backup_config()

        # 完成
        print_next_steps()

        return 0

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
