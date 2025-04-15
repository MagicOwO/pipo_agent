"""Plan and PlanStep classes for representing execution plans."""

from typing import Any, Dict, List, Optional, Tuple

import pyglove as pg
import langfun as lf

from .action import Action, get_registered_actions

@pg.members([
    ('action', pg.typing.Object('Action'), 'The action to execute', {}),
    ('description', pg.typing.Str(), 'Natural language description of this step', {}),
    ('input_mapping', pg.typing.Dict(), 'Mapping from previous step outputs to action inputs', {'default': {}}),
    ('output_key', pg.typing.Str(), 'Key to store this step\'s output under', {'default': ''}),
])
class PlanStep(pg.Object):
    """A single step in an execution plan."""

@pg.members([
    ('goal', pg.typing.Str(), 'The original goal/request', {}),
    ('steps', pg.typing.List(pg.typing.Object('PlanStep')), 'Ordered list of execution steps', {'default': []}),
])
class Plan(pg.Object):
    """A structured execution plan composed of ordered steps."""
    
    def describe(self, detailed: bool = False) -> str:
        """Returns a natural language description of the plan."""
        description = [f"Plan to achieve: {self.goal}\n"]
        for i, step in enumerate(self.steps, 1):
            action_name = step.action.__class__.__name__
            desc = f"Step {i}: {action_name} - {step.description}"
            if detailed:
                desc += f" (Action details: {step.action.to_dict()})"
            description.append(desc)
            if step.input_mapping:
                description.append("  Inputs mapped:")
                for param, source in step.input_mapping.items():
                    description.append(f"  - {param} from {source}")
            if step.output_key:
                 description.append(f"  Output stored as: {step.output_key}")
        return "\n".join(description)
    
    def validate(self, lm: lf.LanguageModel | None = None) -> Tuple[bool, str]:
        """Validates the plan for executability, including action existence and reasonableness.
        
        Args:
            lm: Language model for reasonableness check. Uses default if None.
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        registry = get_registered_actions()
        lm = lm or lf.get_lm()

        # 1. Check if we have any steps
        if not self.steps:
            return False, "Plan Validation Failed: Plan has no steps."
            
        available_outputs = set() 
        action_names = []
        
        # 2. Validate each step (Action Existence & Input Mapping)
        for i, step in enumerate(self.steps):
            action_cls_name = step.action.__class__.__name__
            action_names.append(action_cls_name)
            
            # 2a. Action Existence Check
            if action_cls_name not in registry:
                return False, f"Plan Validation Failed: Action '{action_cls_name}' in step {i+1} not found in the registry."
            
            # 2b. Validate input mappings against available outputs
            for param, source in step.input_mapping.items():
                if source not in available_outputs:
                    return False, f"Plan Validation Failed: Step {i+1} ('{action_cls_name}') requires input '{param}' from source '{source}', which is not available from previous steps."
                    
            # Add this step's output to available outputs if specified
            if step.output_key:
                if step.output_key in available_outputs:
                     return False, f"Plan Validation Failed: Output key '{step.output_key}' in step {i+1} ('{action_cls_name}') is already used by a previous step."
                available_outputs.add(step.output_key)

        # 3. Plan Reasonableness Check (LLM-based)
        plan_description = self.describe(detailed=False) # Get a concise description for the LLM
        prompt = (
            f"Given the goal: '{self.goal}'\n"
            f"And the sequence of actions: {', '.join(action_names)}\n"
            f"Is the following plan a reasonable and logical approach to achieve the goal?\n"
            f"Plan:\n{plan_description}\n\n"
            f"Respond with 'Yes' or 'No'. If 'No', briefly explain why it's unreasonable."
        )
        
        try:
            reasonableness_response = lf.query(prompt, lm=lm)
            if not reasonableness_response.lower().startswith('yes'):
                explanation = reasonableness_response.split('No', 1)[-1].strip().lstrip(',').lstrip('.').strip()
                error_msg = f"Plan Validation Failed: Plan deemed unreasonable by LLM. Reason: {explanation if explanation else 'No specific reason provided.'}"
                return False, error_msg
        except Exception as e:
            # Handle potential LLM call errors gracefully
            return False, f"Plan Validation Failed: Error during LLM reasonableness check: {e}"
                
        return True, "Plan validation successful." 