#!/bin/bash
# Script to remove sensitive commit from Git history

echo "🔧 Fixing Git history to remove flagged commit..."

# 1. Reset to the commit BEFORE the problematic one
echo "Step 1: Finding problematic commit..."
git log --oneline | head -10

echo ""
echo "Step 2: Soft reset to remove the commit (but keep changes)..."
# This removes the commit but keeps your changes
git reset --soft HEAD~1

echo ""
echo "Step 3: Re-committing with sanitized files..."
# Now re-commit with the current (sanitized) versions
git add .
git commit -m "feat: Add deployment documentation and updated dependencies

- Updated requirements.txt with edge-tts for blog TTS
- Added deployment guides for PythonAnywhere
- Updated demo bot to use Botpress shareable link
- Added Botpress widget with custom CTA
- Updated FAQ with comprehensive Q&A"

echo ""
echo "Step 4: Force push to GitHub..."
git push origin main --force

echo ""
echo "✅ Done! The problematic commit has been removed from history."
echo "Your changes are preserved and re-committed without the flagged content."

