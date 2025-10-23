# Model Names & Provider Reference

Complete reference for all available model names and provider identifiers for use with `init_chat_model()`.

## 🎯 Quick Reference

### Format

```python
model = init_chat_model("provider:model-name")
```

### Environment Variable

```env
# In .env file
MODEL_PROVIDER=provider:model-name
```

---

## 🔴 Anthropic Models

### Provider Identifier
```
anthropic
```

### Available Models

| Model Name | Identifier | Cost (Input/Output) | Speed | Best For |
|-----------|-----------|-------------------|-------|----------|
| **Claude 3.5 Haiku** | `anthropic:claude-3-5-haiku-latest` | $0.80/$4 per M | ⚡ Fast | Development, testing |
| **Claude 3.5 Sonnet** | `anthropic:claude-3-5-sonnet-latest` | $3/$15 per M | ⚡⚡ Medium | Production, quality |
| **Claude 3 Opus** | `anthropic:claude-3-opus-latest` | $15/$60 per M | ⚡⚡⚡ Slow | Complex reasoning |
| **Claude 3 Haiku** | `anthropic:claude-3-haiku-latest` | $0.25/$1.25 per M | ⚡ Fast | Legacy |
| **Claude 3 Sonnet** | `anthropic:claude-3-sonnet-latest` | $3/$15 per M | ⚡⚡ Medium | Legacy |

### Usage Examples

```python
# Development (fast, cheap)
model = init_chat_model("anthropic:claude-3-5-haiku-latest")

# Production (balanced)
model = init_chat_model("anthropic:claude-3-5-sonnet-latest")

# High quality (slow, expensive)
model = init_chat_model("anthropic:claude-3-opus-latest")
```

### Environment Variable

```env
MODEL_PROVIDER=anthropic:claude-3-5-haiku-latest
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## 🔵 OpenAI Models

### Provider Identifier
```
openai
```

### Available Models

| Model Name | Identifier | Cost (Input/Output) | Speed | Best For |
|-----------|-----------|-------------------|-------|----------|
| **GPT-4o Mini** | `openai:gpt-4o-mini` | $0.15/$0.60 per M | ⚡ Fast | **Production (recommended)** |
| **GPT-4o** | `openai:gpt-4o` | $5/$15 per M | ⚡⚡ Medium | High quality |
| **GPT-4 Turbo** | `openai:gpt-4-turbo` | $10/$30 per M | ⚡⚡ Medium | Complex tasks |
| **GPT-3.5 Turbo** | `openai:gpt-3.5-turbo` | $0.50/$1.50 per M | ⚡ Fast | Legacy |

### Usage Examples

```python
# Recommended for production (best value)
model = init_chat_model("openai:gpt-4o-mini")

# Higher quality
model = init_chat_model("openai:gpt-4o")

# Most capable
model = init_chat_model("openai:gpt-4-turbo")
```

### Environment Variable

```env
MODEL_PROVIDER=openai:gpt-4o-mini
OPENAI_API_KEY=sk-proj-your-key-here
```

---

## 🟢 Google Gemini Models

### Provider Identifier
```
google_genai
```

### Available Models

| Model Name | Identifier | Cost | Speed | Best For |
|-----------|-----------|------|-------|----------|
| **Gemini 2.5 Flash Lite** | `google_genai:gemini-2.5-flash-lite` | Free tier | ⚡⚡⚡ Very Fast | **Development (free)** |
| **Gemini 2.5 Flash** | `google_genai:gemini-2.5-flash` | $0.075/$0.30 per M | ⚡⚡⚡ Very Fast | Production |
| **Gemini 2.0 Flash** | `google_genai:gemini-2.0-flash` | $0.075/$0.30 per M | ⚡⚡⚡ Very Fast | Production |
| **Gemini 1.5 Pro** | `google_genai:gemini-1.5-pro` | $1.25/$5 per M | ⚡⚡ Medium | High quality |
| **Gemini 1.5 Flash** | `google_genai:gemini-1.5-flash` | $0.075/$0.30 per M | ⚡⚡⚡ Very Fast | Legacy |

### Usage Examples

```python
# Free tier (development)
model = init_chat_model("google_genai:gemini-2.5-flash-lite")

# Production (fast, cheap)
model = init_chat_model("google_genai:gemini-2.5-flash")

# High quality
model = init_chat_model("google_genai:gemini-1.5-pro")
```

### Environment Variable

```env
MODEL_PROVIDER=google_genai:gemini-2.5-flash-lite
GOOGLE_API_KEY=your-key-here
```

---

## 📋 Complete Provider List

### All Supported Providers

```python
# Anthropic
"anthropic:claude-3-5-haiku-latest"
"anthropic:claude-3-5-sonnet-latest"
"anthropic:claude-3-opus-latest"

# OpenAI
"openai:gpt-4o-mini"
"openai:gpt-4o"
"openai:gpt-4-turbo"

# Google Gemini
"google_genai:gemini-2.5-flash-lite"
"google_genai:gemini-2.5-flash"
"google_genai:gemini-2.0-flash"
"google_genai:gemini-1.5-pro"

# Azure OpenAI
"azure_openai:gpt-4.1"

# AWS Bedrock
"anthropic.claude-3-5-sonnet-20240620-v1:0" (bedrock_converse)
```

---

## 🔧 How to Use Model Names

### Method 1: In Code

```python
from langchain.chat_models import init_chat_model

# Using model name directly
model = init_chat_model("openai:gpt-4o-mini")

# Using environment variable
import os
model_name = os.getenv("MODEL_PROVIDER", "anthropic:claude-3-5-haiku-latest")
model = init_chat_model(model_name)
```

### Method 2: In Environment File

```env
# .env file
MODEL_PROVIDER=openai:gpt-4o-mini
OPENAI_API_KEY=sk-proj-your-key-here
```

Then in code:

```python
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model_provider = os.getenv("MODEL_PROVIDER")
model = init_chat_model(model_provider)
```

### Method 3: Direct Class Import

```python
# OpenAI
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o-mini")

# Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

# Anthropic
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-5-haiku-latest")
```

---

## 💡 Naming Convention

All model names follow this pattern:

```
provider:model-identifier
```

### Examples

```
anthropic:claude-3-5-haiku-latest
├─ provider: anthropic
└─ model: claude-3-5-haiku-latest

openai:gpt-4o-mini
├─ provider: openai
└─ model: gpt-4o-mini

google_genai:gemini-2.5-flash-lite
├─ provider: google_genai
└─ model: gemini-2.5-flash-lite
```

---

## 🎯 Recommended Models by Use Case

### Development & Testing
```python
# Free tier available
model = init_chat_model("google_genai:gemini-2.5-flash-lite")

# Or cheap Anthropic
model = init_chat_model("anthropic:claude-3-5-haiku-latest")
```

### Production (Balanced)
```python
# Best cost/quality ratio
model = init_chat_model("openai:gpt-4o-mini")
```

### Production (Quality-First)
```python
# Best reasoning and reliability
model = init_chat_model("anthropic:claude-3-5-sonnet-latest")
```

### Production (Speed-First)
```python
# Fastest inference
model = init_chat_model("google_genai:gemini-2.5-flash")
```

### Complex Reasoning
```python
# Most capable
model = init_chat_model("anthropic:claude-3-opus-latest")
```

---

## 📊 Model Comparison Matrix

### By Cost (per 1M tokens)

```
Cheapest:
1. google_genai:gemini-2.5-flash-lite    ($0 - free tier)
2. openai:gpt-4o-mini                    ($0.75)
3. anthropic:claude-3-5-haiku-latest     ($4.80)
4. google_genai:gemini-2.5-flash         ($10.50)
5. openai:gpt-4o                         ($20)
```

### By Speed (latency)

```
Fastest:
1. google_genai:gemini-2.5-flash-lite    (200-400ms)
2. google_genai:gemini-2.5-flash         (200-400ms)
3. openai:gpt-4o-mini                    (300-600ms)
4. anthropic:claude-3-5-haiku-latest     (400-800ms)
5. anthropic:claude-3-opus-latest        (800-1200ms)
```

### By Quality (reasoning)

```
Best Quality:
1. anthropic:claude-3-opus-latest        (98%)
2. anthropic:claude-3-5-sonnet-latest    (97%)
3. openai:gpt-4o                         (96%)
4. openai:gpt-4o-mini                    (94%)
5. google_genai:gemini-1.5-pro           (93%)
```

---

## ⚠️ Common Mistakes

### ❌ Wrong Format

```python
# Wrong - missing provider
model = init_chat_model("gpt-4o-mini")

# Wrong - wrong separator
model = init_chat_model("openai/gpt-4o-mini")

# Wrong - typo in provider
model = init_chat_model("openai:gpt-4o-mini")  # ✅ Correct
```

### ❌ Wrong Environment Variable

```env
# Wrong - using API key variable
MODEL_PROVIDER=sk-proj-your-key-here

# Correct - using model name
MODEL_PROVIDER=openai:gpt-4o-mini
```

### ❌ Missing API Key

```python
# This will fail if OPENAI_API_KEY not set
model = init_chat_model("openai:gpt-4o-mini")

# Make sure .env has:
# OPENAI_API_KEY=sk-proj-your-key-here
```

---

## ✅ Verification Checklist

Before using a model:

- [ ] Model name follows format: `provider:model-identifier`
- [ ] Provider is one of: `anthropic`, `openai`, `google_genai`
- [ ] Model identifier is spelled correctly
- [ ] Required package is installed (`uv add langchain-openai`, etc.)
- [ ] API key is set in `.env` file
- [ ] API key environment variable matches provider:
  - Anthropic → `ANTHROPIC_API_KEY`
  - OpenAI → `OPENAI_API_KEY`
  - Google → `GOOGLE_API_KEY`

---

## 🔗 Resources

- [LangChain Model Docs](https://docs.langchain.com/oss/python/langchain/models)
- [Anthropic Models](https://docs.anthropic.com/en/docs/about-claude/models/overview)
- [OpenAI Models](https://platform.openai.com/docs/models)
- [Google Gemini Models](https://ai.google.dev/models)

---

## 📝 Quick Copy-Paste Examples

### Development
```env
MODEL_PROVIDER=google_genai:gemini-2.5-flash-lite
GOOGLE_API_KEY=your-key-here
```

### Production (Recommended)
```env
MODEL_PROVIDER=openai:gpt-4o-mini
OPENAI_API_KEY=sk-proj-your-key-here
```

### High Quality
```env
MODEL_PROVIDER=anthropic:claude-3-5-sonnet-latest
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

**Last Updated**: October 2024  
**Version**: 1.0
