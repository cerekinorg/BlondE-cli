# 🎯 Interactive Model Selection Guide

## Overview

BlondE-CLI now features an **interactive model selector** that appears when you use `--offline` without specifying a model. No more manual model path entry - just choose from a menu!

---

## 🚀 How It Works

### When You Run `--offline` Commands

```bash
# Just run with --offline flag
blnd chat --offline
blnd gen "your prompt" --offline
blnd fix file.py --offline
blnd create "description" file.py --offline
blnd doc project/ --offline
```

**What Happens:**
1. 📦 Shows any **cached models** you already have
2. 🌐 Shows **available models** to download
3. 🎯 Lets you **select** which one to use
4. 📥 **Auto-downloads** if needed (first time only)

---

## 📋 Menu Options

### Option 1: Use Cached Models (if available)

If you have models already downloaded:

```
📦 Cached Local Models
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Model File                ┃   Size ┃ Repository        ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ 1  │ codellama-7b.Q4_K_M.gguf  │ 3.8GB  │ CodeLlama-7B-GGUF │
│ 2  │ mistral-7b...gguf         │ 4.1GB  │ Mistral-7B...     │
└────┴───────────────────────────┴────────┴───────────────────┘

✓ You have cached models ready to use!

Choose an option [use/download/cancel] (use):
```

- Type **`use`** → Select from cached models (instant)
- Type **`download`** → Download a new model
- Type **`cancel`** → Exit

### Option 2: Download New Models

If no models cached, or if you chose "download":

```
🌐 Available Models to Download
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Model                  ┃   Size ┃ Description              ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ CodeLlama-7B ⭐        │ 3.8GB  │ Best for code generation │
│ 2  │ Mistral-7B-Instruct    │ 4.1GB  │ Fast general-purpose     │
│ 3  │ DeepSeek-Coder-6.7B    │ 3.8GB  │ Advanced coding tasks    │
│ 4  │ Llama-2-7B-Chat        │ 3.8GB  │ Conversational tasks     │
│ 5  │ Phi-2                  │ 1.6GB  │ Smaller, faster model    │
└────┴────────────────────────┴────────┴──────────────────────────┘

💡 Recommended for first-time users: CodeLlama-7B (Option 1)

Download CodeLlama-7B now? [Y/n]:
```

---

## 🎬 Usage Scenarios

### Scenario 1: First Time User (No Models)

```bash
$ blnd chat --offline

╔══════════════════════════════════════════════════╗
║    🤖 BlondE-CLI Local Model Selector           ║
╚══════════════════════════════════════════════════╝

No cached models found. Let's download one!

🌐 Available Models to Download
[Shows table...]

💡 Recommended for first-time users: CodeLlama-7B (Option 1)

Download CodeLlama-7B now? [Y/n]: y

Downloading CodeLlama-7B (3.8GB)...
This will take 5-10 minutes on first run.
[Download progress bar...]
✓ Model cached!

[Chat starts...]
```

### Scenario 2: Existing User (Has Models)

```bash
$ blnd chat --offline

📦 Cached Local Models
1. codellama-7b.Q4_K_M.gguf (3.8GB)
2. mistral-7b-instruct-v0.2.Q4_K_M.gguf (4.1GB)

✓ You have cached models ready to use!

Choose an option [use/download/cancel] (use): use
Select cached model (1-2): 2

✓ Using: mistral-7b-instruct-v0.2.Q4_K_M.gguf

[Chat starts instantly...]
```

### Scenario 3: Want Different Model

```bash
$ blnd chat --offline

📦 Cached Local Models
1. codellama-7b.Q4_K_M.gguf (3.8GB)

Choose an option [use/download/cancel]: download

🌐 Available Models to Download
[Shows all 5 options...]

Select model to download (1-5 or 'cancel'): 3

Selected: DeepSeek-Coder-6.7B (3.8GB)
Specialized for advanced coding tasks

Download DeepSeek-Coder-6.7B? [Y/n]: y

Downloading... This may take 5-10 minutes.
[Download...]
✓ Downloaded!

[Chat starts...]
```

---

## 🎨 Available Models

| # | Model | Size | Best For |
|---|-------|------|----------|
| 1 | **CodeLlama-7B** ⭐ | 3.8GB | Code generation, bug fixing |
| 2 | **Mistral-7B-Instruct** | 4.1GB | General purpose, fast |
| 3 | **DeepSeek-Coder-6.7B** | 3.8GB | Advanced coding tasks |
| 4 | **Llama-2-7B-Chat** | 3.8GB | Conversational AI |
| 5 | **Phi-2** | 1.6GB | Quick tasks, low memory |

⭐ = Recommended for first-time users

---

## 💡 Smart Features

### 1. **Auto-Recommend CodeLlama**
- First time with no models? We'll suggest CodeLlama-7B
- Just hit Enter to accept the recommendation

### 2. **Instant Access to Cached Models**
- Already downloaded? No wait time!
- Select and start chatting immediately

### 3. **One-Time Download**
- Models downloaded to `~/.blonde/models/`
- Used by all future `--offline` commands
- Never download twice

### 4. **Cancel Anytime**
- Changed your mind? Just type `cancel`
- Or press Ctrl+C

---

## 🔧 Advanced: Skip the Menu

If you know which model you want:

```bash
# Specify model directly (skips interactive menu)
blnd chat --offline --model TheBloke/Mistral-7B-Instruct-v0.2-GGUF

# Or use environment variable
export BLONDE_OFFLINE_MODEL="TheBloke/CodeLlama-7B-GGUF"
blnd chat --offline
```

---

## 📍 Storage Location

Models are cached at: `~/.blonde/models/`

```bash
# Check what you have
ls -lh ~/.blonde/models/

# Free up space (delete models)
rm -rf ~/.blonde/models/*
```

---

## ❓ FAQ

### Q: Do I see the menu every time?
**A:** Only if you don't specify a model with `--model` flag. If you have cached models, you can quickly select them.

### Q: Can I bypass the menu?
**A:** Yes, use `--model` flag:
```bash
blnd chat --offline --model TheBloke/CodeLlama-7B-GGUF
```

### Q: What happens if I cancel?
**A:** The command exits gracefully. No model is downloaded or selected.

### Q: Can I delete models?
**A:** Yes! They're in `~/.blonde/models/`. Delete any .gguf files you don't need.

### Q: How do I get the warnings to go away?
**A:** The warnings about memory/tools are now suppressed. You'll only see the interactive menu.

---

## 🎊 Benefits

✅ **No Manual Paths** - No more typing long model paths  
✅ **Visual Selection** - See what you have vs what's available  
✅ **Smart Defaults** - CodeLlama recommended for beginners  
✅ **Fast Switching** - Quickly switch between cached models  
✅ **One Download** - Download once, use everywhere  
✅ **Offline Ready** - Works without internet after first download  

---

## 🚀 Try It Now

```bash
# Just run with --offline
blnd chat --offline

# The interactive menu will guide you!
```

No more guessing which model to use or where it's stored. The interactive selector handles everything! 🎉
