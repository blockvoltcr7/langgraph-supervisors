#!/bin/bash

# Setup script for hierarchical teams pattern

echo "🔧 Setting up environment for Hierarchical Teams Pattern"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
    echo ""
    echo "Current configuration:"
    echo "---"
    grep -E "^(OPENAI_API_KEY|LANGSMITH)" .env || echo "No API keys configured"
    echo "---"
    echo ""
    read -p "Do you want to update it? (y/N): " update
    if [[ ! $update =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

# Copy from example
if [ ! -f ".env.example" ]; then
    echo "❌ Error: .env.example not found"
    exit 1
fi

cp .env.example .env
echo "✅ Created .env from .env.example"
echo ""

# Prompt for OpenAI API key
echo "📝 Please enter your OpenAI API key:"
echo "   (Get it from: https://platform.openai.com/api-keys)"
read -p "OPENAI_API_KEY: " openai_key

if [ -z "$openai_key" ]; then
    echo "❌ Error: OpenAI API key is required"
    exit 1
fi

# Update .env file
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/your_openai_api_key_here/$openai_key/" .env
else
    # Linux
    sed -i "s/your_openai_api_key_here/$openai_key/" .env
fi

echo "✅ OpenAI API key configured"
echo ""

# Optional: LangSmith
read -p "Do you want to enable LangSmith tracing? (y/N): " enable_langsmith

if [[ $enable_langsmith =~ ^[Yy]$ ]]; then
    echo "📝 Please enter your LangSmith API key:"
    echo "   (Get it from: https://smith.langchain.com)"
    read -p "LANGSMITH_API_KEY: " langsmith_key
    
    if [ -n "$langsmith_key" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/your_langsmith_api_key_here/$langsmith_key/" .env
            sed -i '' "s/LANGSMITH_TRACING=false/LANGSMITH_TRACING=true/" .env
        else
            sed -i "s/your_langsmith_api_key_here/$langsmith_key/" .env
            sed -i "s/LANGSMITH_TRACING=false/LANGSMITH_TRACING=true/" .env
        fi
        echo "✅ LangSmith tracing enabled"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source .venv/bin/activate"
echo "2. Run the demo: python main.py"
echo "3. Or start LangGraph server: langgraph dev"
echo ""
