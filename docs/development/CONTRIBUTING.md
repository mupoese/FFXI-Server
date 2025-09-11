# Contributing to FFXI-Server

## Development Setup
1. Clone the repository
2. Install dependencies using tools in `/tools/`
3. Run initial setup scripts
4. Follow coding standards outlined below

## Code Quality Standards
- **C++**: Follow project .clang-format configuration
- **Lua**: Use consistent indentation and naming
- **Python**: Follow PEP 8 standards
- **SQL**: Use consistent formatting

## Testing Requirements
- All new features must include tests
- Ensure existing tests continue to pass
- Run full test suite before submitting PRs

## Workflow Guidelines
- Use descriptive commit messages (max 72 characters)
- Create feature branches from latest base
- Submit PRs with comprehensive descriptions
- Ensure CI/CD pipelines pass

## Security Requirements
- Follow security scanning guidelines
- No hardcoded credentials or secrets
- Use secure coding practices
- Report security issues responsibly
