#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory OS v2.0 - Memory Control Module
内存控制：去重、TTL、压缩、大小限制
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Set, Tuple
from difflib import SequenceMatcher
import hashlib

if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    except:
        pass

REPO_PATH = Path("D:/Coding/context-sync-data")


class MemoryDeduplicator:
    """内存去重器"""

    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold

    def find_duplicates(self, memories: List[Dict]) -> List[Tuple[int, int, float]]:
        """
        查找重复的记忆对
        返回: [(idx1, idx2, similarity), ...]
        """
        duplicates = []

        for i in range(len(memories)):
            for j in range(i + 1, len(memories)):
                sim = self._calculate_similarity(memories[i], memories[j])
                if sim >= self.similarity_threshold:
                    duplicates.append((i, j, sim))

        return duplicates

    def _calculate_similarity(self, mem1: Dict, mem2: Dict) -> float:
        """计算两个记忆的相似度"""
        content1 = mem1.get("content", "")
        content2 = mem2.get("content", "")

        # 使用 SequenceMatcher
        similarity = SequenceMatcher(None, content1, content2).ratio()

        # 如果类型相同，增加相似度权重
        if mem1.get("context_type") == mem2.get("context_type"):
            similarity = min(1.0, similarity * 1.1)

        return similarity

    def merge_memories(self, mem1: Dict, mem2: Dict) -> Dict:
        """合并两个相似的记忆"""
        # 保留置信度更高的
        if mem2.get("confidence", 0) > mem1.get("confidence", 0):
            mem1, mem2 = mem2, mem1

        # 合并内容
        merged = mem1.copy()
        merged["content"] = self._merge_content(mem1.get("content", ""), mem2.get("content", ""))
        merged["confidence"] = max(mem1.get("confidence", 0), mem2.get("confidence", 0))
        merged["tags"] = list(set(mem1.get("tags", []) + mem2.get("tags", [])))

        # 记录合并历史
        if "merged_from" not in merged:
            merged["merged_from"] = []
        merged["merged_from"].append(mem2.get("context_id"))

        return merged

    def _merge_content(self, content1: str, content2: str) -> str:
        """合并内容（取并集）"""
        lines1 = set(content1.split('\n'))
        lines2 = set(content2.split('\n'))
        merged = lines1 | lines2
        return '\n'.join(sorted(merged))


class TTLManager:
    """TTL 管理器"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.default_ttl = {
            "preference": None,      # 永久
            "decision": 180,         # 6个月
            "principle": None,       # 永久
            "fact": 365,             # 1年
            "goal": None             # 达成时归档
        }

    def is_expired(self, memory: Dict) -> Tuple[bool, str]:
        """
        检查记忆是否过期
        返回: (is_expired, reason)
        """
        mem_type = memory.get("context_type", "memory")
        created_at = memory.get("created_at")
        last_accessed = memory.get("last_accessed")
        access_count = memory.get("access_count", 0)

        if not created_at:
            return False, "no created_at"

        # 获取 TTL
        ttl_days = memory.get("ttl_days")
        if ttl_days is None:
            ttl_days = self.default_ttl.get(mem_type)

        # 永久有效
        if ttl_days is None:
            return False, "permanent"

        # 计算年龄
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_days = (datetime.now(timezone.utc) - created).days
        except:
            return False, "parse error"

        # 检查 TTL
        if age_days > ttl_days:
            # 如果访问次数少，可以过期
            if access_count < 3:
                return True, f"expired ({age_days}d > {ttl_days}d, {access_count} accesses)"
            else:
                return False, f"extended (high access: {access_count})"

        return False, f"active ({age_days}d / {ttl_days}d)"

    def should_extend_ttl(self, memory: Dict) -> bool:
        """是否应该延长 TTL"""
        access_count = memory.get("access_count", 0)
        last_accessed = memory.get("last_accessed")

        if access_count >= 5:
            return True

        if last_accessed:
            try:
                accessed = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
                days_since_access = (datetime.now(timezone.utc) - accessed).days
                if days_since_access < 30:
                    return True
            except:
                pass

        return False


class MemoryCompressor:
    """记忆压缩器"""

    def __init__(self, cluster_threshold: int = 5, similarity_threshold: float = 0.75):
        self.cluster_threshold = cluster_threshold
        self.similarity_threshold = similarity_threshold

    def find_clusters(self, memories: List[Dict]) -> List[List[Dict]]:
        """
        查找相似记忆的聚类
        """
        clusters = []
        used = set()

        for i, mem1 in enumerate(memories):
            if i in used:
                continue

            cluster = [mem1]
            used.add(i)

            for j, mem2 in enumerate(memories[i+1:], i+1):
                if j in used:
                    continue

                sim = self._quick_similarity(mem1, mem2)
                if sim >= self.similarity_threshold:
                    cluster.append(mem2)
                    used.add(j)

            if len(cluster) >= self.cluster_threshold:
                clusters.append(cluster)

        return clusters

    def _quick_similarity(self, mem1: Dict, mem2: Dict) -> float:
        """快速相似度计算"""
        # 标签匹配
        tags1 = set(mem1.get("tags", []))
        tags2 = set(mem2.get("tags", []))
        tag_sim = len(tags1 & tags2) / max(len(tags1 | tags2), 1)

        # 类型匹配
        type_sim = 1.0 if mem1.get("context_type") == mem2.get("context_type") else 0.0

        # 内容相似度（简化）
        content_sim = SequenceMatcher(
            None,
            mem1.get("content", "")[:200],
            mem2.get("content", "")[:200]
        ).ratio()

        return (tag_sim * 0.3 + type_sim * 0.2 + content_sim * 0.5)

    def compress_cluster(self, cluster: List[Dict]) -> Dict:
        """压缩聚类为一条原则"""
        # 选择最新的作为基础
        base = max(cluster, key=lambda m: m.get("created_at", ""))

        # 提取共同主题
        all_tags = set()
        all_content = []
        for mem in cluster:
            all_tags.update(mem.get("tags", []))
            all_content.append(mem.get("content", ""))

        # 生成原则性总结（简化版）
        principle = base.copy()
        principle["context_type"] = "principle"
        principle["content"] = self._generate_principle_summary(all_content)
        principle["tags"] = list(all_tags)
        principle["compressed_from"] = [m.get("context_id") for m in cluster]
        principle["confidence"] = sum(m.get("confidence", 0.5) for m in cluster) / len(cluster)

        return principle

    def _generate_principle_summary(self, contents: List[str]) -> str:
        """生成原则性总结"""
        # 简化实现：找共同关键词
        words_sets = [set(c.lower().split()) for c in contents]
        common_words = set.intersection(*words_sets) if words_sets else set()

        summary = f"# 原则总结\n\n"
        summary += f"从 {len(contents)} 条相关记忆中提取的共同原则。\n\n"
        summary += f"共同关键词: {', '.join(list(common_words)[:10])}\n\n"
        summary += "## 原始记忆摘要:\n"
        for i, content in enumerate(contents[:3], 1):
            preview = content[:100].replace('\n', ' ')
            summary += f"{i}. {preview}...\n"

        return summary


class SizeLimitEnforcer:
    """大小限制执行器"""

    def __init__(self, limits: Dict):
        self.limits = limits

    def check_limits(self, memories_by_type: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        检查并返回需要删除的记忆
        返回: {type: [memories_to_remove], ...}
        """
        to_remove = {}

        for mem_type, max_count in self.limits.items():
            memories = memories_by_type.get(mem_type, [])

            if len(memories) > max_count:
                # 按访问频率和最后访问时间排序
                sorted_mems = sorted(
                    memories,
                    key=lambda m: (m.get("access_count", 0), m.get("last_accessed", "")),
                    reverse=True
                )

                # 保留最新的
                to_keep = sorted_mems[:max_count]
                to_remove[mem_type] = sorted_mems[max_count:]

        return to_remove

    def get_stats(self, memories_by_type: Dict[str, List[Dict]]) -> Dict:
        """获取统计信息"""
        stats = {}

        for mem_type, max_count in self.limits.items():
            current = len(memories_by_type.get(mem_type, []))
            stats[mem_type] = {
                "current": current,
                "max": max_count,
                "usage": current / max_count if max_count > 0 else 0,
                "status": "ok" if current <= max_count else "overflow"
            }

        return stats


class MaintenanceEngine:
    """维护引擎"""

    def __init__(self):
        self.deduplicator = MemoryDeduplicator()
        self.ttl_manager = TTLManager()
        self.compressor = MemoryCompressor()

    def run_maintenance(
        self,
        dry_run: bool = True,
        dedup: bool = True,
        ttl_check: bool = True,
        compress: bool = False,
        enforce_limits: bool = True
    ) -> Dict:
        """
        运行维护任务

        Args:
            dry_run: 如果 True，只报告不实际执行
            dedup: 是否执行去重
            ttl_check: 是否检查 TTL
            compress: 是否压缩
            enforce_limits: 是否强制执行大小限制

        Returns:
            维护报告
        """
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run,
            "actions": []
        }

        # 1. 加载所有记忆
        all_memories = self._load_all_memories()
        report["total_memories"] = len(all_memories)

        # 2. 去重
        if dedup:
            duplicates = self.deduplicator.find_duplicates(all_memories)
            report["duplicates_found"] = len(duplicates)

            if duplicates and not dry_run:
                # 执行去重
                self._execute_deduplication(all_memories, duplicates)
                report["actions"].append(f"merged {len(duplicates)} duplicate pairs")

        # 3. TTL 检查
        if ttl_check:
            expired = []
            extended = []

            for mem in all_memories:
                is_expired, reason = self.ttl_manager.is_expired(mem)

                if is_expired:
                    expired.append((mem, reason))
                elif self.ttl_manager.should_extend_ttl(mem):
                    extended.append(mem)

            report["expired_count"] = len(expired)
            report["extended_count"] = len(extended)

            if not dry_run:
                # 归档过期的
                for mem, reason in expired:
                    self._archive_memory(mem, reason)
                    report["actions"].append(f"archived: {mem.get('context_id', 'unknown')[:8]}")

                # 延长 TTL
                for mem in extended:
                    self._extend_ttl(mem)

        # 4. 压缩
        if compress:
            clusters = self.compressor.find_clusters(all_memories)
            report["clusters_found"] = len(clusters)

            if clusters and not dry_run:
                for cluster in clusters:
                    principle = self.compressor.compress_cluster(cluster)
                    self._save_compressed_principle(principle, cluster)
                    report["actions"].append(f"compressed {len(cluster)} memories into principle")

        # 5. 大小限制
        if enforce_limits:
            limits = self._get_limits_from_config()
            enforcer = SizeLimitEnforcer(limits)

            memories_by_type = self._group_by_type(all_memories)
            to_remove = enforcer.check_limits(memories_by_type)

            total_overflow = sum(len(mems) for mems in to_remove.values())
            report["overflow_count"] = total_overflow

            if not dry_run:
                for mem_type, memories in to_remove.items():
                    for mem in memories:
                        self._archive_memory(mem, f"size limit for {mem_type}")
                        report["actions"].append(f"archived (overflow): {mem.get('context_id', 'unknown')[:8]}")

        return report

    def _load_all_memories(self) -> List[Dict]:
        """加载所有记忆"""
        memories = []
        memory_dir = REPO_PATH / "memory"

        for tier in ["core", "active"]:
            tier_dir = memory_dir / tier
            if not tier_dir.exists():
                continue

            for mem_file in tier_dir.rglob("*.md"):
                mem = self._parse_memory_file(mem_file)
                if mem:
                    mem["_file_path"] = str(mem_file)
                    memories.append(mem)

        return memories

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
            return result
        except:
            return None

    def _group_by_type(self, memories: List[Dict]) -> Dict[str, List[Dict]]:
        """按类型分组"""
        groups = {}
        for mem in memories:
            mem_type = mem.get("context_type", "memory")
            if mem_type not in groups:
                groups[mem_type] = []
            groups[mem_type].append(mem)
        return groups

    def _get_limits_from_config(self) -> Dict[str, int]:
        """从配置获取限制"""
        try:
            config_path = REPO_PATH / ".context" / "config.yml"
            if config_path.exists():
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}

                limits = config.get("memory_os", {}).get("control", {}).get("max_per_type", {})
                return {
                    "preference": limits.get("preference", 100),
                    "decision": limits.get("decision", 200),
                    "principle": limits.get("principle", 50),
                    "fact": limits.get("fact", 500),
                    "goal": limits.get("goal", 50)
                }
        except:
            pass

        # 默认限制
        return {
            "preference": 100,
            "decision": 200,
            "principle": 50,
            "fact": 500,
            "goal": 50
        }

    def _execute_deduplication(self, memories: List[Dict], duplicates: List[Tuple[int, int, float]]):
        """执行去重"""
        removed_indices = set()

        for i, j, sim in duplicates:
            if i in removed_indices or j in removed_indices:
                continue

            # 合并 i 和 j，删除 j
            merged = self.deduplicator.merge_memories(memories[i], memories[j])
            memories[i] = merged

            # 标记 j 为已删除
            removed_indices.add(j)

            # 删除文件
            file_path = memories[j].get("_file_path")
            if file_path:
                Path(file_path).unlink(missing_ok=True)

    def _archive_memory(self, memory: Dict, reason: str):
        """归档记忆"""
        file_path = memory.get("_file_path")
        if not file_path:
            return

        source = Path(file_path)
        if not source.exists():
            return

        # 确定目标路径
        mem_type = memory.get("context_type", "memory")
        target_dir = REPO_PATH / "memory" / "archive" / f"{mem_type}s"
        target_dir.mkdir(parents=True, exist_ok=True)

        target = target_dir / source.name

        # 移动文件
        import shutil
        shutil.move(source, target)

    def _extend_ttl(self, memory: Dict):
        """延长 TTL"""
        file_path = memory.get("_file_path")
        if not file_path:
            return

        # 读取文件
        path = Path(file_path)
        if not path.exists():
            return

        try:
            content = path.read_text(encoding='utf-8')
            old_ttl = memory.get("ttl_days", 365)
            new_ttl = old_ttl + 180

            # 替换 TTL
            content = content.replace(
                f"ttl_days: {old_ttl}",
                f"ttl_days: {new_ttl}"
            )

            path.write_text(content, encoding='utf-8')
        except:
            pass

    def _save_compressed_principle(self, principle: Dict, cluster: List[Dict]):
        """保存压缩后的原则"""
        import yaml
        from pathlib import Path

        # 保存到 principles
        target_dir = REPO_PATH / "memory" / "core" / "principles"
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"principle-{timestamp}-compressed.md"
        filepath = target_dir / filename

        frontmatter = {k: v for k, v in principle.items() if k != "content"}
        content = principle.get("content", "")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("---\n")
            yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True)
            f.write("---\n\n")
            f.write(content)

        # 归档原始记忆
        for mem in cluster:
            self._archive_memory(mem, "compressed into principle")


def format_report(report: Dict) -> str:
    """格式化维护报告"""
    lines = []
    lines.append("\n" + "="*60)
    lines.append("🔧 Memory Maintenance Report")
    lines.append("="*60)
    lines.append(f"\nTimestamp: {report['timestamp']}")
    lines.append(f"Dry run: {report.get('dry_run', True)}")
    lines.append(f"\nTotal memories: {report.get('total_memories', 0)}")

    if "duplicates_found" in report:
        lines.append(f"Duplicates found: {report['duplicates_found']}")
    if "expired_count" in report:
        lines.append(f"Expired memories: {report['expired_count']}")
    if "extended_count" in report:
        lines.append(f"Extended TTL: {report['extended_count']}")
    if "clusters_found" in report:
        lines.append(f"Compression clusters: {report['clusters_found']}")
    if "overflow_count" in report:
        lines.append(f"Size overflow: {report['overflow_count']}")

    actions = report.get("actions", [])
    if actions:
        lines.append(f"\nActions ({len(actions)}):")
        for action in actions[:10]:
            lines.append(f"  - {action}")
        if len(actions) > 10:
            lines.append(f"  ... and {len(actions) - 10} more")
    else:
        lines.append("\nNo actions taken.")

    lines.append("="*60 + "\n")

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    engine = MaintenanceEngine()
    report = engine.run_maintenance(dry_run=True)
    print(format_report(report))
