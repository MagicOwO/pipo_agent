# PIPO Agent

PIPO (Program In Program Out) is a modular and extensible AI agent framework built with Langfun. It enables the creation of AI agents that can:

- Take programs/code as input and produce programs/code as output
- Understand natural language requests
- Generate and validate execution plans
- Execute complex workflows using reusable actions
- Provide structured results

## Installation

```bash
pip install -r requirements.txt
```

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
