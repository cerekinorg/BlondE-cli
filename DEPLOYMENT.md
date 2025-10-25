# BlondE-CLI Deployment Guide

Complete guide for deploying BlondE-CLI across multiple platforms.

## Table of Contents

1. [Quick Deploy](#quick-deploy)
2. [PyPI Deployment](#pypi-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Direct Download](#direct-download)
5. [Platform-Specific Packaging](#platform-specific-packaging)
6. [Automated CI/CD](#automated-cicd)

---

## Quick Deploy

Use the automated deployment script:

```bash
# Run full deployment pipeline
python deploy.py all

# Deploy to specific platform
python deploy.py pypi     # PyPI only
python deploy.py docker   # Docker only
python deploy.py github   # GitHub release only
```

---

## PyPI Deployment

### Prerequisites

```bash
pip install build twine
```

### Step-by-Step

1. **Update Version**
   
   Edit `pyproject.toml`:
   ```toml
   version = "1.0.0"  # Update this
   ```

2. **Run Tests**
   
   ```bash
   pytest tests/ -v
   ```

3. **Build Package**
   
   ```bash
   python -m build
   ```
   
   This creates:
   - `dist/blonde_cli-1.0.0-py3-none-any.whl`
   - `dist/blonde-cli-1.0.0.tar.gz`

4. **Test on TestPyPI** (Optional but recommended)
   
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```
   
   Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ blonde-cli
   ```

5. **Deploy to PyPI**
   
   ```bash
   python -m twine upload dist/*
   ```

6. **Verify Installation**
   
   ```bash
   pip install blonde-cli
   blnd --help
   ```

### PyPI Credentials

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN

[testpypi]
username = __token__
password = pypi-YOUR-TEST-API-TOKEN
```

---

## Docker Deployment

### Build Docker Image

```bash
# Build with version tag
docker build -t blonde-cli:1.0.0 -t blonde-cli:latest .

# Test locally
docker run -it blonde-cli:latest blnd chat
```

### Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag for Docker Hub
docker tag blonde-cli:latest cerekin/blonde-cli:1.0.0
docker tag blonde-cli:latest cerekin/blonde-cli:latest

# Push
docker push cerekin/blonde-cli:1.0.0
docker push cerekin/blonde-cli:latest
```

### Dockerfile Optimizations

The included `Dockerfile` features:

- Multi-stage builds for smaller images
- Layer caching for faster builds
- Non-root user for security
- GPU support (optional)
- Volume mounts for persistence

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  blonde-cli:
    image: cerekin/blonde-cli:latest
    container_name: blonde-cli
    volumes:
      - ./projects:/workspace
      - ~/.blonde:/root/.blonde
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    stdin_open: true
    tty: true
```

Run with:
```bash
docker-compose run blonde-cli blnd chat
```

---

## Direct Download

### Create Portable Package

```bash
python deploy.py portable
```

This creates `install_portable.sh` that users can download and run:

```bash
# User runs:
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/blonde-cli/main/install_portable.sh | bash
```

### GitHub Releases

1. **Build Package**
   
   ```bash
   python -m build
   ```

2. **Create Release** (using GitHub CLI)
   
   ```bash
   gh release create v1.0.0 \
     dist/*.whl \
     dist/*.tar.gz \
     --title "BlondE-CLI v1.0.0" \
     --notes-file RELEASE_NOTES.md
   ```

3. **Users Install**
   
   ```bash
   # Download wheel from GitHub releases
   pip install blonde_cli-1.0.0-py3-none-any.whl
   ```

---

## Platform-Specific Packaging

### Linux (Debian/Ubuntu)

Create `.deb` package:

```bash
# Install tools
sudo apt install python3-stdeb dh-python

# Build deb
python setup.py --command-packages=stdeb.command bdist_deb
```

Install:
```bash
sudo dpkg -i deb_dist/python3-blonde-cli_1.0.0-1_all.deb
```

### macOS (Homebrew)

Create Homebrew formula (`blonde-cli.rb`):

```ruby
class BlondeCli < Formula
  desc "AI-powered code assistant with memory and agentic capabilities"
  homepage "https://github.com/YOUR_REPO/blonde-cli"
  url "https://github.com/YOUR_REPO/blonde-cli/archive/v1.0.0.tar.gz"
  sha256 "SHA256_HASH"
  license "MIT"

  depends_on "python@3.10"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/blnd", "--help"
  end
end
```

Submit to Homebrew:
```bash
# Fork homebrew-core
# Add formula
# Submit PR
```

### Windows (Chocolatey)

Create `blonde-cli.nuspec`:

```xml
<?xml version="1.0"?>
<package>
  <metadata>
    <id>blonde-cli</id>
    <version>1.0.0</version>
    <title>BlondE CLI</title>
    <authors>Cerekin</authors>
    <description>AI-powered code assistant</description>
    <projectUrl>https://github.com/YOUR_REPO/blonde-cli</projectUrl>
    <licenseUrl>https://github.com/YOUR_REPO/blonde-cli/blob/main/LICENSE</licenseUrl>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <tags>ai cli code-assistant python</tags>
  </metadata>
</package>
```

---

## Automated CI/CD

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy BlondE-CLI

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .[dev]
      - name: Run tests
        run: pytest tests/ -v

  deploy-pypi:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Build package
        run: |
          pip install build
          python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

  deploy-docker:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: |
            cerekin/blonde-cli:latest
            cerekin/blonde-cli:${{ github.ref_name }}

  create-release:
    needs: [deploy-pypi, deploy-docker]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/*.whl
            dist/*.tar.gz
          generate_release_notes: true
```

---

## Testing Before Release

### Checklist

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Memory system works
- [ ] Agentic mode functional
- [ ] All commands work with flags
- [ ] Documentation up to date
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] Tested on Linux, macOS, Windows
- [ ] Docker image builds and runs
- [ ] API keys documented

### Test Installation

```bash
# Test from TestPyPI
pip install --index-url https://test.pypi.org/simple/ blonde-cli

# Test from wheel
pip install dist/blonde_cli-1.0.0-py3-none-any.whl

# Test from Docker
docker run -it blonde-cli:latest blnd --help
```

---

## Post-Deployment

1. **Announce on Social Media**
   - Twitter/X
   - Reddit (r/Python, r/LocalLLaMA, r/programming)
   - Hacker News
   - Product Hunt

2. **Update Documentation**
   - README.md
   - GitHub Wiki
   - Documentation site

3. **Monitor**
   - PyPI downloads
   - Docker pulls
   - GitHub stars
   - Issues reported

4. **Respond to Feedback**
   - Fix critical bugs quickly
   - Engage with community
   - Plan next version

---

## Troubleshooting

### PyPI Upload Fails

```bash
# Check credentials
cat ~/.pypirc

# Verify package metadata
twine check dist/*

# Use verbose mode
twine upload --verbose dist/*
```

### Docker Build Fails

```bash
# Check Dockerfile syntax
docker build --no-cache .

# View build logs
docker build . 2>&1 | tee build.log
```

### Tests Fail in CI

```bash
# Run locally with same Python version
python3.10 -m pytest tests/ -v

# Check environment variables
env | grep -i api

# View full error output
pytest tests/ -v -s --tb=long
```

---

## Version Management

### Semantic Versioning

BlondE-CLI follows [SemVer](https://semver.org/):

- **Major (1.0.0)**: Breaking changes
- **Minor (0.1.0)**: New features, backward compatible
- **Patch (0.0.1)**: Bug fixes

### Updating Version

1. Update `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit: `git commit -m "Bump version to 1.0.0"`
4. Tag: `git tag v1.0.0`
5. Push: `git push && git push --tags`

---

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_REPO/blonde-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_REPO/blonde-cli/discussions)
- **Email**: support@cerekin.com

---

**Happy Deploying! 🚀**
