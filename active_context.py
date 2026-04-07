#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory OS v2.0 - Active Context Module
动态上下文构建与管理
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json

if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    except:
        pass

# 路径配置
REPO_PATH = Path("D:/Coding/context-sync-data")


@dataclass
class Focus:
    """当前焦点"""
    type: str  # "project" | "task" | "learning" | "maintenance"
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    goal: Optional[str] = None
    started_at: Optional[str] = None


@dataclass
class MemorySelection:
    """记忆选择配置"""
    pattern: str
    filter_tags: List[str]
    last_accessed_within: str  # e.g., "30d"
    max_count: Optional[int] = None
    min_confidence: float = 0.0


@dataclass
class TokenBudget:
    """Token 预算配置"""
    max_total: int = 8000
    memory_allocation: float = 0.4  # 40%
    context_allocation: float = 0.6  # 60%


class ActiveContextManager:
    """
    Active Context 管理器
    管理当前焦点、记忆选择策略、Token 预算
    """

    def __init__(self):
        self.state_path = REPO_PATH / ".context" / "state" / "active-context.yaml"
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加载状态文件"""
        try:
            import yaml
            if self.state_path.exists():
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[ActiveContext] 加载失败: {e}")
        return self._default_state()

    def _default_state(self) -> Dict:
        """默认状态"""
        return {
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

    def _save_state(self):
        """保存状态"""
        import yaml
        self.state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.state, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def set_focus(
        self,
        focus_type: str = "maintenance",
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        goal: Optional[str] = None
    ):
        """设置当前焦点"""
        self.state["focus"] = {
            "type": focus_type,
            "project_id": project_id,
            "task_id": task_id,
            "goal": goal,
            "started_at": datetime.now(timezone.utc).isoformat()
        }

        # 根据焦点更新 active memory 筛选
        if project_id:
            self._update_filter_for_project(project_id)

        self._save_state()
        print(f"✅ Focus set: [{focus_type}] {goal or project_id or task_id}")

    def _update_filter_for_project(self, project_id: str):
        """根据项目更新筛选器"""
        # 尝试从项目文件读取 tags
        project_file = REPO_PATH / "projects" / f"{project_id}.md"
        if project_file.exists():
            try:
                content = project_file.read_text(encoding='utf-8')
                # 简单提取 tags
                import re
                tags_match = re.search(r'tags:\s*\[(.*?)\]', content)
                if tags_match:
                    tags_str = tags_match.group(1)
                    tags = [t.strip().strip('"') for t in tags_str.split(',')]
                    self.state["memory"]["active"]["filter"]["tags"] = tags
            except:
                pass

    def get_focus(self) -> Dict:
        """获取当前焦点"""
        return self.state.get("focus", {})

    def clear_focus(self):
        """清除焦点"""
        self.state["focus"] = {
            "type": "maintenance",
            "project_id": None,
            "task_id": None,
            "goal": None,
            "started_at": None
        }
        self.state["memory"]["active"]["filter"]["tags"] = []
        self._save_state()
        print("✅ Focus cleared")

    def get_memory_config(self) -> Dict:
        """获取记忆配置"""
        return self.state.get("memory", {})

    def get_token_budget(self) -> TokenBudget:
        """获取 Token 预算"""
        budget = self.state.get("token_budget", {})
        return TokenBudget(
            max_total=budget.get("max_total", 8000),
            memory_allocation=budget.get("memory_allocation", 0.4),
            context_allocation=budget.get("context_allocation", 0.6)
        )

    def display_status(self):
        """显示当前状态"""
        focus = self.get_focus()
        budget = self.get_token_budget()

        print("\n" + "="*60)
        print("🎯 Active Context Status")
        print("="*60)

        # Focus
        print(f"\n[Focus]")
        print(f"  Type: {focus.get('type', 'none')}")
        if focus.get('project_id'):
            print(f"  Project: {focus['project_id']}")
        if focus.get('task_id'):
            print(f"  Task: {focus['task_id']}")
        if focus.get('goal'):
            print(f"  Goal: {focus['goal']}")
        if focus.get('started_at'):
            started = datetime.fromisoformat(focus['started_at'].replace('Z', '+00:00'))
            duration = datetime.now(timezone.utc) - started
            print(f"  Duration: {duration.total_seconds() // 60:.0f} minutes")

        # Memory Config
        memory_cfg = self.get_memory_config()
        active_cfg = memory_cfg.get("active", {})
        filter_cfg = active_cfg.get("filter", {})

        print(f"\n[Memory Filter]")
        print(f"  Pattern: {active_cfg.get('pattern', 'memory/active/**/*')}")
        print(f"  Tags: {filter_cfg.get('tags', [])}")
        print(f"  Last accessed: {filter_cfg.get('last_accessed_within', '30d')}")
        print(f"  Max count: {active_cfg.get('max_count', 50)}")

        # Token Budget
        print(f"\n[Token Budget]")
        print(f"  Max total: {budget.max_total}")
        print(f"  Memory: {budget.memory_allocation*100:.0f}% ({int(budget.max_total * budget.memory_allocation)} tokens)")
        print(f"  Context: {budget.context_allocation*100:.0f}% ({int(budget.max_total * budget.context_allocation)} tokens)")

        print("="*60 + "\n")


class ContextBuilder:
    """
    上下文构建器
    根据 Active Context 配置组装模型输入
    """

    def __init__(self):
        self.active_ctx = ActiveContextManager()
        self.repo_path = REPO_PATH

    def build_context(self) -> str:
        """
        构建完整上下文
        返回组装好的 Markdown 字符串
        """
        parts = []
        budget = self.active_ctx.get_token_budget()
        memory_budget = int(budget.max_total * budget.memory_allocation)

        # 1. System Prompt
        system_prompt = self._get_system_prompt()
        parts.append(("system", 100, system_prompt))

        # 2. Core Memory (必须加载)
        core_memories = self._load_core_memories()
        parts.append(("core_memory", 90, core_memories))

        # 3. Active Memory (根据焦点动态选择，带预算)
        active_memories, tokens_used = self._load_active_memories(memory_budget)
        parts.append(("active_memory", 80, active_memories))

        # 4. Project Context (如果有焦点)
        focus = self.active_ctx.get_focus()
        if focus.get("project_id"):
            project_ctx = self._load_project_context(focus["project_id"])
            parts.append(("project_context", 70, project_ctx))

        # 5. Session History
        session_history = self._load_session_history()
        parts.append(("session_history", 60, session_history))

        # 组装
        return self._assemble(parts)

    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return """# Memory OS v2.0 Active Context

You are working with a disciplined memory system. The following context is selected based on current focus and relevance.

## Context Rules
- CORE memories are essential and always loaded
- ACTIVE memories are dynamically selected based on focus
- All memories have been reviewed and approved by the user
- Session history provides recent context

## Memory Types
- preference: User's stable preferences
- decision: Confirmed decisions
- principle: Reusable principles
- fact: Stable facts
- goal: Current goals
"""

    def _load_core_memories(self) -> str:
        """加载核心记忆"""
        memories = []
        core_dir = self.repo_path / "memory" / "core"

        if not core_dir.exists():
            return ""

        for type_name in ["preferences", "decisions", "principles"]:
            type_dir = core_dir / type_name
            if type_dir.exists():
                for mem_file in sorted(type_dir.glob("*.md")):
                    content = self._read_memory_content(mem_file)
                    if content:
                        memories.append(f"## {type_name.upper()}: {mem_file.stem}\n{content}")

        return "\n\n".join(memories) if memories else ""

    def _load_active_memories(self, budget: int) -> tuple:
        """
        加载活跃记忆（带预算控制）
        返回 (content, tokens_used)
        """
        memories = []
        tokens_used = 0

        active_dir = self.repo_path / "memory" / "active"
        if not active_dir.exists():
            return "", 0

        config = self.active_ctx.get_memory_config().get("active", {})
        filter_tags = config.get("filter", {}).get("tags", [])
        max_count = config.get("max_count", 50)

        # 收集所有候选
        candidates = []
        for mem_file in active_dir.rglob("*.md"):
            mem_data = self._parse_memory_file(mem_file)
            if mem_data:
                score = self._calculate_relevance_score(mem_data, filter_tags)
                candidates.append((score, mem_data, mem_file))

        # 按相关性排序
        candidates.sort(key=lambda x: x[0], reverse=True)

        # 按预算选择
        for score, mem_data, mem_file in candidates[:max_count]:
            content = mem_data.get("content", "")
            tokens = self._estimate_tokens(content)

            if tokens_used + tokens > budget:
                break

            mem_type = mem_data.get("context_type", "memory")
            memories.append(f"## {mem_type.upper()}: {mem_file.stem}\n{content}")
            tokens_used += tokens

            # 更新访问计数
            self._update_access_count(mem_file)

        return "\n\n".join(memories) if memories else "", tokens_used

    def _load_project_context(self, project_id: str) -> str:
        """加载项目上下文"""
        project_file = self.repo_path / "projects" / f"{project_id}.md"
        if project_file.exists():
            return project_file.read_text(encoding='utf-8')
        return ""

    def _load_session_history(self, limit: int = 3) -> str:
        """加载会话历史"""
        sessions = []
        sessions_dir = self.repo_path / "logs" / "sessions"

        if not sessions_dir.exists():
            return ""

        # 获取最近会话
        session_files = sorted(sessions_dir.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

        for session_file in session_files[:limit]:
            content = self._read_memory_content(session_file)
            if content:
                # 只取前500字符
                summary = content[:500]
                sessions.append(f"## Session: {session_file.stem}\n{summary}...")

        return "\n\n".join(sessions) if sessions else ""

    def _parse_memory_file(self, file_path: Path) -> Optional[Dict]:
        """解析记忆文件"""
        try:
            content = file_path.read_text(encoding='utf-8')

            if not content.startswith('---'):
                return None

            parts = content.split('---', 2)
            if len(parts) < 3:
                return None

            import yaml
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()

            result = dict(frontmatter) if frontmatter else {}
            result["content"] = body
            result["file_path"] = str(file_path)
            return result
        except:
            return None

    def _read_memory_content(self, file_path: Path) -> str:
        """读取记忆内容"""
        try:
            data = self._parse_memory_file(file_path)
            return data.get("content", "") if data else ""
        except:
            return ""

    def _calculate_relevance_score(self, mem_data: Dict, filter_tags: List[str]) -> float:
        """
        计算记忆相关性分数
        综合考虑：标签匹配、访问时间、置信度
        """
        score = 0.0

        # 标签匹配
        mem_tags = mem_data.get("tags", [])
        if filter_tags:
            matches = sum(1 for tag in filter_tags if tag in mem_tags)
            score += matches * 2.0

        # 最近访问
        last_accessed = mem_data.get("last_accessed")
        if last_accessed:
            try:
                accessed = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
                days_ago = (datetime.now(timezone.utc) - accessed).days
                if days_ago < 7:
                    score += 3.0
                elif days_ago < 30:
                    score += 2.0
                elif days_ago < 90:
                    score += 1.0
            except:
                pass

        # 置信度
        confidence = mem_data.get("confidence", 0.5)
        score += confidence * 2.0

        # 访问次数
        access_count = mem_data.get("access_count", 0)
        score += min(access_count * 0.1, 1.0)

        return score

    def _estimate_tokens(self, text: str) -> int:
        """估算 token 数"""
        # 简单估算：中文约 1:1.5，英文约 1:0.25
        # 取平均约 1:1
        return len(text) // 2

    def _update_access_count(self, file_path: Path):
        """更新访问计数"""
        try:
            data = self._parse_memory_file(file_path)
            if data:
                data["access_count"] = data.get("access_count", 0) + 1
                data["last_accessed"] = datetime.now(timezone.utc).isoformat()
                # 这里应该写回文件，但为了性能可以先缓存
        except:
            pass

    def _assemble(self, parts: List[tuple]) -> str:
        """组装上下文"""
        # 按优先级排序
        parts.sort(key=lambda x: x[1], reverse=True)

        sections = []
        for part_type, priority, content in parts:
            if content.strip():
                sections.append(f"<!-- Priority: {priority} -->")
                sections.append(f"<!-- Type: {part_type} -->")
                sections.append(content)
                sections.append("")

        return "\n".join(sections)

    def export_for_prompt(self) -> str:
        """导出为可直接使用的 prompt"""
        return self.build_context()


# ============================================
# CLI 接口
# ============================================

def focus_set(focus_type: str = "maintenance", project_id: str = None, task_id: str = None, goal: str = None):
    """设置焦点"""
    manager = ActiveContextManager()
    manager.set_focus(focus_type, project_id, task_id, goal)


def focus_get():
    """获取焦点"""
    manager = ActiveContextManager()
    manager.display_status()


def focus_clear():
    """清除焦点"""
    manager = ActiveContextManager()
    manager.clear_focus()


def build_context():
    """构建上下文"""
    builder = ContextBuilder()
    context = builder.build_context()

    print("\n" + "="*60)
    print("📋 Built Context Preview")
    print("="*60)
    print(context[:2000])
    if len(context) > 2000:
        print(f"\n... ({len(context) - 2000} more characters)")
    print("="*60)

    return context


if __name__ == "__main__":
    # 测试
    print("Active Context Module")
    print("Run 'focus_get()' to test")
