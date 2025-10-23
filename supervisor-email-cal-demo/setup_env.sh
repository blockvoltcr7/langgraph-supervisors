#!/bin/bash

# Setup script for Supervisor Multi-Agent Demo

echo "🚀 Setting up Supervisor Multi-Agent Demo..."
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "✅ .env file already exists"
else
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
    echo ""
    echo "Get your API key from: https://console.anthropic.com/"
    echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Run: python main.py"
echo "  3. Or run: python main_with_hitl.py (for human-in-the-loop demo)"
echo ""
