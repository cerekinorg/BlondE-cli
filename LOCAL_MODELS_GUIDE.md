# 🏠 BlondE-CLI Local Models Guide

Complete guide to running BlondE-CLI with local GGUF models (100% offline, privacy-focused)

---

## ✅ Setup Status

- ✅ **llama-cpp-python** v0.3.16 installed
- ✅ **LocalAdapter** ready and functional
- ✅ **Offline mode** fully integrated
- ✅ **Auto-download** from HuggingFace configured

---

## 🚀 Quick Start

### Run with Default Model (CodeLlama-7B)

```bash
# Start chat with local model (auto-downloads on first use)
blnd chat --offline

# Generate code
blnd gen "create a binary search tree class" --offline

# Fix code
blnd fix myapp.py --offline

# Create new file
blnd create "FastAPI REST API" api.py --offline
```

**First run:** Model will auto-download (~3.8GB, takes 5-10 minutes)  
**Subsequent runs:** Uses cached model instantly

---

## 📦 Recommended GGUF Models

### 1. **CodeLlama-7B** (Default, Best for Coding)
```bash
# Automatically used with --offline flag
blnd chat --offline

# Or specify explicitly:
blnd chat --offline --model TheBloke/CodeLlama-7B-GGUF
```
- **Size:** ~3.8GB (Q4_K_M quantization)
- **Best for:** Code generation, bug fixing, documentation
- **Speed:** Fast on modern CPUs
- **Quality:** Excellent for coding tasks

### 2. **Mistral-7B-Instruct** (Fast & Capable)
```bash
blnd chat --offline --model TheBloke/Mistral-7B-Instruct-v0.2-GGUF
```
- **Size:** ~4.1GB
- **Best for:** General chat, code explanation, creative tasks
- **Speed:** Very fast
- **Quality:** High-quality responses

### 3. **Llama-2-7B-Chat** (Good for Conversation)
```bash
blnd chat --offline --model TheBloke/Llama-2-7B-Chat-GGUF
```
- **Size:** ~3.8GB
- **Best for:** Interactive chat, explanations
- **Speed:** Fast
- **Quality:** Good conversational abilities

### 4. **DeepSeek-Coder-6.7B** (Specialized for Code)
```bash
blnd chat --offline --model TheBloke/deepseek-coder-6.7b-instruct-GGUF
```
- **Size:** ~3.8GB
- **Best for:** Advanced code tasks, multiple languages
- **Speed:** Fast
- **Quality:** Excellent for programming

---

## 💡 Usage Examples

### Interactive Chat
```bash
# Basic offline chat
blnd chat --offline

# With debug logging
blnd chat --offline --debug

# With memory enabled (recommended)
blnd chat --offline --memory

# With agentic tools
blnd chat --offline --agentic
```

### Code Generation
```bash
# Generate and save
blnd gen "implement quicksort in Python" --offline --save quicksort.py

# Specify language
blnd gen "REST API with error handling" --offline --lang python --save api.py

# With memory context
blnd gen "fibonacci generator" --offline --memory
```

### Bug Fixing
```bash
# Fix single file
blnd fix buggy_code.py --offline

# Fix entire directory
blnd fix ./src --offline --preview

# With suggestions
blnd fix app.py --offline --suggest

# Iterative refinement
blnd fix app.py --offline --iterative
```

### File Creation
```bash
# Create with context awareness
blnd create "Database migration script" migrate.py --offline

# With iterative refinement
blnd create "User authentication module" auth.py --offline --iterative

# With tests
blnd create "Calculator class" calc.py --offline --with-tests

# Agentic mode (suggests related files)
blnd create "Blog post model" models/post.py --offline --agentic
```

### Documentation
```bash
# Document single file
blnd doc mycode.py --offline

# Document entire project
blnd doc ./src --offline --export PROJECT_DOCS.md

# Different styles
blnd doc complex_code.py --offline --style tutorial
blnd doc module.py --offline --style concise
```

---

## 🔧 Advanced Configuration

### Custom Model Parameters

Edit `models/local.py` to customize:

```python
# Adjust context length (default: 2048)
n_ctx=4096  # More context = more memory usage

# Adjust output length
max_tokens=500  # Longer responses

# Adjust temperature
temperature=0.7  # 0=deterministic, 1=creative

# CPU threads
n_threads=8  # Use more CPU cores
```

### Pre-download Models

To avoid download during first use:

```bash
# Using huggingface-cli
pip install huggingface-hub[cli]

huggingface-cli download TheBloke/CodeLlama-7B-GGUF \
    codellama-7b.Q4_K_M.gguf \
    --cache-dir ~/.blonde/models
```

### Model Storage Location

Models are cached at: `~/.blonde/models/`

```bash
# Check model cache
ls -lh ~/.blonde/models/

# Remove cached models to free space
rm -rf ~/.blonde/models/*
```

---

## ⚙️ System Requirements

### Minimum Requirements
- **RAM:** 8GB (for 7B models)
- **Storage:** 5GB free space per model
- **CPU:** Modern x86_64 or ARM64 processor
- **OS:** Linux, macOS, or Windows

### Recommended Requirements
- **RAM:** 16GB+ (for better performance)
- **Storage:** 20GB+ (for multiple models)
- **CPU:** 8+ cores
- **GPU:** Optional (see GPU acceleration below)

---

## 🚄 GPU Acceleration (Optional)

### NVIDIA CUDA
```bash
# Reinstall with CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# Then use normally
blnd chat --offline
```

### Apple Metal (M1/M2/M3)
```bash
# Reinstall with Metal support
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# Then use normally
blnd chat --offline
```

**Note:** GPU acceleration provides 5-10x speedup for inference.

---

## 🎛️ Performance Tuning

### For Faster Responses
```python
# In models/local.py, adjust:
max_tokens=100  # Shorter responses
temperature=0.3  # More focused
```

### For Better Quality
```python
# In models/local.py, adjust:
n_ctx=4096      # More context
max_tokens=500  # Longer, detailed responses
temperature=0.7 # More creative
```

### For Low-Memory Systems
Use smaller quantizations:
- `Q2_K` - ~2GB (lower quality)
- `Q3_K_M` - ~2.7GB (decent quality)
- `Q4_K_M` - ~3.8GB (recommended balance)
- `Q5_K_M` - ~4.8GB (higher quality)
- `Q8_0` - ~7GB (highest quality)

---

## 🔒 Privacy & Offline Benefits

### Why Use Local Models?

1. **100% Private** - No data sent to external servers
2. **Offline First** - Works without internet
3. **No API Costs** - Free to use unlimited
4. **Low Latency** - Instant responses (after model load)
5. **Customizable** - Full control over parameters

### Use Cases for Local Models

- ✅ Sensitive code (proprietary, confidential)
- ✅ Air-gapped environments
- ✅ Unstable internet connection
- ✅ Cost-sensitive projects
- ✅ Learning & experimentation

---

## 🐛 Troubleshooting

### Issue: "Failed to download model"
**Solution:**
```bash
# Check internet connection
ping huggingface.co

# Try manual download
pip install huggingface-hub[cli]
huggingface-cli download TheBloke/CodeLlama-7B-GGUF
```

### Issue: "Model loading failed"
**Solution:**
```bash
# Check available memory
free -h

# Try smaller model
blnd chat --offline --model TheBloke/Llama-2-7B-Chat-GGUF

# Or use smaller quantization (Q4_K_S instead of Q4_K_M)
```

### Issue: Slow inference
**Solution:**
1. Use GPU acceleration (see above)
2. Reduce `max_tokens` in `models/local.py`
3. Use faster model (Mistral-7B)
4. Increase CPU threads in `models/local.py`

### Issue: Out of memory
**Solution:**
```bash
# Use smaller quantization
# Edit models/local.py and change model_file:
model_file="codellama-7b.Q3_K_M.gguf"  # Instead of Q4_K_M
```

---

## 📊 Model Comparison

| Model | Size | Speed | Code Quality | Chat Quality | Best For |
|-------|------|-------|--------------|--------------|----------|
| CodeLlama-7B | 3.8GB | Fast | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Coding |
| Mistral-7B | 4.1GB | Very Fast | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | General |
| DeepSeek-Coder | 3.8GB | Fast | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Code |
| Llama-2-Chat | 3.8GB | Fast | ⭐⭐⭐ | ⭐⭐⭐⭐ | Chat |

---

## 🔄 Switching Between Online & Offline

### Use Online for:
- Complex tasks requiring GPT-4 level quality
- Long conversations (more context)
- Latest model capabilities

```bash
blnd chat  # Default: online (OpenRouter)
```

### Use Offline for:
- Privacy-sensitive code
- Fast local inference
- No internet scenarios
- Cost-free operation

```bash
blnd chat --offline  # Local GGUF model
```

### Hybrid Approach
```bash
# Use online for complex planning
blnd gen "design microservices architecture" --save plan.md

# Use offline for implementation
blnd create "implement user service from plan.md" service.py --offline
```

---

## 📈 Next Steps

1. **Try it out:**
   ```bash
   blnd chat --offline
   ```

2. **Test different models:**
   ```bash
   blnd chat --offline --model TheBloke/Mistral-7B-Instruct-v0.2-GGUF
   ```

3. **Enable memory for better context:**
   ```bash
   blnd chat --offline --memory
   ```

4. **Use agentic tools:**
   ```bash
   blnd chat --offline --agentic
   ```

5. **Optimize performance:**
   - Enable GPU acceleration if available
   - Adjust parameters in `models/local.py`
   - Try different quantizations

---

## 💬 Support

- **Documentation:** See `README.md` and `USER_GUIDE.md`
- **Issues:** Report on GitHub
- **Models:** Browse at https://huggingface.co/TheBloke

---

**🎉 You're ready to use BlondE-CLI with local models!**

Start with: `blnd chat --offline`
