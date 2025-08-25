# Item Enum Validator

This tool validates that all `xi.item.*` references in Lua files exist in the item enum table (`scripts/enum/item.lua`). This prevents broken item references that could cause runtime errors.

## Usage

### Basic usage
```bash
# Check all Lua files in scripts/ directory (excludes missions and zones by default)
python3 tools/ci/item_enum_validator.py

# Check specific files
python3 tools/ci/item_enum_validator.py --check-files scripts/globals/gear_sets.lua scripts/globals/porter_slip_items.lua

# Check specific directory
python3 tools/ci/item_enum_validator.py --scripts-dir scripts/globals

# Verbose output
python3 tools/ci/item_enum_validator.py --verbose
```

### Options

- `--item-enum PATH`: Path to item enum file (default: `scripts/enum/item.lua`)
- `--check-files FILE1 FILE2 ...`: Specific files to check
- `--scripts-dir DIR`: Directory to scan for Lua files (default: `scripts/`)
- `--exclude-dirs DIR1 DIR2 ...`: Directories to exclude from validation (default: `missions zones`)
- `--verbose`: Show detailed output

### Integration with CI

The validator is automatically run as part of the Lua CI checks in `tools/ci/lua.sh`.

### Features

- Validates all `xi.item.ITEM_NAME` references in Lua files
- Ignores commented lines (lines starting with `--` or inline comments)
- Supports exclusion of specific directories
- Provides detailed error reporting showing missing items and their locations
- Returns appropriate exit codes for CI integration (0 = success, 1 = validation failed)

### Testing

Run the test suite to verify the validator works correctly:

```bash
python3 tools/test_item_enum_validator.py
```

## Examples

### Successful validation
```bash
$ python3 tools/ci/item_enum_validator.py --check-files scripts/globals/gear_sets.lua
✅ Item enum validation PASSED!
All item references are valid.
```

### Failed validation
```bash
$ python3 tools/ci/item_enum_validator.py --check-files example.lua
❌ Item enum validation FAILED!
Found 1 files with missing item references:

File: example.lua
  - Missing: xi.item.NONEXISTENT_ITEM
  - Missing: xi.item.ANOTHER_MISSING_ITEM
```

## Implementation Notes

- The validator uses regex to extract item names from both the enum file and Lua files
- Comments are properly handled to avoid false positives
- The tool is designed to be fast and efficient for CI environments
- Error reporting is clear and actionable for developers