# How to Set Up Your OpenRouter API Key

This guide will help you get your OpenRouter API key set up quickly.

## Step 1: Create OpenRouter Account

1. Visit https://openrouter.ai/
2. Click "Sign In" or "Sign Up"
3. Create an account (can use Google, GitHub, or email)

## Step 2: Get Your API Key

1. After logging in, go to https://openrouter.ai/keys
2. Click "Create Key" button
3. Give your key a name (e.g., "Causal Discovery")
4. (Optional) Set a credit limit for safety
5. Click "Create"
6. **Copy the API key** - it will look like: `sk-or-v1-...`
   - ⚠️ **IMPORTANT**: You can only see this once! Save it securely.

## Step 3: Add Credits (Free Tier Available)

OpenRouter offers a small free tier to test:

1. Go to https://openrouter.ai/credits
2. For testing: $5 credit is plenty (lasts for ~50-100 discovery runs)
3. Click "Add Credits"
4. Follow payment process

**Free Credits**: Sometimes OpenRouter offers free trial credits for new users.

## Step 4: Configure Your Project

### Option A: Using .env File (Recommended)

1. In your project directory, create a `.env` file:

```bash
# Create from template
cp config/.env.example .env
```

2. Open `.env` in a text editor and replace the placeholder:

```
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
```

3. Save the file

### Option B: Environment Variable (Alternative)

Set as system environment variable:

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY = "sk-or-v1-YOUR_ACTUAL_KEY_HERE"
```

**Windows (Command Prompt):**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
```

**macOS/Linux (Bash/Zsh):**
```bash
export OPENROUTER_API_KEY="sk-or-v1-YOUR_ACTUAL_KEY_HERE"
```

## Step 5: Verify Setup

Run the test script:

```bash
python test_setup.py
```

You should see:
```
[OK] OPENROUTER_API_KEY is set
[SUCCESS] SETUP COMPLETE - System is ready to use!
```

## Step 6: Test with Example

Run a quick test:

```bash
python examples/basic_example.py
```

If it works, you'll see the discovery process running and results saved to `outputs/`.

## Troubleshooting

### Error: "API key not provided"

**Cause**: .env file not found or API key not set

**Solution**:
1. Check `.env` file exists in project root (same folder as `test_setup.py`)
2. Open `.env` and verify key is present
3. Make sure no extra spaces or quotes
4. Restart terminal/IDE

### Error: "Invalid API key"

**Cause**: Key is incorrect or expired

**Solution**:
1. Go back to https://openrouter.ai/keys
2. Verify the key is active
3. Try creating a new key
4. Copy the full key including `sk-or-v1-` prefix

### Error: "Insufficient credits"

**Cause**: No credits in account

**Solution**:
1. Go to https://openrouter.ai/credits
2. Add credits ($5 recommended for testing)
3. Wait a few seconds for credits to appear
4. Try again

### Key Security Best Practices

1. ✅ **DO**: Keep your key in `.env` file (which is in `.gitignore`)
2. ✅ **DO**: Use environment variables for production
3. ❌ **DON'T**: Commit your key to Git
4. ❌ **DON'T**: Share your key publicly
5. ❌ **DON'T**: Hardcode key in source files

If you accidentally expose your key:
1. Go to https://openrouter.ai/keys
2. Delete the exposed key immediately
3. Create a new key
4. Update your `.env` file

## Cost Estimates

**Typical Usage** (with Claude 3.5 Sonnet):
- Simple discovery (3-5 variables, no data): ~$0.05-0.10
- Medium discovery (5-7 variables, with data): ~$0.15-0.30
- Complex discovery (8-10 variables, with data): ~$0.30-0.50

**Cost Factors**:
- Number of variables (more = more API calls)
- `n_samples` setting (higher = more robust but more expensive)
- Conflict resolution (adds extra calls)
- Model choice (Claude Sonnet is mid-range)

**Cost Reduction Tips**:
1. Start with `n_samples=2` for testing
2. Use `resolve_conflicts=False` for quick tests
3. Test with small variable sets first
4. Consider cheaper models for exploration:
   - `openai/gpt-3.5-turbo` (cheaper, less capable)
   - `meta-llama/llama-3-70b` (good quality, lower cost)

## Alternative LLM Models

Edit `.env` to try different models:

**Claude Family** (Recommended):
```
LLM_MODEL=anthropic/claude-3.5-sonnet  # Best quality
LLM_MODEL=anthropic/claude-3-haiku     # Faster, cheaper
```

**OpenAI Family**:
```
LLM_MODEL=openai/gpt-4-turbo          # Excellent quality
LLM_MODEL=openai/gpt-3.5-turbo        # Budget option
```

**Other Options**:
```
LLM_MODEL=meta-llama/llama-3-70b      # Open source, good quality
LLM_MODEL=google/gemini-pro           # Google's model
```

## Getting Help

If you're still having issues:

1. **Check Status**: https://openrouter.ai/status
2. **Documentation**: https://openrouter.ai/docs
3. **Discord**: https://discord.gg/openrouter
4. **Email**: support@openrouter.ai

## Quick Reference

**OpenRouter Dashboard**: https://openrouter.ai/  
**API Keys**: https://openrouter.ai/keys  
**Credits**: https://openrouter.ai/credits  
**Usage Stats**: https://openrouter.ai/activity  
**Documentation**: https://openrouter.ai/docs  

---

**Ready to start?**

Once your API key is set up, try:

```bash
# Verify setup
python test_setup.py

# Run basic example
python examples/basic_example.py

# Run health example with data
python examples/health_example.py
```

Good luck with your causal discovery! 🚀

