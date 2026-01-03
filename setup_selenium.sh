#!/bin/bash

echo "Setting up Selenium scraper for FBI articles..."

# Install required Python packages
echo "Installing Python packages..."
pip install selenium webdriver-manager pandas

# Check if Chrome is installed (required for ChromeDriver)
if command -v google-chrome &> /dev/null; then
    echo "✅ Google Chrome is already installed"
elif command -v google-chrome-stable &> /dev/null; then
    echo "✅ Google Chrome is already installed" 
else
    echo "❌ Google Chrome not found. Installing..."
    
    # For Ubuntu/Debian systems
    if command -v apt-get &> /dev/null; then
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    
    # For CentOS/RHEL/Fedora systems
    elif command -v yum &> /dev/null; then
        sudo yum install -y wget
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        sudo yum localinstall -y google-chrome-stable_current_x86_64.rpm
        rm google-chrome-stable_current_x86_64.rpm
    
    else
        echo "Please install Google Chrome manually from https://www.google.com/chrome/"
        echo "The scraper requires Chrome to work properly."
        exit 1
    fi
fi

echo "✅ Setup complete!"
echo ""
echo "To run the scraper:"
echo "python selenium_scraper.py"
echo ""
echo "Note: The script will automatically:"
echo "- Download and setup ChromeDriver"
echo "- Use stealth techniques to avoid bot detection"
echo "- Add human-like delays between requests"
echo "- Save results to a CSV file"