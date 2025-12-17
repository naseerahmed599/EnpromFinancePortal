#!/bin/bash
# Quick script to clear Python cache files
# Use this if code changes aren't being picked up by Streamlit

echo "Clearing Python cache files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -r {} + 2>/dev/null || true
echo "✅ Cache cleared! Now restart Streamlit."
echo ""
echo "To restart Streamlit:"
echo "  1. Stop the current process (Ctrl+C)"
echo "  2. Run: streamlit run enprom_financial_app.py"

