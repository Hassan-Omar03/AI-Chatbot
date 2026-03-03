#!/bin/bash
# Start Local AI Backend System
# This script starts both Ollama and the FastAPI backend

set -e

echo "================================"
echo "Local AI Backend - Startup Script"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Warning: Ollama is not installed or not in PATH${NC}"
    echo "Please install Ollama from: https://ollama.ai"
    echo ""
    read -p "Continue without Ollama? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Ollama found${NC}"
fi

# Create data directory
echo "Creating data directory..."
mkdir -p data

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
if pip install -q -r requirements.txt; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}Error: Failed to install dependencies${NC}"
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "Creating .env file..."
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ .env created (using defaults)${NC}"
fi

# Start Ollama in background (if available)
if command -v ollama &> /dev/null; then
    echo ""
    echo "Starting Ollama server..."
    
    # Check if ollama is already running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama already running${NC}"
    else
        # Try to start Ollama
        ollama serve > /dev/null 2>&1 &
        OLLAMA_PID=$!
        
        # Wait for Ollama to start
        echo "Waiting for Ollama to start..."
        for i in {1..30}; do
            if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                echo -e "${GREEN}✓ Ollama started (PID: $OLLAMA_PID)${NC}"
                break
            fi
            sleep 1
        done
    fi
fi

# Start FastAPI backend
echo ""
echo "Starting FastAPI backend..."
cd backend
python main.py
