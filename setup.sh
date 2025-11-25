#!/bin/bash

# Quick Setup Script for RAAPID Python Automation Framework

echo "============================================"
echo "RAAPID Automation Framework Setup"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/4] Python detected"
python3 --version
echo ""

# Create virtual environment
echo "[2/4] Creating virtual environment..."
python3 -m venv venv
echo "Virtual environment created successfully"
echo ""

# Activate virtual environment and install dependencies
echo "[3/4] Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Dependencies installed successfully"
echo ""

# Install Playwright browsers
echo "[4/4] Installing Playwright browsers..."
playwright install chromium
echo "Playwright browsers installed successfully"
echo ""

echo "============================================"
echo "Setup completed successfully!"
echo "============================================"
echo ""
echo "To activate the virtual environment, run:"
echo "    source venv/bin/activate"
echo ""
echo "To run tests, use:"
echo "    pytest tests/"
echo ""
echo "For more information, see README.md"
echo ""

