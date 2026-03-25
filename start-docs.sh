#!/bin/bash
# KubeDojo - Documentation Server
# Starts MkDocs development server on port 8001

set -e

# Get script directory (project root)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📚 Starting KubeDojo Documentation Server..."
echo "📁 Project: $PROJECT_DIR"

# Change to project directory
cd "$PROJECT_DIR"

# Port to use
PORT=8001
LOG_FILE="/tmp/mkdocs-kubedojo.log"

# Check if port is in use
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use"
    echo "   Killing existing process..."
    lsof -ti:$PORT | xargs kill -9
    sleep 1
    echo "✅ Cleaned up port $PORT"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Creating virtual environment..."
    python3 -m venv .venv
    echo "   Installing dependencies..."
    source .venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found"
fi

# Start MkDocs server
echo "🚀 Starting MkDocs server on http://127.0.0.1:$PORT"
source .venv/bin/activate && NO_MKDOCS_2_WARNING=1 nohup mkdocs serve --dev-addr=127.0.0.1:$PORT --no-livereload --clean > "$LOG_FILE" 2>&1 &
MKDOCS_PID=$!
sleep 2

# Check if it started successfully
if ps -p $MKDOCS_PID > /dev/null 2>&1; then
    echo "✅ MkDocs server running (PID: $MKDOCS_PID)"
    echo "   📖 Documentation: http://127.0.0.1:$PORT"
    echo "   📝 Logs: $LOG_FILE"
    echo ""
    echo "To stop the server: kill $MKDOCS_PID"
    echo "Or use: lsof -ti:$PORT | xargs kill"
else
    echo "❌ MkDocs server failed to start"
    echo "   Check logs: $LOG_FILE"
    exit 1
fi
