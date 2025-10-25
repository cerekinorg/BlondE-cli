#!/usr/bin/env python3
"""
BlondE-CLI Deployment Script

Handles deployment to multiple platforms:
- PyPI (pip install)
- Docker Hub
- GitHub Releases (direct download)
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path


def run_command(cmd, capture_output=False):
    """Run shell command and handle errors"""
    print(f"\n🚀 Running: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            return result.stdout
        else:
            subprocess.run(cmd, shell=True, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if capture_output and e.stderr:
            print(f"Error output: {e.stderr}")
        sys.exit(1)


def clean_build():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning build artifacts...")
    dirs_to_clean = ['build', 'dist', '*.egg-info', '__pycache__']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(f"**/{pattern}"):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Removed {path}")


def run_tests():
    """Run test suite before deployment"""
    print("\n🧪 Running tests...")
    run_command("pytest tests/ -v --tb=short")
    print("✅ All tests passed!")


def build_package():
    """Build Python package"""
    print("\n📦 Building Python package...")
    clean_build()
    run_command("python -m build")
    print("✅ Package built successfully!")


def deploy_to_pypi(test=True):
    """Deploy to PyPI or TestPyPI"""
    print(f"\n🚀 Deploying to {'TestPyPI' if test else 'PyPI'}...")
    
    if test:
        run_command("python -m twine upload --repository testpypi dist/*")
    else:
        run_command("python -m twine upload dist/*")
    
    print(f"✅ Deployed to {'TestPyPI' if test else 'PyPI'}!")


def build_docker():
    """Build Docker image"""
    print("\n🐳 Building Docker image...")
    
    # Get version from pyproject.toml
    version = run_command(
        "grep '^version' pyproject.toml | cut -d'\"' -f2",
        capture_output=True
    ).strip()
    
    image_name = f"blonde-cli:{version}"
    
    run_command(f"docker build -t {image_name} -t blonde-cli:latest .")
    print(f"✅ Docker image built: {image_name}")
    
    return image_name


def push_docker(image_name):
    """Push Docker image to Docker Hub"""
    print("\n🐳 Pushing Docker image to Docker Hub...")
    
    # Tag for Docker Hub (adjust username as needed)
    hub_image = f"cerekin/{image_name}"
    run_command(f"docker tag {image_name} {hub_image}")
    run_command(f"docker push {hub_image}")
    
    print(f"✅ Pushed to Docker Hub: {hub_image}")


def create_github_release():
    """Create GitHub release with binaries"""
    print("\n📤 Creating GitHub release...")
    
    version = run_command(
        "grep '^version' pyproject.toml | cut -d'\"' -f2",
        capture_output=True
    ).strip()
    
    # Create release notes
    release_notes = f"""
# BlondE-CLI v{version}

## What's New
- Context-aware AI with memory system
- Agentic mode for autonomous task execution
- Iterative refinement for all commands
- Enhanced UI with streaming responses
- Multi-platform support (Linux, macOS, Windows)

## Installation

### Via pip
```bash
pip install blonde-cli
```

### Via Docker
```bash
docker pull cerekin/blonde-cli:{version}
docker run -it cerekin/blonde-cli:{version}
```

### Direct Download
Download the wheel file from assets below and install:
```bash
pip install blonde_cli-{version}-py3-none-any.whl
```

## Quick Start
```bash
# Interactive chat with memory
blnd chat --memory --agentic

# Generate code
blnd gen "Create a REST API with FastAPI" --save api.py

# Fix bugs with iterative refinement
blnd fix myfile.py --iterative --memory

# Create files with tests
blnd create "A user authentication module" auth.py --with-tests
```

## Documentation
See [README.md](https://github.com/YOUR_REPO/blonde-cli) for full documentation.
"""
    
    # Save release notes
    with open("RELEASE_NOTES.md", "w") as f:
        f.write(release_notes)
    
    print("✅ Release notes created: RELEASE_NOTES.md")
    print("\n📝 Next steps:")
    print("1. Create a GitHub release manually or use GitHub CLI:")
    print(f"   gh release create v{version} dist/*.whl --notes-file RELEASE_NOTES.md")


def create_portable_installer():
    """Create portable installer script"""
    print("\n📦 Creating portable installer...")
    
    installer_script = """#!/bin/bash
# BlondE-CLI Portable Installer
# Works without pip or Python package management

set -e

INSTALL_DIR="$HOME/.blonde-cli"
VENV_DIR="$INSTALL_DIR/venv"
BIN_DIR="$HOME/.local/bin"

echo "🚀 Installing BlondE-CLI..."

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install BlondE-CLI
echo "📥 Installing BlondE-CLI..."
pip install blonde-cli

# Create symlink
ln -sf "$VENV_DIR/bin/blnd" "$BIN_DIR/blnd"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "📝 Add this to your ~/.bashrc or ~/.zshrc:"
    echo "export PATH=\"$BIN_DIR:\\$PATH\""
fi

echo ""
echo "✅ BlondE-CLI installed successfully!"
echo "🎉 Run 'blnd chat' to get started!"
"""
    
    with open("install_portable.sh", "w") as f:
        f.write(installer_script)
    
    os.chmod("install_portable.sh", 0o755)
    print("✅ Portable installer created: install_portable.sh")


def main():
    """Main deployment workflow"""
    print("=" * 60)
    print("BlondE-CLI Deployment Script")
    print("=" * 60)
    
    # Parse arguments
    args = sys.argv[1:]
    
    if not args:
        print("\nUsage:")
        print("  python deploy.py [test|pypi|docker|github|portable|all]")
        print("\nOptions:")
        print("  test     - Run tests only")
        print("  pypi     - Deploy to PyPI")
        print("  docker   - Build and push Docker image")
        print("  github   - Create GitHub release")
        print("  portable - Create portable installer")
        print("  all      - Run full deployment pipeline")
        sys.exit(0)
    
    action = args[0]
    
    try:
        if action == "test":
            run_tests()
        
        elif action == "pypi":
            run_tests()
            build_package()
            
            response = input("\nDeploy to TestPyPI first? (y/n): ")
            if response.lower() == 'y':
                deploy_to_pypi(test=True)
                input("\nTest the package, then press Enter to deploy to PyPI...")
            
            deploy_to_pypi(test=False)
        
        elif action == "docker":
            run_tests()
            image_name = build_docker()
            
            response = input("\nPush to Docker Hub? (y/n): ")
            if response.lower() == 'y':
                push_docker(image_name)
        
        elif action == "github":
            build_package()
            create_github_release()
        
        elif action == "portable":
            create_portable_installer()
        
        elif action == "all":
            print("\n🎯 Running full deployment pipeline...")
            run_tests()
            build_package()
            
            # PyPI
            response = input("\nDeploy to PyPI? (y/n): ")
            if response.lower() == 'y':
                deploy_to_pypi(test=False)
            
            # Docker
            response = input("\nBuild and push Docker image? (y/n): ")
            if response.lower() == 'y':
                image_name = build_docker()
                push_docker(image_name)
            
            # GitHub release
            create_github_release()
            
            # Portable installer
            create_portable_installer()
            
            print("\n" + "=" * 60)
            print("🎉 Deployment complete!")
            print("=" * 60)
        
        else:
            print(f"❌ Unknown action: {action}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
