# Workflow Issues Report
Generated: /home/runner/work/FFXI-Server/FFXI-Server

## Summary
- Total workflows analyzed: 13
- Workflows with issues: 13
- Total issues found: 39

## Issues by Type
- missing_system_deps: 3
- missing_timeout: 36

## Detailed Findings
### build.yml
- 🔵 **missing_timeout** (low): Job 'Comprehensive_Python312_Build_Test' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Comprehensive_Python312_Build_Test job
- 🔵 **missing_timeout** (low): Job 'Sanity_Checks' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Sanity_Checks job
- 🔵 **missing_timeout** (low): Job 'Linux_LuaLanguageServer' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Linux_LuaLanguageServer job
- 🔵 **missing_timeout** (low): Job 'Linux_Clang18_64bit' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Linux_Clang18_64bit job
- 🔵 **missing_timeout** (low): Job 'Linux_ClangTidy18_64bit' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Linux_ClangTidy18_64bit job
- 🔵 **missing_timeout** (low): Job 'Linux_GCC14_64bit' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Linux_GCC14_64bit job
- 🔵 **missing_timeout** (low): Job 'Database_Performance_Tests' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Database_Performance_Tests job
- 🔵 **missing_timeout** (low): Job 'Full_Startup_Checks_Linux' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Full_Startup_Checks_Linux job
- 🔵 **missing_timeout** (low): Job 'MultiInstance_Startup_Checks_Linux' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to MultiInstance_Startup_Checks_Linux job

### changelog.yml
- 🔵 **missing_timeout** (low): Job 'Publish_Changelog' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Publish_Changelog job

### codeql.yml
- 🔵 **missing_timeout** (low): Job 'analyze' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to analyze job

### codeql_analysis.yml
- 🔵 **missing_timeout** (low): Job 'analyze' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to analyze job

### database_ci_integration.yml
- 🔵 **missing_timeout** (low): Job 'Database_Impact_Analysis' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Database_Impact_Analysis job
- 🔵 **missing_timeout** (low): Job 'Database_Unit_Tests' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Database_Unit_Tests job
- 🔵 **missing_timeout** (low): Job 'Database_Performance_Validation' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Database_Performance_Validation job
- 🔵 **missing_timeout** (low): Job 'Database_Integration_Tests' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Database_Integration_Tests job
- 🔵 **missing_timeout** (low): Job 'Database_Security_Scan' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Database_Security_Scan job

### database_performance.yml
- 🔵 **missing_timeout** (low): Job 'Database_Health_Check' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Database_Health_Check job

### discussion_keyword_comment.yml
- 🔵 **missing_timeout** (low): Job 'comment' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to comment job

### docker-build.yml
- 🔵 **missing_timeout** (low): Job 'docker-build' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to docker-build job
- 🔵 **missing_timeout** (low): Job 'docker-test' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to docker-test job
- 🔵 **missing_timeout** (low): Job 'docker-security-scan' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to docker-security-scan job
- 🔵 **missing_timeout** (low): Job 'docker-integration-test' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to docker-integration-test job

### launcher-build-test.yml
- 🔵 **missing_timeout** (low): Job 'Launcher_Build_Test' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Launcher_Build_Test job
- 🔵 **missing_timeout** (low): Job 'Windows_Launcher_Build_Test' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Windows_Launcher_Build_Test job
- 🔵 **missing_timeout** (low): Job 'macOS_Launcher_Build_Test' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to macOS_Launcher_Build_Test job

### macos-build.yml
- 🟠 **missing_system_deps** (medium): Job 'MacOS_64bit' builds code but may be missing system dependency installation
- 🔵 **missing_timeout** (low): Job 'MacOS_64bit' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to MacOS_64bit job
- 🔵 **missing_timeout** (low): Job 'MacOS_Launcher_Build' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to MacOS_Launcher_Build job
- 🔵 **missing_timeout** (low): Job 'MacOS_Integration_Tests' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to MacOS_Integration_Tests job

### windows-build.yml
- 🟠 **missing_system_deps** (medium): Job 'Windows_64bit_Debug' builds code but may be missing system dependency installation
- 🟠 **missing_system_deps** (medium): Job 'Windows_64bit_Release_Tracy_Modules' builds code but may be missing system dependency installation
- 🔵 **missing_timeout** (low): Job 'Windows_64bit_Debug' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Windows_64bit_Debug job
- 🔵 **missing_timeout** (low): Job 'Windows_64bit_Release_Tracy_Modules' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Windows_64bit_Release_Tracy_Modules job
- 🔵 **missing_timeout** (low): Job 'Windows_Launcher_Build' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Windows_Launcher_Build job
- 🔵 **missing_timeout** (low): Job 'Full_Startup_Checks_Windows' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Full_Startup_Checks_Windows job
- 🔵 **missing_timeout** (low): Job 'Full_Startup_Checks_Windows_Tracy_Modules' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Full_Startup_Checks_Windows_Tracy_Modules job

### pr_checkboxes_comment.yml
- 🔵 **missing_timeout** (low): Job 'Check_Checkboxes' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Check_Checkboxes job

### pr_labels.yml
- 🔵 **missing_timeout** (low): Job 'Check_Blocking_Labels' doesn't have timeout configured
  - 🔧 Fix: Add timeout-minutes to Check_Blocking_Labels job

## Recommendations
1. Run with `--fix` flag to apply automatic fixes
2. Review all critical and high severity issues first
3. Test workflow changes in a feature branch
4. Consider implementing additional CI optimizations