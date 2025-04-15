"""Base Action class and action registry for PIPO agent."""

import functools
from typing import Any, Callable, Dict, Type

import langfun as lf
import pyglove as pg

# Global registry for actions
_ACTION_REGISTRY: Dict[str, Type['Action']] = {}

def register_action(name: str = None) -> Callable:
    """Decorator to register an action class in the global registry.
    
    Args:
        name: Optional name for the action. If None, uses the class name.
    
    Returns:
        Decorator function that registers the action class.
    """
    def decorator(cls: Type['Action']) -> Type['Action']:
        action_name = name or cls.__name__
        if action_name in _ACTION_REGISTRY:
            raise ValueError(f"Action {action_name} already registered")
        _ACTION_REGISTRY[action_name] = cls
        return cls
    return decorator

def get_registered_actions() -> Dict[str, Type['Action']]:
    """Returns a copy of the action registry."""
    return _ACTION_REGISTRY.copy()

class Action(pg.Object):
    """Base class for all PIPO agent actions.
    
    Each action represents a discrete capability that can be executed
    as part of a plan. Actions must define their inputs as pg.Object fields
    and implement an execute method that returns a structured output.
    """
    
    def execute(self, **kwargs) -> Any:
        """Execute the action with the given inputs.
        
        Args:
            **kwargs: Additional execution context parameters.
            
        Returns:
            Action output (can be primitive type or pg.Object).
            
        Raises:
            NotImplementedError: If the action doesn't implement execute.
        """
        raise NotImplementedError("Action must implement execute method")
    
    @classmethod
    def get_description(cls) -> str:
        """Returns a description of the action for use in planning.
        
        The description includes the action's name, purpose, inputs,
        and outputs, derived from its class definition and docstring.
        """
        # Get docstring
        doc = cls.__doc__ or ""
        
        # Get input schema
        inputs = []
        for name, field in cls.get_fields().items():
            field_type = field.value_spec.__class__.__name__
            field_doc = field.description or ""
            inputs.append(f"- {name}: {field_type} - {field_doc}")
            
        input_desc = "\n".join(inputs) if inputs else "No inputs required"
        
        return f"""
Action: {cls.__name__}

Description:
{doc.strip()}

Inputs:
{input_desc}
        """.strip() 