#!/usr/bin/env python3
"""Test the offline flow to debug model selector issue."""

import sys
from rich.console import Console

console = Console()

print("=" * 60)
print("TESTING OFFLINE FLOW")
print("=" * 60)
print()

# Test 1: Check imports
print("1. Checking imports...")
try:
    from cli import MODEL_SELECTOR_AVAILABLE
    print(f"   MODEL_SELECTOR_AVAILABLE: {MODEL_SELECTOR_AVAILABLE}")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

if not MODEL_SELECTOR_AVAILABLE:
    print("   ERROR: Model selector not available!")
    sys.exit(1)

try:
    from model_selector import select_model
    print(f"   select_model: {select_model}")
except Exception as e:
    print(f"   ERROR importing select_model: {e}")
    sys.exit(1)

print()

# Test 2: Check the condition
print("2. Testing condition (offline=True, model=None)...")
offline = True
model = None
result = offline and not model and MODEL_SELECTOR_AVAILABLE
print(f"   offline={offline}, model={model}")
print(f"   Condition result: {result}")

if result:
    print("   ✓ Should call select_model()")
else:
    print("   ✗ Will NOT call select_model()")
    sys.exit(1)

print()

# Test 3: Simulate calling select_model
print("3. Simulating model selector call...")
print("   (This will show the actual menu)")
print()

try:
    selection = select_model()
    if selection:
        repo, file, is_cached, path = selection
        print(f"\n   ✓ Selection successful!")
        print(f"     repo={repo}")
        print(f"     file={file}")
        print(f"     is_cached={is_cached}")
        print(f"     path={path}")
        
        model_string = f"{repo}/{file}"
        print(f"     model string: {model_string}")
    else:
        print("   Cancelled by user")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
