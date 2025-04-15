@echo off
REM Script to set up PIPO agent environment

echo.
echo === Setting up PIPO Agent Environment ===
echo.

REM Create and activate virtual environment
echo Setting up Python virtual environment...
if not exist .venv (
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install initial requirements
echo.
echo Installing initial requirements...
pip install python-dotenv

REM Install project dependencies
echo.
echo Installing project dependencies...
pip install -e .

REM Install Windows-specific dependencies
echo.
echo Installing Windows-specific dependencies...
pip install python-magic-bin

REM Create .env file if it doesn't exist
if not exist .env (
    echo.
    echo Creating .env file...
    echo OPENAI_API_KEY=your_openai_api_key_here > .env
    echo Created .env file. Please edit it with your actual OpenAI API key.
)

echo.
echo === Setup Complete! ===
echo.
echo Next steps:
echo 1. Edit the .env file with your OpenAI API key
echo 2. Run examples using: python run.py [code^|research]
echo.

REM Deactivate virtual environment
call .venv\Scripts\deactivate.bat 