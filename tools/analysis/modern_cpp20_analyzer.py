#!/usr/bin/env python3
"""
Modern C++20 Code Analysis Tool for FFXI-Server
Advanced analysis and modernization suggestions for C++20 features and patterns.

This tool analyzes the C++20 codebase and provides intelligent suggestions for
leveraging modern C++20 features, performance optimizations, and best practices
specifically tailored for game server development.
"""

import os
import re
import json
import ast
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import argparse
import subprocess

@dataclass
class ModernizationSuggestion:
    """Modernization suggestion data structure"""
    file_path: str
    line_number: int
    original_code: str
    suggested_code: str
    feature_category: str
    impact_level: str  # low, medium, high
    description: str
    rationale: str
    compatibility_notes: str = ""
    auto_applicable: bool = False

@dataclass
class FeatureUsageStats:
    """Feature usage statistics"""
    feature_name: str
    usage_count: int
    files_using: Set[str]
    examples: List[str]
    recommended_replacements: List[str] = None

class ModernCppAnalyzer:
    """Advanced C++20 modernization analyzer"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).absolute()
        self.suggestions = []
        self.feature_stats = {}
        self.db_path = self.root_dir / "cpp20_analysis.db"
        
        # Modern C++20 feature patterns and their benefits
        self.cpp20_features = {
            'concepts': {
                'patterns': [
                    r'\btemplate\s*<[^>]*>\s*requires\b',
                    r'\bconcept\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=',
                    r'\brequires\s+[a-zA-Z_][a-zA-Z0-9_]*<'
                ],
                'benefits': 'Better template error messages and constraints',
                'impact': 'high'
            },
            'coroutines': {
                'patterns': [
                    r'\bco_await\b',
                    r'\bco_yield\b', 
                    r'\bco_return\b',
                    r'std::coroutine_handle',
                    r'std::suspend_always',
                    r'std::suspend_never'
                ],
                'benefits': 'Asynchronous programming with readable syntax',
                'impact': 'high'
            },
            'modules': {
                'patterns': [
                    r'\bmodule\s+[a-zA-Z_][a-zA-Z0-9_.]*\s*;',
                    r'\bimport\s+[a-zA-Z_][a-zA-Z0-9_.]*\s*;',
                    r'\bexport\s+module\b'
                ],
                'benefits': 'Faster compilation and better encapsulation',
                'impact': 'high'
            },
            'ranges': {
                'patterns': [
                    r'std::ranges::[a-zA-Z_][a-zA-Z0-9_]*',
                    r'std::views::[a-zA-Z_][a-zA-Z0-9_]*',
                    r'ranges::[a-zA-Z_][a-zA-Z0-9_]*',
                    r'views::[a-zA-Z_][a-zA-Z0-9_]*',
                    r'\|\s*std::views::'
                ],
                'benefits': 'Functional programming style and lazy evaluation',
                'impact': 'medium'
            },
            'format': {
                'patterns': [
                    r'std::format\s*\(',
                    r'std::vformat\s*\(',
                    r'std::format_to\s*\('
                ],
                'benefits': 'Type-safe and performance-optimized string formatting',
                'impact': 'medium'
            },
            'span': {
                'patterns': [
                    r'std::span\s*<[^>]*>',
                    r'std::span\s+[a-zA-Z_]'
                ],
                'benefits': 'Safe array and container access',
                'impact': 'medium'
            },
            'string_view': {
                'patterns': [
                    r'std::string_view\s+[a-zA-Z_]',
                    r'std::string_view\s*[,)]'
                ],
                'benefits': 'Efficient string handling without copies',
                'impact': 'medium'
            },
            'optional': {
                'patterns': [
                    r'std::optional\s*<[^>]*>',
                    r'std::nullopt\b',
                    r'\.has_value\(\)',
                    r'\.value_or\('
                ],
                'benefits': 'Explicit nullable value handling',
                'impact': 'medium'
            },
            'variant': {
                'patterns': [
                    r'std::variant\s*<[^>]*>',
                    r'std::visit\s*\(',
                    r'std::holds_alternative\s*<'
                ],
                'benefits': 'Type-safe unions and pattern matching',
                'impact': 'medium'
            },
            'constexpr_if': {
                'patterns': [
                    r'if\s+constexpr\s*\(',
                    r'else\s+if\s+constexpr\s*\('
                ],
                'benefits': 'Compile-time conditional compilation',
                'impact': 'low'
            },
            'structured_bindings': {
                'patterns': [
                    r'auto\s*\[[^]]+\]\s*=',
                    r'auto\s+\[[^]]+\]\s*:'
                ],
                'benefits': 'Clean unpacking of tuples and pairs',
                'impact': 'low'
            },
            'init_statements': {
                'patterns': [
                    r'if\s*\([^;]+;[^)]+\)',
                    r'switch\s*\([^;]+;[^)]+\)',
                    r'for\s*\([^;]*;[^;]*;[^;]*;[^)]*\)'
                ],
                'benefits': 'Cleaner scoping and initialization',
                'impact': 'low'
            }
        }
        
        # Legacy patterns that should be modernized
        self.legacy_patterns = {
            'raw_pointers': {
                'pattern': r'\bnew\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\[[^\]]*\])?\s*\(',
                'suggestion': 'Use std::make_unique or std::make_shared',
                'modern_alternative': 'std::make_unique<T>()',
                'impact': 'high'
            },
            'c_style_casts': {
                'pattern': r'\([a-zA-Z_][a-zA-Z0-9_]*\s*\*?\s*\)\s*[a-zA-Z_0-9]',
                'suggestion': 'Use static_cast, dynamic_cast, or const_cast',
                'modern_alternative': 'static_cast<T>()',
                'impact': 'medium'
            },
            'manual_loops': {
                'pattern': r'for\s*\(\s*(?:auto\s+)?[a-zA-Z_][a-zA-Z0-9_]*\s*=.*\.begin\(\)\s*;.*\.end\(\)',
                'suggestion': 'Use range-based for loop',
                'modern_alternative': 'for (auto&& item : container)',
                'impact': 'medium'
            },
            'printf_style': {
                'pattern': r'\b(?:printf|sprintf|fprintf)\s*\(',
                'suggestion': 'Use std::format for type safety',
                'modern_alternative': 'std::format("format", args...)',
                'impact': 'medium'
            },
            'string_concatenation': {
                'pattern': r'std::string.*\+.*std::string',
                'suggestion': 'Consider std::format for complex string building',
                'modern_alternative': 'std::format("{}{}", str1, str2)',
                'impact': 'low'
            },
            'null_checks': {
                'pattern': r'if\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*!=\s*(?:nullptr|NULL)\s*\)',
                'suggestion': 'Consider std::optional for nullable values',
                'modern_alternative': 'if (optional_value.has_value())',
                'impact': 'medium'
            },
            'const_string_ref': {
                'pattern': r'const\s+std::string\s*&\s+[a-zA-Z_][a-zA-Z0-9_]*',
                'suggestion': 'Use std::string_view for read-only string parameters',
                'modern_alternative': 'std::string_view parameter_name',
                'impact': 'medium'
            },
            'manual_resource_management': {
                'pattern': r'\bdelete\s+[a-zA-Z_][a-zA-Z0-9_]*\s*;',
                'suggestion': 'Use RAII with smart pointers',
                'modern_alternative': 'Use std::unique_ptr or std::shared_ptr',
                'impact': 'high'
            }
        }
        
        # Performance improvement opportunities
        self.performance_patterns = {
            'unnecessary_copies': {
                'pattern': r'auto\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=.*\[.*\]',
                'suggestion': 'Use auto&& or const auto& to avoid copies',
                'impact': 'medium'
            },
            'string_find_zero': {
                'pattern': r'\.find\([^)]+\)\s*!=\s*0',
                'suggestion': 'Use .starts_with() for prefix checking',
                'impact': 'low'
            },
            'empty_check': {
                'pattern': r'\.size\(\)\s*==\s*0',
                'suggestion': 'Use .empty() for clarity and potential optimization',
                'impact': 'low'
            }
        }

    def initialize_database(self):
        """Initialize SQLite database for analysis results"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS modernization_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    line_number INTEGER,
                    original_code TEXT,
                    suggested_code TEXT,
                    feature_category TEXT,
                    impact_level TEXT,
                    description TEXT,
                    rationale TEXT,
                    compatibility_notes TEXT,
                    auto_applicable BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS feature_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_name TEXT NOT NULL,
                    usage_count INTEGER,
                    files_count INTEGER,
                    examples TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_suggestions_file ON modernization_suggestions(file_path)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_suggestions_category ON modernization_suggestions(feature_category)
            ''')

    def analyze_cpp_file(self, file_path: Path) -> List[ModernizationSuggestion]:
        """Analyze a single C++ file for modernization opportunities"""
        suggestions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            relative_path = str(file_path.relative_to(self.root_dir))
            
            # Check for legacy patterns
            suggestions.extend(self.find_legacy_patterns(relative_path, content, lines))
            
            # Check for performance improvements
            suggestions.extend(self.find_performance_improvements(relative_path, content, lines))
            
            # Analyze current C++20 feature usage
            self.analyze_feature_usage(relative_path, content)
            
            # Suggest additional C++20 features
            suggestions.extend(self.suggest_cpp20_features(relative_path, content, lines))
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
        
        return suggestions

    def find_legacy_patterns(self, file_path: str, content: str, lines: List[str]) -> List[ModernizationSuggestion]:
        """Find legacy code patterns that should be modernized"""
        suggestions = []
        
        for pattern_name, pattern_info in self.legacy_patterns.items():
            pattern = pattern_info['pattern']
            
            for i, line in enumerate(lines, 1):
                matches = re.finditer(pattern, line)
                for match in matches:
                    original_code = match.group(0)
                    
                    # Generate specific suggestion based on pattern
                    suggested_code = self.generate_modern_alternative(pattern_name, original_code, line)
                    
                    suggestions.append(ModernizationSuggestion(
                        file_path=file_path,
                        line_number=i,
                        original_code=original_code,
                        suggested_code=suggested_code,
                        feature_category=pattern_name,
                        impact_level=pattern_info['impact'],
                        description=pattern_info['suggestion'],
                        rationale=f"Modernizes {pattern_name.replace('_', ' ')} to use C++20 best practices",
                        auto_applicable=self.is_auto_applicable(pattern_name, line)
                    ))
        
        return suggestions

    def find_performance_improvements(self, file_path: str, content: str, lines: List[str]) -> List[ModernizationSuggestion]:
        """Find performance improvement opportunities"""
        suggestions = []
        
        for pattern_name, pattern_info in self.performance_patterns.items():
            pattern = pattern_info['pattern']
            
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    suggestions.append(ModernizationSuggestion(
                        file_path=file_path,
                        line_number=i,
                        original_code=line.strip(),
                        suggested_code=self.generate_performance_suggestion(pattern_name, line),
                        feature_category='performance',
                        impact_level=pattern_info['impact'],
                        description=pattern_info['suggestion'],
                        rationale="Performance optimization using modern C++ features"
                    ))
        
        return suggestions

    def analyze_feature_usage(self, file_path: str, content: str):
        """Analyze current C++20 feature usage"""
        for feature_name, feature_info in self.cpp20_features.items():
            usage_count = 0
            examples = []
            
            for pattern in feature_info['patterns']:
                matches = re.finditer(pattern, content)
                for match in matches:
                    usage_count += 1
                    if len(examples) < 3:  # Store up to 3 examples
                        examples.append(match.group(0))
            
            if usage_count > 0:
                if feature_name not in self.feature_stats:
                    self.feature_stats[feature_name] = FeatureUsageStats(
                        feature_name=feature_name,
                        usage_count=0,
                        files_using=set(),
                        examples=[]
                    )
                
                self.feature_stats[feature_name].usage_count += usage_count
                self.feature_stats[feature_name].files_using.add(file_path)
                self.feature_stats[feature_name].examples.extend(examples)

    def suggest_cpp20_features(self, file_path: str, content: str, lines: List[str]) -> List[ModernizationSuggestion]:
        """Suggest additional C++20 features that could be beneficial"""
        suggestions = []
        
        # Suggest std::format for printf-style code
        if re.search(r'\bprintf\s*\(|sprintf\s*\(|fprintf\s*\(', content):
            if 'std::format' not in content:
                suggestions.append(ModernizationSuggestion(
                    file_path=file_path,
                    line_number=1,
                    original_code="printf/sprintf usage",
                    suggested_code="#include <format>\n// Use std::format instead",
                    feature_category='format',
                    impact_level='medium',
                    description="Replace printf-style formatting with std::format",
                    rationale="std::format provides type safety and better performance",
                    compatibility_notes="Requires C++20 or later"
                ))
        
        # Suggest std::string_view for const string& parameters
        const_string_refs = re.findall(r'const\s+std::string\s*&\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
        if const_string_refs and 'string_view' not in content:
            suggestions.append(ModernizationSuggestion(
                file_path=file_path,
                line_number=1,
                original_code=f"const std::string& {const_string_refs[0]}",
                suggested_code=f"std::string_view {const_string_refs[0]}",
                feature_category='string_view',
                impact_level='medium',
                description="Use std::string_view for read-only string parameters",
                rationale="Avoids unnecessary string copies and provides flexibility",
                compatibility_notes="Requires C++17 or later"
            ))
        
        # Suggest std::optional for nullptr checks
        if re.search(r'!=\s*nullptr|==\s*nullptr', content) and 'std::optional' not in content:
            suggestions.append(ModernizationSuggestion(
                file_path=file_path,
                line_number=1,
                original_code="pointer != nullptr",
                suggested_code="optional_value.has_value()",
                feature_category='optional',
                impact_level='medium',
                description="Consider std::optional for nullable values",
                rationale="Provides explicit nullable semantics and type safety",
                compatibility_notes="Requires C++17 or later"
            ))
        
        # Suggest ranges for manual loops
        manual_loops = re.findall(r'for\s*\([^)]+\.begin\(\)[^)]+\.end\(\)[^)]*\)', content)
        if manual_loops and 'ranges::' not in content and 'std::ranges::' not in content:
            suggestions.append(ModernizationSuggestion(
                file_path=file_path,
                line_number=1,
                original_code="Manual iterator loops",
                suggested_code="std::ranges algorithms",
                feature_category='ranges',
                impact_level='medium',
                description="Consider std::ranges algorithms for better expressiveness",
                rationale="Ranges provide more readable and composable algorithms",
                compatibility_notes="Requires C++20"
            ))
        
        return suggestions

    def generate_modern_alternative(self, pattern_name: str, original_code: str, full_line: str) -> str:
        """Generate specific modern alternative for legacy code"""
        if pattern_name == 'raw_pointers':
            # Extract type from new expression
            type_match = re.search(r'new\s+([a-zA-Z_][a-zA-Z0-9_]*)', original_code)
            if type_match:
                type_name = type_match.group(1)
                return f"std::make_unique<{type_name}>()"
            return "std::make_unique<T>()"
        
        elif pattern_name == 'c_style_casts':
            return "static_cast<T>(value)"
        
        elif pattern_name == 'manual_loops':
            return "for (auto&& item : container)"
        
        elif pattern_name == 'printf_style':
            return "std::format(\"format\", args...)"
        
        elif pattern_name == 'const_string_ref':
            # Extract parameter name
            param_match = re.search(r'const\s+std::string\s*&\s+([a-zA-Z_][a-zA-Z0-9_]*)', full_line)
            if param_match:
                param_name = param_match.group(1)
                return f"std::string_view {param_name}"
            return "std::string_view parameter"
        
        return self.legacy_patterns[pattern_name]['modern_alternative']

    def generate_performance_suggestion(self, pattern_name: str, line: str) -> str:
        """Generate performance improvement suggestion"""
        if pattern_name == 'unnecessary_copies':
            return line.replace('auto ', 'auto&& ')
        
        elif pattern_name == 'string_find_zero':
            return line.replace('.find(', '.starts_with(').replace(') != 0', ')')
        
        elif pattern_name == 'empty_check':
            return line.replace('.size() == 0', '.empty()')
        
        return line

    def is_auto_applicable(self, pattern_name: str, line: str) -> bool:
        """Check if modernization can be automatically applied"""
        # Conservative approach - only mark simple cases as auto-applicable
        auto_applicable_patterns = {
            'empty_check': True,
            'const_string_ref': False,  # Requires careful analysis
            'c_style_casts': False,     # May change semantics
            'raw_pointers': False,      # Requires ownership analysis
        }
        
        return auto_applicable_patterns.get(pattern_name, False)

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive modernization report"""
        # Group suggestions by category
        suggestions_by_category = defaultdict(list)
        impact_distribution = Counter()
        
        for suggestion in self.suggestions:
            suggestions_by_category[suggestion.feature_category].append(suggestion)
            impact_distribution[suggestion.impact_level] += 1
        
        # File-level statistics
        files_analyzed = set(s.file_path for s in self.suggestions)
        files_with_issues = defaultdict(int)
        
        for suggestion in self.suggestions:
            files_with_issues[suggestion.file_path] += 1
        
        # Feature adoption analysis
        feature_adoption = {}
        for feature_name, feature_info in self.cpp20_features.items():
            if feature_name in self.feature_stats:
                stats = self.feature_stats[feature_name]
                feature_adoption[feature_name] = {
                    'usage_count': stats.usage_count,
                    'files_using': len(stats.files_using),
                    'adoption_rate': len(stats.files_using) / len(files_analyzed) * 100 if files_analyzed else 0,
                    'examples': stats.examples[:3],
                    'benefits': self.cpp20_features[feature_name]['benefits']
                }
            else:
                feature_adoption[feature_name] = {
                    'usage_count': 0,
                    'files_using': 0,
                    'adoption_rate': 0,
                    'examples': [],
                    'benefits': self.cpp20_features[feature_name]['benefits']
                }
        
        # Priority recommendations
        priority_recommendations = []
        
        # High-impact suggestions
        high_impact_count = impact_distribution['high']
        if high_impact_count > 0:
            priority_recommendations.append(
                f"Address {high_impact_count} high-impact modernization opportunities"
            )
        
        # Low feature adoption
        low_adoption_features = [
            name for name, stats in feature_adoption.items() 
            if stats['adoption_rate'] < 10 and self.cpp20_features[name]['impact'] == 'high'
        ]
        
        if low_adoption_features:
            priority_recommendations.append(
                f"Consider adopting high-impact C++20 features: {', '.join(low_adoption_features)}"
            )
        
        # Auto-fixable issues
        auto_fixable_count = sum(1 for s in self.suggestions if s.auto_applicable)
        if auto_fixable_count > 0:
            priority_recommendations.append(
                f"Apply {auto_fixable_count} automatic modernization fixes"
            )
        
        return {
            'analysis_summary': {
                'total_suggestions': len(self.suggestions),
                'files_analyzed': len(files_analyzed),
                'files_with_suggestions': len(files_with_issues),
                'auto_fixable_suggestions': auto_fixable_count
            },
            'impact_distribution': dict(impact_distribution),
            'suggestions_by_category': {
                category: len(suggestions) 
                for category, suggestions in suggestions_by_category.items()
            },
            'feature_adoption': feature_adoption,
            'top_files_needing_attention': sorted(
                files_with_issues.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            'priority_recommendations': priority_recommendations,
            'modernization_score': self.calculate_modernization_score()
        }

    def calculate_modernization_score(self) -> Dict[str, float]:
        """Calculate overall modernization score"""
        if not self.suggestions:
            return {'overall': 100.0, 'breakdown': {}}
        
        # Count total opportunities
        total_files = len(set(s.file_path for s in self.suggestions))
        total_suggestions = len(self.suggestions)
        
        # Weight by impact
        weighted_issues = 0
        for suggestion in self.suggestions:
            if suggestion.impact_level == 'high':
                weighted_issues += 3
            elif suggestion.impact_level == 'medium':
                weighted_issues += 2
            else:
                weighted_issues += 1
        
        # Calculate scores (0-100, higher is better)
        max_possible_weighted = total_suggestions * 3  # If all were high impact
        issue_score = max(0, 100 - (weighted_issues / max_possible_weighted * 100))
        
        # Feature adoption score
        adopted_features = len([f for f in self.feature_stats if self.feature_stats[f].usage_count > 0])
        total_features = len(self.cpp20_features)
        adoption_score = (adopted_features / total_features) * 100
        
        # Overall score
        overall_score = (issue_score * 0.7 + adoption_score * 0.3)
        
        return {
            'overall': round(overall_score, 1),
            'breakdown': {
                'code_quality': round(issue_score, 1),
                'feature_adoption': round(adoption_score, 1)
            }
        }

    def save_to_database(self):
        """Save analysis results to database"""
        with sqlite3.connect(self.db_path) as conn:
            # Clear previous results
            conn.execute("DELETE FROM modernization_suggestions")
            conn.execute("DELETE FROM feature_usage")
            
            # Save suggestions
            for suggestion in self.suggestions:
                conn.execute('''
                    INSERT INTO modernization_suggestions (
                        file_path, line_number, original_code, suggested_code,
                        feature_category, impact_level, description, rationale,
                        compatibility_notes, auto_applicable
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    suggestion.file_path,
                    suggestion.line_number,
                    suggestion.original_code,
                    suggestion.suggested_code,
                    suggestion.feature_category,
                    suggestion.impact_level,
                    suggestion.description,
                    suggestion.rationale,
                    suggestion.compatibility_notes,
                    suggestion.auto_applicable
                ))
            
            # Save feature usage
            for feature_name, stats in self.feature_stats.items():
                conn.execute('''
                    INSERT INTO feature_usage (
                        feature_name, usage_count, files_count, examples
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    feature_name,
                    stats.usage_count,
                    len(stats.files_using),
                    json.dumps(stats.examples)
                ))

    def run_analysis(self):
        """Run comprehensive C++20 analysis"""
        print("🔍 Starting Modern C++20 Code Analysis...")
        
        # Initialize database
        self.initialize_database()
        
        # Find C++ files
        cpp_files = []
        for ext in ['.cpp', '.hpp', '.h', '.cc', '.cxx', '.hxx']:
            cpp_files.extend(self.root_dir.glob(f"**/*{ext}"))
        
        # Filter out build directories and external dependencies
        skip_dirs = ['build', 'ext', '.git', 'node_modules', 'third_party']
        cpp_files = [f for f in cpp_files if not any(skip in str(f) for skip in skip_dirs)]
        
        print(f"📁 Analyzing {len(cpp_files)} C++ files...")
        
        # Analyze each file
        for i, file_path in enumerate(cpp_files):
            if i % 10 == 0 and i > 0:
                print(f"Progress: {i}/{len(cpp_files)} files analyzed...")
            
            file_suggestions = self.analyze_cpp_file(file_path)
            self.suggestions.extend(file_suggestions)
        
        print(f"✅ Analysis complete! Found {len(self.suggestions)} modernization opportunities")
        
        # Save results
        self.save_to_database()
        
        # Generate report
        report = self.generate_comprehensive_report()
        
        # Save report to file
        report_path = self.root_dir / "cpp20_modernization_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📊 Report saved to {report_path}")
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Modern C++20 Code Analysis Tool")
    parser.add_argument("--root", default=".", help="Root directory to analyze")
    parser.add_argument("--output", help="Output file for JSON report")
    parser.add_argument("--category", choices=['all', 'legacy', 'performance', 'features'], 
                       default='all', help="Analysis category")
    parser.add_argument("--impact", choices=['all', 'high', 'medium', 'low'], 
                       default='all', help="Filter by impact level")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    
    args = parser.parse_args()
    
    analyzer = ModernCppAnalyzer(args.root)
    report = analyzer.run_analysis()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n=== MODERN C++20 ANALYSIS SUMMARY ===")
    print(f"🎯 Modernization Score: {report['modernization_score']['overall']}/100")
    print(f"📋 Total Suggestions: {report['analysis_summary']['total_suggestions']}")
    print(f"📁 Files Analyzed: {report['analysis_summary']['files_analyzed']}")
    print(f"🔧 Auto-fixable: {report['analysis_summary']['auto_fixable_suggestions']}")
    
    print(f"\n📊 Impact Distribution:")
    for impact, count in report['impact_distribution'].items():
        print(f"   {impact.capitalize()}: {count}")
    
    print(f"\n🚀 Top Feature Opportunities:")
    for feature, stats in sorted(report['feature_adoption'].items(), 
                                key=lambda x: x[1]['adoption_rate']):
        if stats['adoption_rate'] < 50:  # Show underutilized features
            print(f"   {feature}: {stats['adoption_rate']:.1f}% adoption - {stats['benefits']}")
    
    if report['priority_recommendations']:
        print(f"\n💡 Priority Recommendations:")
        for rec in report['priority_recommendations']:
            print(f"   • {rec}")

if __name__ == "__main__":
    main()