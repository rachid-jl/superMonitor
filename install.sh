#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Make the main script executable
chmod +x system_monitor.py

echo "Installation complete! Run './system_monitor.py' to start monitoring."