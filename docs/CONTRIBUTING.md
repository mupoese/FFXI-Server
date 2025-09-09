# Contributing Guide

## Table of Contents

- [Contributing Guide](#contributing-guide)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [License](#license)
  - [General Guidelines](#general-guidelines)
  - [Technical Guidelines](#technical-guidelines)
  - [Workflow Guide](#workflow-guide)
  - [Issue Report Contributions](#issue-report-contributions)
  - [Pull Request Contributions](#pull-request-contributions)

## Code of Conduct

- Please read and understand our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

- We operate under [GNU General Public License v3.0](LICENSE).
- We do not accept contributions that use other more restrictive licenses (such as AGPLv3).

## General Guidelines

- By contributing to LandSandBoat, either through issues, pull requests, or discussions, you are expected to abide by the rules laid out here in this Contributing Guide.
- We do not support out-of-date clients or client modification.
- We do not support piracy of any kind. We encourage you to maintain an active retail subscription and support the game.

## Technical Guidelines

- For more specific guides on how to contribute using Git, GitHub, C++, Lua, SQL, Python, other technical changes, and how to style your code, etc. please see the [Development Guide](development/) and other development documentation in this repository.

### 🌐 Web Interface and Monitoring

This repository now includes a comprehensive web administration interface with integrated monitoring:

- **Homepage**: `http://localhost:8000` - Beautiful responsive landing page with real-time server status
- **Admin Dashboard**: `http://localhost:8000/admin.html` - 8-tab comprehensive administration interface
- **Monitoring Stack**: Prometheus + Grafana + Node Exporter integration with Docker profiles

**Quick Start:**
```bash
# Start with web interface and monitoring
COMPOSE_PROFILES=monitoring docker-compose up -d

# Access interfaces
open http://localhost:8000              # Homepage with server status
open http://localhost:8000/admin.html   # Admin dashboard
open http://localhost:3000              # Grafana dashboards
```

### Development Environment Setup

**Docker Development Environment:**
```bash
# Clone and setup
git clone https://github.com/mupoese/FFXI-Server.git
cd FFXI-Server
cp .env.example .env

# Start development environment with full monitoring
COMPOSE_PROFILES=admin,redis,monitoring docker-compose up -d

# Development tools
python3 tools/dev_automation.py all
tools/enhanced_ci_pipeline.sh all
```

## Workflow Guide

- It is **always** better to ask questions and ask for advice instead of investing a lot of time into work that we may end up asking you to rewrite or split up into smaller contributions.
- Cite your sources. This can be comments in your code or your commit messages. Pull Request descriptions and comments will get lost over time.
- If you're commiting work on someone else's behalf, use git's `--author` argument or GitHub's `Co-Authored-By:` feature so they get the credit they deserve.
- Make your commit messages meaningful, or amend/rebase once you're ready to push.
- If you want to report or resolve an exploitable issue please try and get in contact with staff privately. Staff are pretty easy to find across different Discords or by the emails their commits are attributed with. This software is used by many live servers with active players, and we want to distribute fixes for exploits in a responsible and private fashion before they're published to the public.

## Issue Report Contributions

- Unimplemented feature requests must be _retail behavior_, and adequately cover everything about that feature which is missing.
- Fill out the templated checkboxes that are preloaded in the issue body. These allow us to diagnose your issue as efficiently as possible, and confirm that you've searched for duplicate issues or recent fixes.

## Pull Request Contributions

All contributions must be done through pull requests to this repository. We don't take fixes from Discord to apply ourselves. If you need help with making a pull request, there is a GitHub guide on how to do so.

We prefer submitting early and often, over monolithic and once. If you're implementing a complex feature, please try to submit PRs as you get each smaller functional aspect working (use your best judgment on what counts as a useful PR). This way we can help make sure you're on the right track before you sink a lot of time into implementations we might want done in a different way.

Please try to leave your PR alone after submission, unless it's to fix bugs you've noticed, or if we've requested changes. If you're still pushing commits after opening the PR, it makes it hard for reviewers to know when you're "finished" and if it's "safe" to begin their reviews. If you do want to push early for reviews of your in-progress work, you can open your PR as a "draft".

After a pull request is made, if a staff member leaves feedback for you to change, you must either fix or address it for your pull request to be merged.

If you do not fill the checkboxes confirming that you've read the supporting documentation, and that you've tested your code - your PR will not be reviewed.
