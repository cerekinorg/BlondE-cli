# 🚀 Local Models - Quick Start

## ✅ Status: READY TO USE

Local model support is **fully functional**. Just add `--offline` to any command!

---

## 🎯 Quick Commands

### Chat
```bash
blnd chat --offline
```
First run downloads CodeLlama-7B (~3.8GB, 5-10 minutes)  
Subsequent runs are **instant** using cached model

### Generate Code
```bash
blnd gen "create a FastAPI server" --offline
```

### Fix Bugs
```bash
blnd fix mycode.py --offline
```

### Create Files
```bash
blnd create "user authentication module" auth.py --offline
```

### Document Code
```bash
blnd doc myproject/ --offline
```

---

## 🎨 Different Models

### CodeLlama (Default - Best for coding)
```bash
blnd chat --offline
```

### Mistral-7B (Fast general purpose)
```bash
blnd chat --offline --model TheBloke/Mistral-7B-Instruct-v0.2-GGUF
```

### DeepSeek-Coder (Advanced coding)
```bash
blnd chat --offline --model TheBloke/deepseek-coder-6.7b-instruct-GGUF
```

---

## 💾 Storage

**Models cached at:** `~/.blonde/models/`

**Size per model:** ~3.8GB

**First download:** 5-10 minutes  
**After that:** Instant (uses cache)

---

## 🔒 Privacy Benefits

✅ **100% Private** - No data sent to external servers  
✅ **Works Offline** - No internet needed after initial download  
✅ **Free Forever** - No API costs  
✅ **Full Control** - Customize all parameters  

---

## 🧪 Test It Now

```bash
# Quick test
./venv/bin/python demo_local.py

# Or jump right in
blnd chat --offline
```

---

## 📖 Full Documentation

See `LOCAL_MODELS_GUIDE.md` for:
- Complete model list
- Performance tuning
- GPU acceleration
- Troubleshooting
- Advanced usage

---

## ⚡ Tips

1. **First run takes 5-10 min** (downloads model)
2. **Subsequent runs are instant** (uses cache)
3. **Use `--memory` flag** for context awareness
4. **Use `--agentic` flag** to enable tools
5. **Models work offline** after first download

---

**🎉 You're ready! Start with:**

```bash
blnd chat --offline
```
