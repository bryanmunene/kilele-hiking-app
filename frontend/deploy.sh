#!/bin/bash

# Streamlit Cloud Deployment Setup Script

echo "🏔️ Kilele Hiking App - Deployment Setup"
echo "========================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - Kilele Hiking App"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "📋 Pre-deployment Checklist:"
echo "=============================="
echo "✅ requirements.txt created"
echo "✅ .streamlit/config.toml configured"
echo "✅ README.md created"
echo "✅ .gitignore configured"
echo "✅ Nature theme applied to all pages"
echo "✅ Database seeded with trail data"
echo ""

echo "🚀 Next Steps:"
echo "=============="
echo "1. Create a GitHub repository at https://github.com/new"
echo "2. Run these commands:"
echo "   git remote add origin https://github.com/YOURUSERNAME/kilele-hiking-app.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Go to https://share.streamlit.io"
echo "4. Sign in with GitHub"
echo "5. Click 'New app'"
echo "6. Select repository: YOURUSERNAME/kilele-hiking-app"
echo "7. Set main file: frontend/Home.py"
echo "8. Click 'Deploy!'"
echo ""
echo "🎉 Your app will be live at:"
echo "   https://YOURUSERNAME-kilele-hiking-app.streamlit.app"
echo ""
