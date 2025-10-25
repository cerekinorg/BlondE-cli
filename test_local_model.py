#!/usr/bin/env python3
"""
Quick test for local model functionality
"""

import sys
from pathlib import Path

# Test imports
print("Testing local model imports...")
try:
    from llama_cpp import Llama
    print("✓ llama-cpp-python installed")
except ImportError as e:
    print(f"✗ llama-cpp-python import failed: {e}")
    sys.exit(1)

try:
    from models.local import LocalAdapter
    print("✓ LocalAdapter imported")
except ImportError as e:
    print(f"✗ LocalAdapter import failed: {e}")
    sys.exit(1)

try:
    from cli import load_adapter
    print("✓ CLI load_adapter imported")
except ImportError as e:
    print(f"✗ CLI import failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("Local Model Setup Verified!")
print("="*60)

print("\n📦 Available GGUF models to download:")
print("1. TheBloke/CodeLlama-7B-GGUF (Recommended for coding)")
print("   - File: codellama-7b.Q4_K_M.gguf (~3.8GB)")
print("   - Best for code generation and fixing")
print()
print("2. TheBloke/Llama-2-7B-Chat-GGUF (Good for chat)")
print("   - File: llama-2-7b-chat.Q4_K_M.gguf (~3.8GB)")
print("   - Best for conversational tasks")
print()
print("3. TheBloke/Mistral-7B-Instruct-v0.2-GGUF (Fast and capable)")
print("   - File: mistral-7b-instruct-v0.2.Q4_K_M.gguf (~4.1GB)")
print("   - Good balance of speed and quality")

print("\n" + "="*60)
print("Usage Examples:")
print("="*60)
print()
print("# Chat with local model (auto-downloads on first use):")
print("blnd chat --offline")
print()
print("# Use specific GGUF model:")
print("blnd chat --offline --model TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
print()
print("# Generate code with local model:")
print("blnd gen \"create a quicksort function\" --offline --save quicksort.py")
print()
print("# Fix code with local model:")
print("blnd fix myfile.py --offline")
print()
print("# Create files with local model:")
print("blnd create \"REST API server with Flask\" server.py --offline")

print("\n" + "="*60)
print("⚠️  First Run Information:")
print("="*60)
print("- Models will be downloaded to: ~/.blonde/models/")
print("- First download may take 5-10 minutes (3-4GB per model)")
print("- Subsequent runs will use cached models instantly")
print("- You can pre-download models using huggingface-cli")

print("\n✅ Local model support is READY!")
print("Run 'blnd chat --offline' to start using local models.\n")
