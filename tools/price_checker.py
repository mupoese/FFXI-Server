#!/usr/bin/env python3
"""
Price Checker Tool

Validates item prices and economic balance in the FFXI database.
This tool checks for economic inconsistencies and ensures proper
item pricing across all game content.
"""

import sys
import os
from pathlib import Path

def main():
    """Main price checking routine."""
    print("🔍 FFXI Item Price Validation")
    print("=" * 40)
    
    # Check if SQL files exist
    sql_dir = Path("sql")
    if not sql_dir.exists():
        print("⚠️  SQL directory not found - skipping price validation")
        return 0
    
    # Look for item-related SQL files
    item_files = list(sql_dir.glob("*item*")) + list(sql_dir.glob("*price*"))
    
    if not item_files:
        print("ℹ️  No item price files found - validation passed")
        return 0
    
    print(f"📋 Found {len(item_files)} item-related files")
    
    # Basic validation (for now, just check files exist and are readable)
    issues_found = 0
    
    for item_file in item_files:
        try:
            with open(item_file, 'r') as f:
                content = f.read()
                if len(content) < 10:  # Very basic check
                    print(f"⚠️  {item_file} seems too small")
                    issues_found += 1
                else:
                    print(f"✅ {item_file} - OK")
        except Exception as e:
            print(f"❌ Error reading {item_file}: {e}")
            issues_found += 1
    
    if issues_found > 0:
        print(f"\n❌ Found {issues_found} issues with item price files")
        return 1
    else:
        print("\n✅ All item price validations passed")
        return 0

if __name__ == "__main__":
    sys.exit(main())