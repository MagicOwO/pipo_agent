#!/bin/bash
# Script to set up PIPO agent environment

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Exit on error
set -e

# Function to display step messages
show_step() {
    echo -e "\n${BLUE}>>> $1${NC}"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Creating .env file. Please edit it with your API keys.${NC}"
        echo 'OPENAI_API_KEY=your_openai_api_key_here' > .env
        echo -e "${YELLOW}Please edit the .env file with your actual API key, then run this script again.${NC}"
        exit 1
    fi
    
    # Check if API key is still the placeholder
    if grep -q "your_openai_api_key_here" .env; then
        echo -e "${YELLOW}Please replace the placeholder API key in the .env file with your actual key, then run this script again.${NC}"
        exit 1
    fi
}

# Create and activate virtual environment
show_step "Setting up Python virtual environment"
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install initial requirements
show_step "Installing initial requirements"
pip install python-dotenv

# Install project dependencies
show_step "Installing project dependencies"
pip install -e .

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    show_step "Creating .env file"
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo -e "${YELLOW}Created .env file. Please edit it with your actual OpenAI API key.${NC}"
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit the .env file with your OpenAI API key"
echo "2. Run examples using: python run.py [code|research]"

# Main execution
main() {
    show_step "Welcome to PIPO Agent Setup"
    
    # Check if .env file exists and is configured
    check_env_file
    
    # Setup virtual environment and install dependencies
    setup_venv
    
    echo -e "\n${GREEN}Environment setup complete! You can now run examples using run_pipo.sh${NC}"
}

# Execute main function
main "$@" 