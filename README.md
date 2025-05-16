# AI Agent Planner Visualization

A Streamlit web application for visualizing AI agent planning and execution processes.

## Features

- **Two Planning Modes**:
  - **Static Planning**: Generates and executes a complete plan upfront
  - **Dynamic Planning**: Generates steps one at a time based on previous results

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd pipo_agent
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy the `env.example` file to `.env` and update it with your actual API key:
   ```
   # Windows
   copy env.example .env
   # Linux/Mac
   cp env.example .env
   ```
   
   Then edit the `.env` file and replace `your_openai_api_key_here` with your actual OpenAI API key.

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the provided URL (typically http://localhost:8501)

3. Type your question in the text area

4. Choose between Static Planning or Dynamic Planning

5. View the results in the interactive UI

## Project Structure

- `app.py`: The Streamlit web application
- `naive_demo.py`: Core planning and execution logic
- `.env`: Contains environment variables (not tracked in git)
- `env.example`: Template for the `.env` file
- `actions/`: Directory containing all available actions
  - `base.py`: Base Action class
  - `final_answer.py`: Action for generating the final answer
  - Other action implementations

## Requirements

- Python 3.8+
- Streamlit
- PyGlove
- LangFun
- OpenAI API key

## Environment Variables

The application reads the following environment variables from the `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key for calling LLM services

## Note

This application requires an OpenAI API key to function. Make sure you have a valid API key and sufficient credits in your OpenAI account. 