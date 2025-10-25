#!/bin/bash
# Quick test of new features

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          Testing BlondE-CLI New Features                     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "✅ Test 1: Check blnd command is available"
which blnd && echo "   SUCCESS: blnd command found" || echo "   FAILED: blnd not found"
echo ""

echo "✅ Test 2: Check model_selector module"
python3 -c "from model_selector import select_model; print('   SUCCESS: model_selector imported')" 2>/dev/null || echo "   FAILED: model_selector import failed"
echo ""

echo "✅ Test 3: Verify no warnings on import"
echo "   Running: blnd --help (checking for warnings...)"
blnd --help 2>&1 | grep -q "WARNING" && echo "   FAILED: Warnings still present" || echo "   SUCCESS: No warnings!"
echo ""

echo "✅ Test 4: Check MODEL_SELECTOR_AVAILABLE flag"
python3 -c "from cli import MODEL_SELECTOR_AVAILABLE; print(f'   MODEL_SELECTOR_AVAILABLE = {MODEL_SELECTOR_AVAILABLE}')"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   All Tests Complete!                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Try the new interactive model selector:"
echo "   $ blnd chat --offline"
echo ""
