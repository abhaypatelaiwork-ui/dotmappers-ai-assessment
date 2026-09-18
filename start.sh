#!/bin/bash
set -e

# API background mein chalao
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# API ready hone ka wait karo (max 30 seconds)
echo "Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    echo "  Attempt $i/30..."
    sleep 1
done

# UI ko batao API kahan hai
export API_URL=http://localhost:8000

# Streamlit foreground mein chalao
echo "🚀 Starting Streamlit UI..."
streamlit run ui/streamlit_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true