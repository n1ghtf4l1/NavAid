#!/bin/bash
# start_backend.sh - Start the NavAid Python backend server

echo "🚀 Starting NavAid Backend Server..."
echo ""

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY environment variable not set!"
    echo "Please set it with: export GOOGLE_API_KEY='your-api-key'"
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Start server
echo "🌐 Starting Flask server on http://localhost:8000"
echo ""
export KMP_DUPLICATE_LIB_OK=TRUE
python backend_server.py
