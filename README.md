# Context Sync System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub](https://img.shields.io/badge/storage-GitHub-black.svg)](https://github.com)
[![Memory OS v2](https://img.shields.io/badge/Memory%20OS-v2.0-green.svg)](./MEMORY_OS_DESIGN.md)

**English** | [简体中文](./README.zh-CN.md)

> **An Experiment in "Self-Compilation"**
>
> *"Who am I" should not just be a biological question, but an engineering problem that can be `git clone`d, `diff`ed, and `merge`d.*
>
> The ultimate goal of this project is: **to gradually compile myself into a loadable context**. When I go offline one day, I hope to still:
> ```bash
> context pull me
> # The system continues to function normally
> # Maybe, even submit a PR
> ```
>
> This is not a backup, this is **version-controlled existence**.

---

## Table of Contents

- [Memory OS v2.0](#-memory-os-v20)
- [Core Features](#-core-features)
- [Requirements](#-requirements)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Examples](#-usage-examples)
- [Context Format](#-context-format)
- [Integration Guide](#-integration-guide)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## Memory OS v2.0

The system has been upgraded to a **disciplined Memory OS**. Key changes:

| v1.x | v2.0 |
|------|------|
| Direct memory creation | `suggest` → create **candidate** → `review` → **promote** → memory |
| Unlimited memory growth | **Three-tier architecture** + **review mechanism** + **TTL control** |
| Everything is memory | Memory only stores **stable knowledge** (preferences/decisions/principles/facts) |
| No focus management | **Active Context** dynamically selects memories |

**v2.0 Core Principle**: AI cannot directly write to memory; it must go through review.

## Core Features

- **Cross-Device Sync** - Seamlessly share context across multiple machines
- **Cross-Model Compatible** - Claude/GPT/Gemini can all parse the same format
- **Cross-Agent Sharing** - Pass context between different AI assistants
- **GitHub Storage** - Version control + free hosting + global access
- **Markdown First** - Human-readable, LLM-friendly, preserved forever
- **Disciplined Memory** - v2.0: Three-tier architecture + review mechanism
- **Active Context** - v2.0: Dynamic memory selection with token budget management
- **Memory Control** - v2.0: Deduplication, TTL, compression, size limits

## Requirements

- Python 3.8+
- Git
- GitHub account
- (Optional) GitHub CLI (`gh`)

## Quick Start

### Method 1: Using GitHub CLI (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/context-sync.git
cd context-sync

# 2. Install dependencies
pip install click pyyaml gitpython

# 3. Create data repository
gh repo create my-context-data --private --clone

# 4. Configure environment variables
# Windows
setx CONTEXT_SYNC_REPO "C:\path\to\my-context-data"
setx CONTEXT_SYNC_SCRIPT "C:\path\to\context-sync\auto-sync.py"

# macOS/Linux
export CONTEXT_SYNC_REPO="~/context-sync-data"
export CONTEXT_SYNC_SCRIPT="~/context-sync/auto-sync.py"
```

### Method 2: Manual Setup

```bash
# 1. Clone the main repository
git clone https://github.com/YOUR_USERNAME/context-sync.git

# 2. Create data repository on GitHub (private)
# Visit https://github.com/new to create

# 3. Clone data repository
mkdir -p ~/context-sync-data
cd ~/context-sync-data
git init
git remote add origin https://github.com/YOUR_USERNAME/my-context-data.git

# 4. Create directory structure
mkdir -p .context sessions memory projects tasks shared
```

## Installation

### Install Dependencies

```bash
# Required dependencies
pip install click pyyaml gitpython

# Optional dependencies (for advanced features)
pip install requests rich
```

### Add to PATH (Recommended)

**Windows:**
```powershell
# Using PowerShell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";D:\Coding\context-sync-system", "User")
```

**macOS/Linux:**
```bash
# Add to .bashrc or .zshrc
export PATH="$PATH:/path/to/context-sync-system"
```

## Configuration

Create configuration file `~/.context-sync/config.yml`:

```yaml
version: "1.0.0"
user:
  id: "your-github-username"
  email: "your@email.com"

sync:
  mode: "hybrid"      # hybrid | auto | manual
  auto_push: true
  auto_pull: true

paths:
  repo: "~/context-sync-data"

features:
  milestone_detection: true
  session_summary: true
  smart_suggest: true
```

## Usage Examples

### v2.0 Memory OS Commands

```bash
# ===== Core Workflow (Important) =====

# 1. After completing work, create a memory candidate
#    (Don't write directly to memory; create a candidate for review)
python auto-sync.py suggest "Completed login feature, decided to use JWT authentication"
# Output: Created candidate memory (type: decision, importance: 9/10)
#         Run 'auto-sync.py review' to review

# 2. Review candidate memories
python auto-sync.py review              # Interactive review (recommended)
# Or
python auto-sync.py review --auto       # Auto-approve high-confidence candidates

# 3. After approval, automatically:
#    - Creates memory/core/decisions/decision-xxx.md
#    - Archives candidate to candidate/approved/
#    - Pushes to GitHub

# ===== Active Context =====

# Set current focus
python auto-sync.py focus set --project my-project --goal "Implement user authentication"

# Get current focus
python auto-sync.py focus get

# Build context (dynamically select memories based on focus)
python auto-sync.py context

# ===== Memory Query =====

# List all semantic memories
python auto-sync.py memory list

# Show statistics
python auto-sync.py memory stats

# ===== Maintenance =====

# Run maintenance (deduplication, TTL check, enforce size limits)
python auto-sync.py maintenance --dry-run   # Dry run
python auto-sync.py maintenance             # Execute maintenance

# ===== Basic Commands =====

# Push/Pull
python auto-sync.py push
python auto-sync.py pull

# Generate session summary
python auto-sync.py summary
```

### v1.x Compatible Commands

```bash
# Create context record
python auto-sync.py create "Completed user login feature" --type session --tags auth,feature

# Search historical context
python auto-sync.py search "login"

# Sync to GitHub
python auto-sync.py push

# Pull latest context
python auto-sync.py pull
```

### Hybrid Mode Workflow (Recommended)

```bash
# 1. Start working
python auto-sync.py start

# 2. After completing important work, get smart suggestions
python auto-sync.py suggest "Just completed database migration"

# 3. Create context based on suggestions
python auto-sync.py create "Completed database migration" --type memory --tags migration

# 4. End of session, auto-generate summary
python auto-sync.py summary
```

## Context Format

```markdown
---
context_id: "550e8400-e29b-41d4-a716-446655440000"
context_type: "session"
version: "1.0.0"
created_at: "2026-04-07T10:30:00Z"
updated_at: "2026-04-07T11:45:00Z"
source:
  device_id: "device-hash"
  user_id: "username"
  agent_type: "claude-code"
  model: "claude-opus-4-6"
tags: ["project-x", "feature-y", "auth"]
relations:
  - type: "parent"
    context_id: "parent-uuid"
  - type: "related"
    context_id: "related-uuid"
---

# Session Content

Supports full Markdown syntax, including:
- Code blocks
- Lists
- Tables
- Links

## Key Decisions

- Use JWT for authentication
- Choose PostgreSQL as database
```

## Integration Guide

### Claude Code Integration

Add to `CLAUDE.md`:

```markdown
## Context Sync Integration

After completing SIGNIFICANT work:
- Run: python "D:\Coding\context-sync-system\auto-sync.py" suggest "{{summary}}"
- If suggested, run: python "D:\Coding\context-sync-system\auto-sync.py" create "{{description}}" --type memory

Before ending session:
- Run: python "D:\Coding\context-sync-system\auto-sync.py" summary
- Run: python "D:\Coding\context-sync-system\auto-sync.py" push

Before starting work:
- Run: python "D:\Coding\context-sync-system\auto-sync.py" pull
- Read relevant context from memory/
```

### Other Agent Integration

Any agent supporting these capabilities can use it:
- **Read**: Markdown + YAML frontmatter
- **Write**: Same format
- **Sync**: git push/pull

## Project Structure

```
context-sync-system/
├── auto-sync.py          # Main program: automated sync + smart detection
├── context-sync.py       # Core CLI tool
├── scripts/
│   └── context-sync.py   # Compatible version
├── README.md             # This file
├── LICENSE               # MIT License
├── SCHEMA.md            # Context Schema definition
├── IMPLEMENTATION.md    # Detailed implementation docs
├── HYBRID_GUIDE.md      # Hybrid mode guide
├── MILESTONE_GUIDE.md   # Milestone detection guide
└── .gitignore           # Git ignore rules
```

## Documentation

### v2.0 Memory OS Documentation

| Document | Content |
|----------|---------|
| [MEMORY_OS_DESIGN.md](./MEMORY_OS_DESIGN.md) | **Core Design Document** - Architecture principles, flow design, constraints |
| [MEMORY_OS_ARCHITECTURE.md](./MEMORY_OS_ARCHITECTURE.md) | **Architecture Diagram** - Data flow, control flow, state machine visualization |
| [MEMORY_OS_ROADMAP.md](./MEMORY_OS_ROADMAP.md) | **Implementation Plan** - Phase 1-5 detailed tasks |
| [SCHEMA_v2.md](./SCHEMA_v2.md) | **Schema v2.0** - Three-tier data structure specification |
| [QUICKSTART_v2.md](./QUICKSTART_v2.md) | **Quick Start Guide** - v2.0 workflow tutorial |

### General Documentation

| Document | Content |
|----------|---------|
| [SCHEMA.md](./SCHEMA.md) | Context data format specification (v1.0) |
| [OBSIDIAN_SYNC_GUIDE.md](./OBSIDIAN_SYNC_GUIDE.md) | Obsidian Vault sync guide |

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** this repository
2. Create your **Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. Open a **Pull Request**

### Contribution Areas

- Bug fixes
- New features
- Documentation improvements
- Multi-language support
- Test cases

## Roadmap

- [ ] Web interface for managing context
- [ ] VS Code extension
- [ ] Automatic conflict resolution
- [ ] Context compression and archiving
- [ ] Team collaboration features
- [ ] AI-driven context summarization

## License

This project is open-sourced under the [MIT](LICENSE) license.

## Support

- Submit an [Issue](https://github.com/YOUR_USERNAME/context-sync/issues)
- View [Discussions](https://github.com/YOUR_USERNAME/context-sync/discussions)

## Acknowledgments

Thanks to all developers contributing to cross-agent collaboration!

---

**Give AI assistants persistent memory, let workflows transcend device boundaries.**
