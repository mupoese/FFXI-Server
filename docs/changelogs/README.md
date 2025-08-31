# LandSandBoat Server Changelogs

This directory contains automatically generated changelogs for the LandSandBoat Server project, following the format and structure used by the upstream LandSandBoat/server repository.

## Structure

Changelogs are organized by date in the format `changelog-YYYY-MM-DD.md` and are generated automatically based on merged pull requests.

## Format

Each changelog follows the LandSandBoat standard format:

```markdown
## [Project Name] Changelog (YYYY-MM-DD)
- [component] feature description [[#PR](link), [patch](patch-link)] (contributors)
```

### Components
Common component tags used:
- `[sql]` - Database schema changes  
- `[lua]` - Lua script modifications
- `[cpp]` - C++ core changes
- `[core]` - Core server functionality
- `[fix]` - Bug fixes
- `[quest]` - Quest implementations
- `[mission]` - Mission content

## Generation

Changelogs are generated using the `tools/generate_changelog.py` script, which can be run:

```bash
# Generate changelog for last CI period (15 days)
python3 tools/generate_changelog.py ci mupoese/server

# Generate changelog for specific number of days
python3 tools/generate_changelog.py 7 mupoese/server "Custom Server Name"
```

## Integration

The changelog system integrates with:
- GitHub Actions workflows for automatic generation
- `tools/log_manager.py` for development tracking
- ROADMAP.md for documentation of improvements
- .github/copilot-instructions.md for contributor guidance

## Usage in Development

When making changes:
1. Follow proper commit message format (10-72 characters)
2. Use descriptive PR titles that will appear in changelogs
3. Include appropriate component tags in PR descriptions
4. Document major changes in both changelog and ROADMAP.md

For more information, see the main ROADMAP.md and .github/copilot-instructions.md files.
