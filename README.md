# PIPO Agent

PIPO (Program In Program Out) is a modular and extensible AI agent framework built with Langfun. It enables the creation of AI agents that can:

- Take programs/code as input and produce programs/code as output
- Understand natural language requests
- Generate and validate execution plans
- Execute complex workflows using reusable actions
- Provide structured results

## Quick Start

Follow these steps to get started with PIPO Agent:

### 1. First-time Setup

Run the appropriate setup script for your platform:

```bash
# On Linux/macOS:
chmod +x setup_env.sh
./setup_env.sh

# On Windows:
./setup_env.bat
```

After running the setup script:
1. Open the `.env` file that was created
2. Replace the placeholder with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-actual-key-here
   ```

### 2. Running Examples

Each time you want to run the examples:

1. First, activate the virtual environment:
   ```bash
   # On Linux/macOS:
   source .venv/bin/activate
   
   # On Windows:
   .\.venv\Scripts\activate
   ```

2. Then run one of the examples:
   ```bash
   python run.py code     # Run code transformation example
   # or
   python run.py research # Run research task example
   ```

3. When you're finished, deactivate the virtual environment:
   ```bash
   deactivate
   ```

### Troubleshooting

If you encounter an error related to `libmagic` or `python-magic` on Windows, you can manually install it:

```bash
pip install python-magic-bin
```

This is needed because Langfun's full installation depends on libraries that require additional setup on Windows systems.

## Core Components

### Actions

Actions are the building blocks of PIPO agents. Each action is a Python class that inherits from `Action` and represents a discrete capability:

```python
from pipo_agent import Action, register_action

@register_action()
class WebSearch(Action):
    query: str = pg.field(description="Search query")
    
    def execute(self, **kwargs):
        # Implementation here
        pass
```

### Plans

Plans are structured representations of how to achieve a goal using available actions:

```python
from pipo_agent import Plan, PlanStep

plan = Plan(
    goal="Research recent AI developments",
    steps=[
        PlanStep(
            action=WebSearch(query="latest AI news"),
            description="Search for recent AI news",
            output_key="search_results"
        ),
        # More steps...
    ]
)
```

### Agent Usage

```python
import langfun as lf
from pipo_agent import Agent

# Initialize agent with language model
agent = Agent(lm=lf.llms.Gpt4(api_key="your-key"))

# Process a request
result = agent.process_request(
    "What AI products did Google launch in 2024?"
)

# Get results
print(result.summary)
print(result.to_text(agent.lm))
```

## Creating Custom Actions

1. Define a new action class inheriting from `Action`
2. Use `pg.field()` to define inputs
3. Implement the `execute()` method
4. Register using the `@register_action()` decorator

Example:

```python
@register_action()
class SummarizeText(Action):
    """Summarize text content."""
    
    text: str = pg.field(description="Text to summarize")
    max_length: int = pg.field(
        default=200,
        description="Maximum summary length"
    )
    
    def execute(self, **kwargs):
        # Implementation using LLM or other methods
        pass
```

## Contributing

Contributions are welcome! Please read our contributing guidelines for details.

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
