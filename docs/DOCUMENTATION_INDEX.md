# 📚 FFXI Server Documentation Index

**Last Updated**: September 2024 - Repository Reorganized and Documentation Updated  
**Status**: 🔴 **PRIORITY 1: Job Completeness Initiative** - 10/22 Jobs Complete

Welcome to the comprehensive FFXI Server documentation. This directory contains all project documentation organized by category for easy navigation and reference.

## 🔴 PRIORITY 1: Job Completeness Initiative

**CURRENT STATUS**: ✅ **10/22 jobs at 100%** with 83.0% average completeness

### Priority 1 Documentation
- **[ROADMAP.md](../ROADMAP.md)** - ✅ Updated with current job status and graduated subjob system
- **[Job Completeness Current Status](reports/JOB_COMPLETENESS_CURRENT_STATUS.md)** - ✅ NEW: Complete current implementation status
- **[Job Completeness Plan](reports/JOB_COMPLETENESS_PLAN.md)** - ✅ Updated implementation plan  
- **[Job Completeness Analysis](reports/JOB_COMPLETENESS_ANALYSIS.md)** - ✅ Analysis results
- **[Repository Organization Status](REPOSITORY_ORGANIZATION_STATUS.md)** - ✅ NEW: Organization completion status

### Implementation Status
- **Current Completeness**: 83.0% average (10/22 jobs at 100%)
- **Graduated Subjob System**: Implemented in all 10 complete jobs
- **Next Priority**: Rune Fencer (52.5%), Bard (55.0%), Corsair (59.5%)
- **Integration**: Job Points (100%), Merits (100%) across all jobs

## 🗂️ Repository Organization (NEWLY RESTRUCTURED)

### Tools Structure (**COMPLETELY REORGANIZED - September 2024**)
The tools directory has been completely reorganized for better maintainability:

- **[Tools Overview](../tools/README.md)** - Complete reorganization guide
- **[Admin Tools](../tools/admin/README.md)** - Administration, monitoring, announcements
- **[Analysis Tools](../tools/analysis/README.md)** - Job analysis, security, validation
- **[Database Tools](../tools/database/README.md)** - Database management and optimization
- **[Development Tools](../tools/development/README.md)** - Code generation, documentation
- **[Launchers](../tools/launchers/README.md)** - Game launcher and client management
- **[Monitoring Tools](../tools/monitoring/README.md)** - Performance and system monitoring
- **[Streaming Tools](../tools/streaming/README.md)** - Asset and streaming management
- **[Testing Tools](../tools/testing/README.md)** - Testing frameworks and validation
- **[AI-GM Tools](../tools/ai-gm/README.md)** - AI-GM system tools (moved from root)

## Quick Links

- **[GM Account System](GM_ACCOUNT_SYSTEM.md)** - Complete GM privileges and command reference
- **[Development Roadmap](ROADMAP.md)** - Project development priorities and timeline
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to the project
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards and expectations

## Documentation Structure

### 📁 `/systems/` - Game System Documentation
Technical documentation for core FFXI game systems and mechanics:

- **[Job Level System Analysis](systems/comprehensive_job_level_system_analysis.md)** - Complete job, sub-job, merit points, and progression systems
- **[Progressive Subjob System](systems/progressive_subjob_system_documentation.md)** - Enhanced subjob scaling for endgame content
- **[Expansion Checklist](systems/expansion_checklist.md)** - Implementation status of all FFXI expansions
- **[GM Account System](GM_ACCOUNT_SYSTEM.md)** - GM privileges, commands, and administrative functions

### 📁 `/development/` - Development Resources
Resources for developers working on the server:

- **[Cross Platform Build](development/CROSS_PLATFORM_BUILD.md)** - Multi-platform compilation guide
- **[Function Indexing System](development/FUNCTION_INDEXING_SYSTEM.md)** - Code organization and indexing
- **[Interaction Framework](development/interaction-framework.md)** - Entity interaction system
- **[Python 3.12 Implementation](development/PYTHON_312_IMPLEMENTATION.md)** - Python modernization details
- **[Python 3.12 Upgrade Summary](development/PYTHON_312_UPGRADE_SUMMARY.md)** - Migration process and changes
- **[Python Migration Plan](development/PYTHON_MIGRATION_PLAN.md)** - Step-by-step migration strategy
- **[CoP Mission Status](development/CoP MissionStatus.md)** - Chains of Promathia implementation status
- **[Sol Refactoring](development/sol_refactoring.md)** - Lua binding improvements
- **[Zone Requirements](development/need_to_zone.md)** - Zone transition requirements

### 📁 `/operations/` - Server Operations
Documentation for server administration and operations:

- **[Database Workflow Improvements](operations/DATABASE_WORKFLOW_IMPROVEMENTS.md)** - Database optimization and maintenance
- **[Workflow Dependency Fixes](operations/workflow_dependency_fixes_log.md)** - CI/CD pipeline improvements  
- **[Workflow Fixes Log](operations/workflow_fixes_issue_log.md)** - Build system issue resolution
- **[Workflow Optimization](operations/workflow_optimization_summary.md)** - Performance improvements
- **[Build Update Issues](operations/comprehensive_build_update_issue_log.md)** - Build system troubleshooting

### 📁 `/guides/` - Setup and Usage Guides
Step-by-step guides for common tasks:

- **[Docker Installation Fix](docker-compose-installation-fix.md)** - Docker setup troubleshooting

### 📁 `/analysis/` - Technical Analysis
In-depth technical analysis and research documents:

- Performance analysis reports
- System architecture studies
- Implementation research

### 📁 `/summaries/` - Project Summaries
Overview documents and executive summaries:

- Feature implementation summaries
- Progress reports
- Release planning documents

### 📁 `/changelogs/` - Release History
Release notes and change history:

- Version changelogs
- Feature announcements
- Breaking change notifications

## Getting Started

1. **New Developers**: Start with [Development Guides](development/)
2. **Server Administrators**: Review [Operations Documentation](operations/)
3. **Game Masters**: Study the [GM Account System](GM_ACCOUNT_SYSTEM.md)
4. **Contributors**: Read [Contributing Guidelines](CONTRIBUTING.md)

## Documentation Maintenance

This documentation is actively maintained and updated with each release. For documentation issues or improvements:

1. Check existing documentation for accuracy
2. Submit pull requests for corrections or additions
3. Follow the project's documentation standards
4. Test all code examples and procedures before submission

## Recent Updates

- **GM Account System**: Complete documentation of GM privileges and 197+ commands
- **Systems Documentation**: Comprehensive job and subjob system analysis
- **Development Resources**: Python 3.12 migration and build system improvements
- **Operations Guides**: Workflow optimization and database maintenance procedures

For the most current information, always refer to the latest documentation in the main branch.