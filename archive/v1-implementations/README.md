# v1.x Implementation Archive

This directory contains legacy v1.x implementations for reference.

## Files

| File | Description | Reference Value |
|------|-------------|-----------------|
| `context-sync.py` | Full v1 CLI implementation with Click | ⭐⭐⭐ CLI design patterns, Git integration |
| `context-sync-simple.py` | Simplified v1 implementation | ⭐⭐ Basic structure |

## Key Features in v1 Implementations

### context-sync.py (Full Version)
- **Click-based CLI** - Argument parsing, command structure
- **GitPython integration** - Git operations wrapper
- **Search functionality** - Content search implementation
- **Complete CRUD** - Create, read, update, delete contexts

### For v2.0 Development Reference

These implementations can be referenced for:
1. Adding `search` command to v2.0
2. Using Click for more robust CLI
3. GitPython for advanced git operations
4. Complete CRUD operations

## Current v2.0 Implementation

The v2.0 uses:
- `auto-sync.py` - Main CLI with argparse
- `memory_os_v2.py` - Core memory management
- `active_context.py` - Context building
- `memory_control.py` - Maintenance operations

---

**Note:** These are reference implementations only. Use v2.0 for production.
