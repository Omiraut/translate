#!/bin/bash

# Quick Start Script for Translation API

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       Translation API - Quick Start Setup                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
python --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║            Setup Complete!                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the API:"
echo "   python main.py"
echo ""
echo "3. In another terminal, run the demo:"
echo "   python demo.py"
echo ""
echo "4. Open in browser:"
echo "   http://localhost:8000/docs  (Swagger UI)"
echo ""
