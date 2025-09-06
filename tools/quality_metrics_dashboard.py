#!/usr/bin/env python3
"""
Automated Quality Metrics Dashboard for FFXI-Server
Comprehensive code quality tracking and automated metrics collection.

This tool provides real-time code quality metrics, trend analysis, and automated
quality assurance monitoring for the FFXI-Server codebase with intelligent
reporting and actionable insights.
"""

import os
import sys
import time
import json
import sqlite3
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import argparse
import re
import hashlib

try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

@dataclass
class QualityMetric:
    """Quality metric data structure"""
    timestamp: float
    metric_name: str
    value: float
    unit: str
    category: str
    file_path: Optional[str] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    trend: Optional[str] = None  # improving, degrading, stable
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class CodeQualitySnapshot:
    """Complete code quality snapshot"""
    timestamp: float
    total_files: int
    total_lines: int
    total_functions: int
    complexity_score: float
    coverage_percentage: float
    technical_debt_hours: float
    maintainability_index: float
    duplication_percentage: float
    security_issues: int
    performance_issues: int
    bug_risk_score: float

class QualityMetricsDashboard:
    """Automated quality metrics collection and dashboard"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).absolute()
        self.config = self.load_config()
        self.metrics_history = deque(maxlen=self.config.get('max_history', 10000))
        self.db_path = self.root_dir / "quality_metrics.db"
        self.cache_dir = self.root_dir / ".quality_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.initialize_database()
        
        # Quality thresholds
        self.thresholds = {
            'complexity_score': {'warning': 10.0, 'critical': 20.0},
            'maintainability_index': {'warning': 20.0, 'critical': 10.0},
            'duplication_percentage': {'warning': 5.0, 'critical': 10.0},
            'coverage_percentage': {'warning': 80.0, 'critical': 60.0},
            'technical_debt_hours': {'warning': 24.0, 'critical': 48.0},
            'security_issues': {'warning': 5, 'critical': 10},
            'performance_issues': {'warning': 10, 'critical': 20},
            'bug_risk_score': {'warning': 7.0, 'critical': 8.5}
        }
        
        # File patterns to analyze
        self.source_patterns = {
            'cpp': ['**/*.cpp', '**/*.hpp', '**/*.h'],
            'lua': ['**/*.lua'],
            'python': ['**/*.py'],
            'sql': ['**/*.sql']
        }

    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_path = self.root_dir / "quality_metrics_config.json"
        default_config = {
            'collection_interval': 300,  # 5 minutes
            'retention_days': 90,
            'enable_trend_analysis': True,
            'enable_alerts': True,
            'web_port': 8081,
            'skip_directories': ['build', 'ext', '.git', 'node_modules'],
            'enable_detailed_analysis': True,
            'enable_security_scanning': True,
            'enable_performance_analysis': True
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config

    def initialize_database(self):
        """Initialize SQLite database for metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    category TEXT NOT NULL,
                    file_path TEXT,
                    threshold_warning REAL,
                    threshold_critical REAL,
                    trend TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quality_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    total_files INTEGER,
                    total_lines INTEGER,
                    total_functions INTEGER,
                    complexity_score REAL,
                    coverage_percentage REAL,
                    technical_debt_hours REAL,
                    maintainability_index REAL,
                    duplication_percentage REAL,
                    security_issues INTEGER,
                    performance_issues INTEGER,
                    bug_risk_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quality_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    threshold_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON quality_metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON quality_metrics(metric_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON quality_snapshots(timestamp)')

    def collect_file_metrics(self) -> List[QualityMetric]:
        """Collect file-level quality metrics"""
        metrics = []
        timestamp = time.time()
        
        skip_dirs = self.config.get('skip_directories', [])
        
        # Collect basic file statistics
        total_files = 0
        total_lines = 0
        
        for lang, patterns in self.source_patterns.items():
            lang_files = 0
            lang_lines = 0
            
            for pattern in patterns:
                for file_path in self.root_dir.glob(pattern):
                    if any(skip in str(file_path) for skip in skip_dirs):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                        
                        lang_files += 1
                        lang_lines += lines
                        
                    except Exception:
                        continue
            
            total_files += lang_files
            total_lines += lang_lines
            
            metrics.append(QualityMetric(
                timestamp=timestamp,
                metric_name=f'{lang}_file_count',
                value=lang_files,
                unit='files',
                category='size'
            ))
            
            metrics.append(QualityMetric(
                timestamp=timestamp,
                metric_name=f'{lang}_line_count',
                value=lang_lines,
                unit='lines',
                category='size'
            ))
        
        metrics.append(QualityMetric(
            timestamp=timestamp,
            metric_name='total_files',
            value=total_files,
            unit='files',
            category='size'
        ))
        
        metrics.append(QualityMetric(
            timestamp=timestamp,
            metric_name='total_lines',
            value=total_lines,
            unit='lines',
            category='size'
        ))
        
        return metrics

    def analyze_complexity(self) -> List[QualityMetric]:
        """Analyze code complexity metrics"""
        metrics = []
        timestamp = time.time()
        
        try:
            # Run our function indexer for complexity analysis
            indexer_path = self.root_dir / "tools" / "advanced_function_indexer.py"
            if indexer_path.exists():
                result = subprocess.run([
                    sys.executable, str(indexer_path), 
                    "--root", str(self.root_dir),
                    "--quiet"
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    # Load function analysis results
                    report_path = self.root_dir / "function_analysis_report.json"
                    if report_path.exists():
                        with open(report_path, 'r') as f:
                            function_data = json.load(f)
                        
                        # Extract complexity metrics
                        total_functions = function_data.get('total_functions', 0)
                        
                        metrics.append(QualityMetric(
                            timestamp=timestamp,
                            metric_name='total_functions',
                            value=total_functions,
                            unit='functions',
                            category='complexity'
                        ))
                        
                        # Calculate average complexity from most complex functions
                        most_complex = function_data.get('most_complex_functions', [])
                        if most_complex:
                            avg_complexity = sum(f['complexity'] for f in most_complex[:10]) / min(10, len(most_complex))
                            metrics.append(QualityMetric(
                                timestamp=timestamp,
                                metric_name='average_complexity',
                                value=avg_complexity,
                                unit='score',
                                category='complexity',
                                threshold_warning=self.thresholds['complexity_score']['warning'],
                                threshold_critical=self.thresholds['complexity_score']['critical']
                            ))
                        
        except Exception as e:
            print(f"Error analyzing complexity: {e}")
        
        return metrics

    def analyze_duplication(self) -> List[QualityMetric]:
        """Analyze code duplication"""
        metrics = []
        timestamp = time.time()
        
        # Simple duplication detection using file hashing
        file_hashes = defaultdict(list)
        duplicate_lines = 0
        total_analyzed_lines = 0
        
        try:
            for pattern in ['**/*.cpp', '**/*.hpp', '**/*.h']:
                for file_path in self.root_dir.glob(pattern):
                    if any(skip in str(file_path) for skip in self.config.get('skip_directories', [])):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        # Hash chunks of 5 lines for duplication detection
                        for i in range(len(lines) - 4):
                            chunk = ''.join(lines[i:i+5]).strip()
                            if chunk and len(chunk) > 50:  # Ignore small chunks
                                chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
                                file_hashes[chunk_hash].append((file_path, i+1))
                                total_analyzed_lines += 1
                                
                    except Exception:
                        continue
            
            # Count duplicated lines
            for chunk_hash, locations in file_hashes.items():
                if len(locations) > 1:
                    duplicate_lines += len(locations) * 5  # Each duplicate is 5 lines
            
            duplication_percentage = (duplicate_lines / max(total_analyzed_lines * 5, 1)) * 100
            
            metrics.append(QualityMetric(
                timestamp=timestamp,
                metric_name='duplication_percentage',
                value=duplication_percentage,
                unit='percent',
                category='duplication',
                threshold_warning=self.thresholds['duplication_percentage']['warning'],
                threshold_critical=self.thresholds['duplication_percentage']['critical']
            ))
            
            metrics.append(QualityMetric(
                timestamp=timestamp,
                metric_name='duplicate_lines',
                value=duplicate_lines,
                unit='lines',
                category='duplication'
            ))
            
        except Exception as e:
            print(f"Error analyzing duplication: {e}")
        
        return metrics

    def analyze_security_issues(self) -> List[QualityMetric]:
        """Analyze security-related issues"""
        metrics = []
        timestamp = time.time()
        
        if not self.config.get('enable_security_scanning', True):
            return metrics
        
        try:
            # Run our vulnerability scanner
            scanner_path = self.root_dir / "tools" / "vulnerability_scanner.py"
            if scanner_path.exists():
                result = subprocess.run([
                    sys.executable, str(scanner_path)
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # Parse scanner output for issue count
                    security_issues = 0
                    
                    # Count security-related patterns in output
                    security_patterns = [
                        'buffer overflow', 'sql injection', 'xss', 'csrf',
                        'insecure', 'vulnerability', 'security'
                    ]
                    
                    for line in result.stdout.lower().split('\n'):
                        if any(pattern in line for pattern in security_patterns):
                            security_issues += 1
                    
                    metrics.append(QualityMetric(
                        timestamp=timestamp,
                        metric_name='security_issues',
                        value=security_issues,
                        unit='issues',
                        category='security',
                        threshold_warning=self.thresholds['security_issues']['warning'],
                        threshold_critical=self.thresholds['security_issues']['critical']
                    ))
                    
        except Exception as e:
            print(f"Error analyzing security issues: {e}")
        
        return metrics

    def analyze_performance_issues(self) -> List[QualityMetric]:
        """Analyze performance-related issues"""
        metrics = []
        timestamp = time.time()
        
        if not self.config.get('enable_performance_analysis', True):
            return metrics
        
        performance_issues = 0
        
        try:
            # Look for common performance anti-patterns
            performance_patterns = [
                r'std::string.*\+.*std::string',  # String concatenation
                r'\.size\(\)\s*==\s*0',  # Use empty() instead
                r'new\s+\w+\[',  # Raw array allocation
                r'malloc\s*\(',  # C-style allocation
                r'for.*\.begin\(\).*\.end\(\)'  # Manual iteration
            ]
            
            for pattern in ['**/*.cpp', '**/*.hpp']:
                for file_path in self.root_dir.glob(pattern):
                    if any(skip in str(file_path) for skip in self.config.get('skip_directories', [])):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        for perf_pattern in performance_patterns:
                            matches = re.findall(perf_pattern, content)
                            performance_issues += len(matches)
                            
                    except Exception:
                        continue
            
            metrics.append(QualityMetric(
                timestamp=timestamp,
                metric_name='performance_issues',
                value=performance_issues,
                unit='issues',
                category='performance',
                threshold_warning=self.thresholds['performance_issues']['warning'],
                threshold_critical=self.thresholds['performance_issues']['critical']
            ))
            
        except Exception as e:
            print(f"Error analyzing performance issues: {e}")
        
        return metrics

    def calculate_maintainability_index(self, complexity: float, lines: int, functions: int) -> float:
        """Calculate maintainability index (0-100, higher is better)"""
        if functions == 0 or lines == 0:
            return 100.0
        
        # Simplified maintainability index calculation
        # Based on Halstead volume, cyclomatic complexity, and lines of code
        
        # Estimate Halstead volume (simplified)
        volume = lines * 4.7  # Rough approximation
        
        # Calculate maintainability index
        mi = 171 - 5.2 * complexity - 0.23 * (volume / functions) - 16.2 * complexity
        
        # Normalize to 0-100 scale
        mi = max(0, min(100, mi))
        
        return mi

    def calculate_technical_debt(self, complexity: float, duplication: float, issues: int) -> float:
        """Calculate technical debt in hours"""
        # Simplified technical debt calculation
        debt_hours = 0.0
        
        # Complexity debt (high complexity functions need refactoring)
        if complexity > 10:
            debt_hours += (complexity - 10) * 2  # 2 hours per excess complexity point
        
        # Duplication debt
        debt_hours += duplication * 0.5  # 30 minutes per percentage point of duplication
        
        # Issue debt
        debt_hours += issues * 0.25  # 15 minutes per issue
        
        return debt_hours

    def calculate_bug_risk_score(self, complexity: float, security_issues: int, performance_issues: int) -> float:
        """Calculate bug risk score (0-10, lower is better)"""
        risk_score = 0.0
        
        # Complexity contributes to bug risk
        risk_score += min(5.0, complexity / 4.0)
        
        # Security issues are high risk
        risk_score += min(3.0, security_issues / 3.0)
        
        # Performance issues contribute to stability risk
        risk_score += min(2.0, performance_issues / 10.0)
        
        return min(10.0, risk_score)

    def generate_quality_snapshot(self) -> CodeQualitySnapshot:
        """Generate comprehensive quality snapshot"""
        timestamp = time.time()
        
        # Collect current metrics
        all_metrics = []
        all_metrics.extend(self.collect_file_metrics())
        all_metrics.extend(self.analyze_complexity())
        all_metrics.extend(self.analyze_duplication())
        all_metrics.extend(self.analyze_security_issues())
        all_metrics.extend(self.analyze_performance_issues())
        
        # Extract values for snapshot
        metric_values = {m.metric_name: m.value for m in all_metrics}
        
        total_files = metric_values.get('total_files', 0)
        total_lines = metric_values.get('total_lines', 0)
        total_functions = metric_values.get('total_functions', 0)
        complexity_score = metric_values.get('average_complexity', 5.0)
        duplication_percentage = metric_values.get('duplication_percentage', 0.0)
        security_issues = metric_values.get('security_issues', 0)
        performance_issues = metric_values.get('performance_issues', 0)
        
        # Calculate derived metrics
        maintainability_index = self.calculate_maintainability_index(
            complexity_score, total_lines, total_functions
        )
        
        technical_debt_hours = self.calculate_technical_debt(
            complexity_score, duplication_percentage, security_issues + performance_issues
        )
        
        bug_risk_score = self.calculate_bug_risk_score(
            complexity_score, security_issues, performance_issues
        )
        
        # Simulate coverage (would need actual test coverage tool)
        coverage_percentage = 75.0  # Placeholder
        
        snapshot = CodeQualitySnapshot(
            timestamp=timestamp,
            total_files=int(total_files),
            total_lines=int(total_lines),
            total_functions=int(total_functions),
            complexity_score=complexity_score,
            coverage_percentage=coverage_percentage,
            technical_debt_hours=technical_debt_hours,
            maintainability_index=maintainability_index,
            duplication_percentage=duplication_percentage,
            security_issues=int(security_issues),
            performance_issues=int(performance_issues),
            bug_risk_score=bug_risk_score
        )
        
        # Add derived metrics to metrics list
        derived_metrics = [
            QualityMetric(
                timestamp=timestamp,
                metric_name='maintainability_index',
                value=maintainability_index,
                unit='score',
                category='quality',
                threshold_warning=self.thresholds['maintainability_index']['warning'],
                threshold_critical=self.thresholds['maintainability_index']['critical']
            ),
            QualityMetric(
                timestamp=timestamp,
                metric_name='technical_debt_hours',
                value=technical_debt_hours,
                unit='hours',
                category='debt',
                threshold_warning=self.thresholds['technical_debt_hours']['warning'],
                threshold_critical=self.thresholds['technical_debt_hours']['critical']
            ),
            QualityMetric(
                timestamp=timestamp,
                metric_name='bug_risk_score',
                value=bug_risk_score,
                unit='score',
                category='risk',
                threshold_warning=self.thresholds['bug_risk_score']['warning'],
                threshold_critical=self.thresholds['bug_risk_score']['critical']
            )
        ]
        
        all_metrics.extend(derived_metrics)
        
        # Store metrics
        self.metrics_history.extend(all_metrics)
        
        return snapshot

    def check_quality_thresholds(self, snapshot: CodeQualitySnapshot) -> List[Dict[str, Any]]:
        """Check quality thresholds and generate alerts"""
        alerts = []
        
        # Define checks
        checks = [
            ('complexity_score', snapshot.complexity_score, 'Cyclomatic Complexity'),
            ('maintainability_index', snapshot.maintainability_index, 'Maintainability Index'),
            ('duplication_percentage', snapshot.duplication_percentage, 'Code Duplication'),
            ('technical_debt_hours', snapshot.technical_debt_hours, 'Technical Debt'),
            ('security_issues', snapshot.security_issues, 'Security Issues'),
            ('performance_issues', snapshot.performance_issues, 'Performance Issues'),
            ('bug_risk_score', snapshot.bug_risk_score, 'Bug Risk Score')
        ]
        
        for metric_name, value, display_name in checks:
            if metric_name in self.thresholds:
                thresholds = self.thresholds[metric_name]
                
                # Check critical threshold
                if 'critical' in thresholds:
                    critical = thresholds['critical']
                    if (metric_name == 'maintainability_index' and value < critical) or \
                       (metric_name != 'maintainability_index' and value > critical):
                        alerts.append({
                            'timestamp': snapshot.timestamp,
                            'metric_name': metric_name,
                            'value': value,
                            'threshold_type': 'critical',
                            'severity': 'critical',
                            'message': f"{display_name} is {value:.1f}, exceeding critical threshold of {critical}"
                        })
                        continue
                
                # Check warning threshold
                if 'warning' in thresholds:
                    warning = thresholds['warning']
                    if (metric_name == 'maintainability_index' and value < warning) or \
                       (metric_name != 'maintainability_index' and value > warning):
                        alerts.append({
                            'timestamp': snapshot.timestamp,
                            'metric_name': metric_name,
                            'value': value,
                            'threshold_type': 'warning',
                            'severity': 'warning',
                            'message': f"{display_name} is {value:.1f}, exceeding warning threshold of {warning}"
                        })
        
        return alerts

    def save_snapshot_to_db(self, snapshot: CodeQualitySnapshot):
        """Save quality snapshot to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO quality_snapshots (
                        timestamp, total_files, total_lines, total_functions,
                        complexity_score, coverage_percentage, technical_debt_hours,
                        maintainability_index, duplication_percentage, security_issues,
                        performance_issues, bug_risk_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    snapshot.timestamp,
                    snapshot.total_files,
                    snapshot.total_lines,
                    snapshot.total_functions,
                    snapshot.complexity_score,
                    snapshot.coverage_percentage,
                    snapshot.technical_debt_hours,
                    snapshot.maintainability_index,
                    snapshot.duplication_percentage,
                    snapshot.security_issues,
                    snapshot.performance_issues,
                    snapshot.bug_risk_score
                ))
                
                # Save individual metrics
                for metric in self.metrics_history:
                    conn.execute('''
                        INSERT INTO quality_metrics (
                            timestamp, metric_name, value, unit, category,
                            file_path, threshold_warning, threshold_critical,
                            trend, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        metric.timestamp,
                        metric.metric_name,
                        metric.value,
                        metric.unit,
                        metric.category,
                        metric.file_path,
                        metric.threshold_warning,
                        metric.threshold_critical,
                        metric.trend,
                        json.dumps(metric.metadata) if metric.metadata else None
                    ))
                
        except Exception as e:
            print(f"Error saving snapshot to database: {e}")

    def get_quality_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get quality trends over time"""
        cutoff_time = time.time() - (hours * 3600)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT timestamp, complexity_score, maintainability_index,
                           technical_debt_hours, bug_risk_score
                    FROM quality_snapshots 
                    WHERE timestamp > ?
                    ORDER BY timestamp
                ''', (cutoff_time,))
                
                snapshots = cursor.fetchall()
                
                if len(snapshots) < 2:
                    return {'error': 'Insufficient data for trend analysis'}
                
                # Calculate trends
                first = snapshots[0]
                last = snapshots[-1]
                
                trends = {
                    'complexity_trend': 'improving' if last[1] < first[1] else 'degrading' if last[1] > first[1] else 'stable',
                    'maintainability_trend': 'improving' if last[2] > first[2] else 'degrading' if last[2] < first[2] else 'stable',
                    'debt_trend': 'improving' if last[3] < first[3] else 'degrading' if last[3] > first[3] else 'stable',
                    'risk_trend': 'improving' if last[4] < first[4] else 'degrading' if last[4] > first[4] else 'stable'
                }
                
                return {
                    'trends': trends,
                    'data_points': len(snapshots),
                    'time_range_hours': hours
                }
                
        except Exception as e:
            return {'error': str(e)}

    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        snapshot = self.generate_quality_snapshot()
        alerts = self.check_quality_thresholds(snapshot)
        trends = self.get_quality_trends(24)
        
        # Save to database
        self.save_snapshot_to_db(snapshot)
        
        # Calculate quality score (0-100, higher is better)
        quality_score = (
            min(100, snapshot.maintainability_index) * 0.3 +
            max(0, 100 - snapshot.complexity_score * 5) * 0.2 +
            max(0, 100 - snapshot.duplication_percentage * 10) * 0.2 +
            max(0, 100 - snapshot.bug_risk_score * 10) * 0.2 +
            max(0, 100 - snapshot.technical_debt_hours / 48 * 100) * 0.1
        )
        
        return {
            'timestamp': snapshot.timestamp,
            'quality_score': round(quality_score, 1),
            'snapshot': asdict(snapshot),
            'alerts': alerts,
            'trends': trends,
            'recommendations': self.generate_recommendations(snapshot, alerts)
        }

    def generate_recommendations(self, snapshot: CodeQualitySnapshot, alerts: List[Dict[str, Any]]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        # Critical issues first
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        if critical_alerts:
            recommendations.append(f"⚠️ Address {len(critical_alerts)} critical quality issues immediately")
        
        # Complexity recommendations
        if snapshot.complexity_score > 15:
            recommendations.append("🔧 Refactor high-complexity functions to improve maintainability")
        
        # Technical debt
        if snapshot.technical_debt_hours > 24:
            recommendations.append(f"💰 Address technical debt ({snapshot.technical_debt_hours:.1f} hours estimated)")
        
        # Security issues
        if snapshot.security_issues > 0:
            recommendations.append(f"🔒 Fix {snapshot.security_issues} security issues")
        
        # Performance issues
        if snapshot.performance_issues > 10:
            recommendations.append(f"🚀 Optimize {snapshot.performance_issues} performance anti-patterns")
        
        # Duplication
        if snapshot.duplication_percentage > 5:
            recommendations.append(f"📋 Reduce code duplication ({snapshot.duplication_percentage:.1f}%)")
        
        # Maintainability
        if snapshot.maintainability_index < 50:
            recommendations.append("🔨 Improve code maintainability through refactoring")
        
        return recommendations

    def start_web_dashboard(self):
        """Start web dashboard"""
        if not FLASK_AVAILABLE:
            print("Flask not available. Install with: pip install flask")
            return
        
        app = Flask(__name__)
        
        @app.route('/')
        def dashboard():
            return render_template_string(self.get_dashboard_html())
        
        @app.route('/api/quality-report')
        def api_quality_report():
            return jsonify(self.generate_quality_report())
        
        @app.route('/api/trends/<int:hours>')
        def api_trends(hours):
            return jsonify(self.get_quality_trends(hours))
        
        print(f"Starting quality dashboard on http://localhost:{self.config.get('web_port', 8081)}")
        app.run(host='0.0.0.0', port=self.config.get('web_port', 8081), debug=False)

    def get_dashboard_html(self) -> str:
        """Get HTML for quality dashboard"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>FFXI Server Quality Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .metric-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #eee; }
        .metric-row:last-child { border-bottom: none; }
        .metric-label { font-weight: 500; color: #555; }
        .metric-value { font-size: 1.4em; font-weight: bold; }
        .quality-excellent { color: #28a745; }
        .quality-good { color: #17a2b8; }
        .quality-warning { color: #ffc107; }
        .quality-danger { color: #dc3545; }
        .score-circle { width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: white; margin: 0 auto; }
        .alert-item { padding: 12px; margin: 8px 0; border-radius: 8px; }
        .alert-critical { background: #f8d7da; border-left: 4px solid #dc3545; }
        .alert-warning { background: #fff3cd; border-left: 4px solid #ffc107; }
        .recommendation { background: #e7f3ff; border-left: 4px solid #007bff; padding: 12px; margin: 8px 0; border-radius: 4px; }
        .trend-up { color: #28a745; }
        .trend-down { color: #dc3545; }
        .trend-stable { color: #6c757d; }
    </style>
    <script>
        function updateDashboard() {
            fetch('/api/quality-report')
                .then(response => response.json())
                .then(data => {
                    // Update quality score
                    const score = data.quality_score;
                    const scoreElement = document.getElementById('quality-score');
                    scoreElement.textContent = score.toFixed(1);
                    
                    // Color code the score
                    const scoreCircle = document.getElementById('score-circle');
                    if (score >= 80) {
                        scoreCircle.className = 'score-circle quality-excellent';
                        scoreCircle.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
                    } else if (score >= 60) {
                        scoreCircle.className = 'score-circle quality-good';
                        scoreCircle.style.background = 'linear-gradient(135deg, #17a2b8, #6f42c1)';
                    } else if (score >= 40) {
                        scoreCircle.className = 'score-circle quality-warning';
                        scoreCircle.style.background = 'linear-gradient(135deg, #ffc107, #fd7e14)';
                    } else {
                        scoreCircle.className = 'score-circle quality-danger';
                        scoreCircle.style.background = 'linear-gradient(135deg, #dc3545, #e83e8c)';
                    }
                    
                    // Update metrics
                    const snapshot = data.snapshot;
                    document.getElementById('total-files').textContent = snapshot.total_files;
                    document.getElementById('total-lines').textContent = snapshot.total_lines.toLocaleString();
                    document.getElementById('complexity').textContent = snapshot.complexity_score.toFixed(1);
                    document.getElementById('maintainability').textContent = snapshot.maintainability_index.toFixed(1);
                    document.getElementById('technical-debt').textContent = snapshot.technical_debt_hours.toFixed(1) + 'h';
                    document.getElementById('security-issues').textContent = snapshot.security_issues;
                    document.getElementById('duplication').textContent = snapshot.duplication_percentage.toFixed(1) + '%';
                    
                    // Update alerts
                    const alertsContainer = document.getElementById('alerts-list');
                    alertsContainer.innerHTML = '';
                    data.alerts.forEach(alert => {
                        const alertDiv = document.createElement('div');
                        alertDiv.className = `alert-item alert-${alert.severity}`;
                        alertDiv.textContent = alert.message;
                        alertsContainer.appendChild(alertDiv);
                    });
                    
                    // Update recommendations
                    const recContainer = document.getElementById('recommendations-list');
                    recContainer.innerHTML = '';
                    data.recommendations.forEach(rec => {
                        const recDiv = document.createElement('div');
                        recDiv.className = 'recommendation';
                        recDiv.textContent = rec;
                        recContainer.appendChild(recDiv);
                    });
                    
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error updating dashboard:', error);
                });
        }
        
        setInterval(updateDashboard, 30000); // Update every 30 seconds
        window.onload = updateDashboard;
    </script>
</head>
<body>
    <div class="header">
        <h1>📊 FFXI Server Quality Dashboard</h1>
        <p>Comprehensive code quality monitoring and metrics tracking</p>
        <p>Last Update: <span id="last-update">Loading...</span></p>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3 style="text-align: center; margin-bottom: 20px;">Overall Quality Score</h3>
            <div id="score-circle" class="score-circle">
                <span id="quality-score">--</span>
            </div>
            <p style="text-align: center; margin-top: 15px; color: #666;">
                Score based on maintainability, complexity, and technical debt
            </p>
        </div>
        
        <div class="card">
            <h3>Code Metrics</h3>
            <div class="metric-row">
                <span class="metric-label">Total Files</span>
                <span class="metric-value" id="total-files">--</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Lines of Code</span>
                <span class="metric-value" id="total-lines">--</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Avg Complexity</span>
                <span class="metric-value" id="complexity">--</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Maintainability</span>
                <span class="metric-value" id="maintainability">--</span>
            </div>
        </div>
        
        <div class="card">
            <h3>Quality Issues</h3>
            <div class="metric-row">
                <span class="metric-label">Technical Debt</span>
                <span class="metric-value" id="technical-debt">--</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Security Issues</span>
                <span class="metric-value" id="security-issues">--</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Code Duplication</span>
                <span class="metric-value" id="duplication">--</span>
            </div>
        </div>
        
        <div class="card">
            <h3>Active Alerts</h3>
            <div id="alerts-list">
                <p style="color: #666; text-align: center;">Loading alerts...</p>
            </div>
        </div>
        
        <div class="card">
            <h3>Recommendations</h3>
            <div id="recommendations-list">
                <p style="color: #666; text-align: center;">Loading recommendations...</p>
            </div>
        </div>
        
        <div class="card">
            <h3>Quick Actions</h3>
            <button onclick="location.reload()" style="width: 100%; padding: 12px; margin: 8px 0; border: none; background: #007bff; color: white; border-radius: 6px; cursor: pointer;">🔄 Refresh Dashboard</button>
            <button onclick="window.open('/api/quality-report', '_blank')" style="width: 100%; padding: 12px; margin: 8px 0; border: none; background: #28a745; color: white; border-radius: 6px; cursor: pointer;">📈 View Raw Data</button>
            <button onclick="window.open('/api/trends/168', '_blank')" style="width: 100%; padding: 12px; margin: 8px 0; border: none; background: #17a2b8; color: white; border-radius: 6px; cursor: pointer;">📊 Weekly Trends</button>
        </div>
    </div>
</body>
</html>
        '''

def main():
    parser = argparse.ArgumentParser(description="Automated Quality Metrics Dashboard")
    parser.add_argument("--root", default=".", help="Root directory to analyze")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--report", action="store_true", help="Generate quality report")
    parser.add_argument("--web", action="store_true", help="Start web dashboard")
    parser.add_argument("--port", type=int, default=8081, help="Web dashboard port")
    
    args = parser.parse_args()
    
    dashboard = QualityMetricsDashboard(args.root)
    
    if args.port:
        dashboard.config['web_port'] = args.port
    
    if args.report:
        report = dashboard.generate_quality_report()
        
        print("\n=== QUALITY METRICS REPORT ===")
        print(f"🎯 Overall Quality Score: {report['quality_score']}/100")
        print(f"📁 Files: {report['snapshot']['total_files']}")
        print(f"📏 Lines: {report['snapshot']['total_lines']:,}")
        print(f"🔧 Avg Complexity: {report['snapshot']['complexity_score']:.1f}")
        print(f"🏗️ Maintainability: {report['snapshot']['maintainability_index']:.1f}")
        print(f"💰 Technical Debt: {report['snapshot']['technical_debt_hours']:.1f}h")
        
        if report['alerts']:
            print(f"\n⚠️ Active Alerts ({len(report['alerts'])}):")
            for alert in report['alerts'][:5]:
                print(f"   • {alert['message']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        # Save report
        report_path = Path(args.root) / "quality_metrics_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📊 Detailed report saved to {report_path}")
    
    elif args.web:
        dashboard.start_web_dashboard()
    
    else:
        print("Use --report for quality analysis or --web for dashboard")

if __name__ == "__main__":
    main()