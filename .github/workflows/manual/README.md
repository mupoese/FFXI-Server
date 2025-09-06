# Manual Build Workflows

This directory contains workflow files for manual compilation of FFXI Server components on Windows and macOS platforms. These workflows are not part of the main CI/CD pipeline but can be triggered manually when needed.

## Available Workflows

### Windows Build (`windows-build.yml`)
Manual workflow for building FFXI Server on Windows with the following options:
- **Build Type**: Debug or Release
- **Tracy Profiling**: Enable/disable Tracy profiling support
- **Modules**: Enable/disable module support
- **Launcher Build**: Includes Windows launcher compilation

**Usage:**
1. Go to the Actions tab in GitHub
2. Select "Windows Manual Build" workflow
3. Click "Run workflow"
4. Choose your build options
5. Download artifacts when complete

### macOS Build (`macos-build.yml`)
Manual workflow for building FFXI Server on macOS with the following options:
- **Build Type**: Debug or Release  
- **Integration Tests**: Enable/disable integration testing
- **Launcher Build**: Includes macOS launcher compilation

**Usage:**
1. Go to the Actions tab in GitHub
2. Select "macOS Manual Build" workflow
3. Click "Run workflow"
4. Choose your build options
5. Download artifacts when complete

### Launcher Build Test (`launcher-build-test.yml`)
Cross-platform launcher compilation testing for development purposes.
Tests launcher builds on Ubuntu, Windows, and macOS with fictive .env configurations.

## Docker-First Approach

The main CI/CD pipeline now focuses on Docker builds only. For production deployments:
1. Use the Docker build workflow from the main `.github/workflows/` directory
2. Docker images include launcher compilation capabilities
3. Launcher files are served via web interface on port 8089

## Building for Production

For production deployments, use the Docker approach:

```bash
# Build Docker image
docker build -f docker/Dockerfile -t ffxi-server .

# Run with launcher web server
docker run -p 8089:8089 ffxi-server all-with-launcher

# Access launcher downloads
curl http://localhost:8089/downloads/
```

## Migration from Windows/macOS Builds

If you were previously using Windows or macOS builds from the main workflow:
1. Use these manual workflows instead for desktop compilation
2. Consider switching to Docker for server deployments  
3. Docker provides better consistency and easier deployment

## Environment Variables

All manual builds support the same environment variables as the main Docker build:
- Server configuration via `.env` files
- Database connection settings
- Network configuration options
- Launcher customization options