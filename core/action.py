"""Base Action class and action registry for PIPO agent."""

import functools
import inspect 
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
        
        If a subclass implements a `run` method instead, this will call that.
        
        Args:
            **kwargs: Additional execution context parameters.
            
        Returns:
            Action output (can be primitive type or pg.Object).
            
        Raises:
            NotImplementedError: If the action doesn't implement execute or run method.
        """
        if hasattr(self, 'run') and callable(getattr(self, 'run')):
            # Check if lm is expected by the run method's signature
            sig = inspect.signature(self.run)
            
            # If run expects an lm parameter and none is provided, use a default
            if 'lm' in sig.parameters and 'lm' not in kwargs:
                # Default to a simple mock LM that just returns text
                class SimpleLM(lf.LanguageModel):
                    def __init__(self):
                        pass
                    
                    def generate(self, prompt, **kwargs):
                        return f"Mock response for: {prompt[:50]}..."
                
                print("Warning: No language model provided for action execution. Using a simple mock.")
                kwargs['lm'] = SimpleLM()
                
            # Filter kwargs to only include accepted parameters
            accepted_params = sig.parameters.keys()
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in accepted_params}
            
            print(f"Executing {self.__class__.__name__}.run with params: {filtered_kwargs.keys()}")
            
            # Create a dictionary of values to bind to the object
            binding_values = {}
            
            # For the specific parameter values defined on the class, check if any match
            # the input_mapping keys and update the class attributes via bind
            property_names = [name for name in dir(self.__class__) 
                             if isinstance(getattr(self.__class__, name), property)]
            
            for prop_name in property_names:
                # If we have a property with this name but no input param, see if any input key
                # might be referring to it
                if prop_name not in filtered_kwargs:
                    for input_key in kwargs.keys():
                        # Look for partial matches (e.g., "search_results" might match "results" property)
                        if input_key.endswith(prop_name) or input_key.startswith(prop_name):
                            print(f"  Mapping input '{input_key}' to property '{prop_name}'")
                            # Add to binding dictionary instead of using setattr
                            binding_values[prop_name] = kwargs[input_key]
            
            # Use pg.Object.bind to update the properties if we have any to bind
            if binding_values:
                try:
                    # Create a copy of the object with the new values
                    updated_action = pg.clone(self).rebind(**binding_values)
                    # Use the updated copy for executing the run method
                    return updated_action.run(**filtered_kwargs)
                except Exception as e:
                    print(f"Warning: Failed to bind properties: {e}")
                    # Fall back to original object if binding fails
            
            # Call the run method with filtered parameters
            return self.run(**filtered_kwargs)
        
        raise NotImplementedError("Action must implement execute or run method")
    
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
        
        # Check if the class defines MEMBERS (for pg.Object subclasses)
        members = getattr(cls, 'MEMBERS', {})
        
        for name, field in members.items():
            field_type = str(field.value_spec)
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