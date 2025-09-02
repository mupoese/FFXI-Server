#!/usr/bin/env python3
"""
Item Enum Validator
Validates that all xi.item.* references in Lua files exist in the item enum table.
This prevents broken item references that could cause runtime errors.
"""

import os
import re
import sys
import argparse
from typing import Set, List, Tuple


def extract_item_enum_names(item_enum_file: str) -> Set[str]:
    """Extract all item names from the item enum file."""
    if not os.path.exists(item_enum_file):
        print(f"Error: Item enum file not found: {item_enum_file}")
        sys.exit(1)
    
    with open(item_enum_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all item names from the enum using regex
    # Pattern matches: ITEM_NAME = value,
    pattern = r'^\s*([A-Z_][A-Z0-9_]*)\s*='
    items = set(re.findall(pattern, content, re.MULTILINE))
    
    return items


def extract_item_references(lua_file: str) -> Set[str]:
    """Extract all xi.item.* references from a Lua file, excluding commented lines."""
    if not os.path.exists(lua_file):
        return set()
    
    try:
        with open(lua_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        # Skip files with encoding issues
        return set()
    
    references = set()
    
    for line in lines:
        # Skip lines that are comments (starting with -- after whitespace)
        stripped_line = line.strip()
        if stripped_line.startswith('--'):
            continue
            
        # Remove inline comments
        comment_pos = line.find('--')
        if comment_pos != -1:
            line = line[:comment_pos]
        
        # Pattern matches: xi.item.ITEM_NAME
        pattern = r'xi\.item\.([A-Z_][A-Z0-9_]*)'
        line_references = re.findall(pattern, line)
        references.update(line_references)
    
    return references


def find_lua_files(directory: str, exclude_dirs: List[str] = None) -> List[str]:
    """Find all Lua files in a directory, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = []
    
    lua_files = []
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from the search
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.lua'):
                lua_files.append(os.path.join(root, file))
    
    return lua_files


def validate_files(files: List[str], valid_items: Set[str]) -> List[Tuple[str, Set[str]]]:
    """Validate item references in the given files."""
    errors = []
    
    for lua_file in files:
        references = extract_item_references(lua_file)
        missing_items = references - valid_items
        
        if missing_items:
            errors.append((lua_file, missing_items))
    
    return errors


def main():
    parser = argparse.ArgumentParser(
        description='Validate xi.item references in Lua files against item enum'
    )
    parser.add_argument(
        '--item-enum',
        default='scripts/enum/item.lua',
        help='Path to item enum open(default: scripts/enum/item.lua)'
    )
    parser.add_argument(
        '--check-files',
        nargs='*',
        help='Specific files to check (default: check all Lua files in scripts/)'
    )
    parser.add_argument(
        '--scripts-dir',
        default='scripts/',
        help='Directory to scan for Lua files (default: scripts/)'
    )
    parser.add_argument(
        '--exclude-dirs',
        nargs='*',
        default=['missions', 'zones'],
        help='Directories to exclude from validation'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    args = parser.parse_args()
    
    # Extract valid item names from enum
    if args.verbose:
        print(f"Loading item enum from: {args.item_enum}")
    
    valid_items = extract_item_enum_names(args.item_enum)
    
    if args.verbose:
        print(f"Found {len(valid_items)} items in enum")
    
    # Determine files to check
    if args.check_files:
        files_to_check = args.check_files
    else:
        files_to_check = find_lua_files(args.scripts_dir, args.exclude_dirs)
    
    if args.verbose:
        print(f"Checking {len(files_to_check)} Lua files")
    
    # Validate files
    errors = validate_files(files_to_check, valid_items)
    
    # Report results
    if errors:
        print("❌ Item enum validation FAILED!")
        print(f"Found {len(errors)} files with missing item references:")
        print()
        
        for file_path, missing_items in errors:
            print(f"File: {file_path}")
            for item in sorted(missing_items):
                print(f"  - Missing: xi.item.{item}")
            print()
        
        sys.exit(1)
    else:
        print("✅ Item enum validation PASSED!")
        print("All item references are valid.")
        sys.exit(0)


if __name__ == '__main__':
    main()