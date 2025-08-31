# Docker Compose Installation Fix

## Issue
The GitHub Actions workflow failed with the error:
```
docker-compose: command not found
ERROR: docker-compose.yml syntax validation failed!
```

## Root Cause
GitHub Actions runners use Docker v2 which includes Docker Compose v2 as a plugin (`docker compose`), but the legacy standalone `docker-compose` binary is not installed by default.

## Solution Applied
Added installation steps to install the standalone `docker-compose` binary in all workflow jobs that use it:

```yaml
- name: Install docker-compose
  run: |
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    docker-compose version
```

## Jobs Modified
- `docker-build`: Added installation before docker-compose config validation
- `docker-test`: Added installation before container testing
- `docker-integration-test`: Added installation before integration tests
- `docker-security-scan`: No changes needed (doesn't use docker-compose)

## Future Considerations
This is a temporary fix to maintain backward compatibility. The repository should eventually migrate from `docker-compose` (v1 syntax) to `docker compose` (v2 syntax) for better future-proofing.

Some tools in the repository already use the v2 syntax (e.g., `tools/docker_validation.sh`), while others still use v1 syntax (e.g., `tools/docker_test_suite.py`).

## Verification
- ✅ YAML syntax validation passes
- ✅ All jobs with docker-compose usage have installation steps  
- ✅ Installation steps are placed before first docker-compose usage
- ✅ Docker Compose v2.29.2 installation tested successfully