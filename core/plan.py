"""Plan and PlanStep classes for representing execution plans."""

from typing import Any, Dict, List, Optional

import langfun as lf
import pyglove as pg

from .action import Action

class PlanStep(pg.Object):
    """A single step in an execution plan."""
    
    action: Action = pg.Field(
        type='Action',
        description="The action to execute"
    )
    description: str = pg.Field(
        type='str',
        description="Natural language description of this step"
    )
    input_mapping: Dict[str, str] = pg.Field(
        type='Dict[str, str]',
        default={},
        description="Mapping from previous step outputs to action inputs"
    )
    output_key: Optional[str] = pg.Field(
        type='Optional[str]',
        default=None,
        description="Key to store this step's output under"
    )

class Plan(pg.Object):
    """A structured execution plan composed of ordered steps."""
    
    goal: str = pg.Field(
        type='str',
        description="The original goal/request"
    )
    steps: List[PlanStep] = pg.Field(
        type='List[PlanStep]',
        description="Ordered list of execution steps"
    )
    
    def describe(self) -> str:
        """Returns a natural language description of the plan."""
        description = [f"Plan to achieve: {self.goal}\n"]
        for i, step in enumerate(self.steps, 1):
            description.append(f"Step {i}: {step.description}")
            if step.input_mapping:
                description.append("  Using:")
                for param, source in step.input_mapping.items():
                    description.append(f"  - {param} from {source}")
        return "\n".join(description)
    
    def validate(self) -> tuple[bool, str]:
        """Validates the plan for executability.
        
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        # Check if we have any steps
        if not self.steps:
            return False, "Plan has no steps"
            
        # Track available outputs for input mapping
        available_outputs = set()
        
        # Validate each step
        for i, step in enumerate(self.steps):
            # Validate input mappings
            for param, source in step.input_mapping.items():
                if source not in available_outputs:
                    return False, f"Step {i+1} requires output '{source}' which is not available"
                    
            # Add this step's output to available outputs if specified
            if step.output_key:
                available_outputs.add(step.output_key)
                
        return True, "" 