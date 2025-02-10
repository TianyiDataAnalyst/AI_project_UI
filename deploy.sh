#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install pipdeptree
pip install --upgrade pip
pip install pipdeptree

# Visualize dependencies
pipdeptree

# Install dependencies with wheels
pip install --prefer-binary -r requirements.txt

# Build the project (if necessary)
# npm run build

# Deploy to Cloudflare
wrangler publish
