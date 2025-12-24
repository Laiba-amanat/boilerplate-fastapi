#!/bin/bash

# FastAPI Template Documentation Deployment Script

set -e

echo "🚀 FastAPI Template Documentation Deployment Script"
echo "================================="

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV not installed, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not installed, please install Git first"
    exit 1
fi

# Install documentation dependencies
echo "📦 Installing documentation dependencies..."
uv sync --group docs

# Build documentation
echo "🏗️  Building documentation..."
uv run mkdocs build

# Check build result
if [ -d "site" ]; then
    echo "✅ Documentation build successful!"
    echo "📁 Build files located at: site/"
else
    echo "❌ Documentation build failed"
    exit 1
fi

# Ask if deploy to GitHub Pages
read -p "🤔 Deploy to GitHub Pages? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Deploying to GitHub Pages..."
    uv run mkdocs gh-deploy
    echo "✅ Deployment completed!"
    echo "🌐 Access URL: https://$(git remote get-url origin | sed 's/.*github.com[:/]//' | sed 's/.git$//' | sed 's/\//./').github.io/$(basename $(git remote get-url origin) .git)/"
else
    echo "📋 Manual deployment options:"
    echo "   - Local preview: uv run mkdocs serve"
    echo "   - Build documentation: uv run mkdocs build"
    echo "   - Deploy to GitHub Pages: uv run mkdocs gh-deploy"
fi

# Show local preview information
echo ""
echo "📖 Local preview:"
echo "   uv run mkdocs serve"
echo "   Access URL: http://localhost:8000"
echo ""
echo "🎉 Documentation system setup completed!"
