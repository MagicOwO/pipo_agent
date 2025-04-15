"""Test script to understand PyGlove object creation."""

import inspect
import pyglove as pg

# Import action classes
from core.action import Action
from actions import WebSearch, FetchWebContent, ExtractEntities, GenerateReport

# Display registered actions
from core.action import get_registered_actions
actions = get_registered_actions()
print(f"Registered actions: {list(actions.keys())}")

# Try to create instances of each action
print("\nTrying to create action instances:")

for name, action_cls in actions.items():
    print(f"\nTesting {name}:")
    
    try:
        # Print field info
        print(f"  Fields:")
        for field_name in dir(action_cls):
            if field_name.startswith('_') or field_name.isupper():
                continue
            try:
                field = getattr(action_cls, field_name)
                print(f"    {field_name}: {type(field)}")
            except Exception as e:
                pass
                
        # Try to create with no params
        try:
            instance1 = action_cls()
            print(f"  Created with no params: {instance1}")
        except Exception as e:
            print(f"  Failed with no params: {e}")
        
        # Try with explicit empty values
        try:
            if name == 'WebSearch':
                instance2 = WebSearch(query="", num_results=5)
            elif name == 'FetchWebContent':
                instance2 = FetchWebContent(url="")
            elif name == 'ExtractEntities':
                instance2 = ExtractEntities(text="")
            elif name == 'GenerateReport':
                instance2 = GenerateReport(entities=[], style="formal")
            else:
                instance2 = action_cls()
            print(f"  Created with explicit values: {instance2}")
        except Exception as e:
            print(f"  Failed with explicit values: {e}")
            
    except Exception as e:
        print(f"  Error testing {name}: {e}")

# Test for PlanStep with WebSearch
print("\nTesting PlanStep with WebSearch:")
from core.plan import PlanStep

try:
    # Create WebSearch instance
    ws = WebSearch(query="test")
    
    # Create PlanStep with WebSearch
    step = PlanStep(
        action=ws,
        description="Test step",
        input_mapping={},
        output_key="test_output"
    )
    
    print(f"  Created PlanStep: {step}")
    print(f"  Action: {step.action}")
    print(f"  Description: {step.description}")
except Exception as e:
    print(f"  Failed to create PlanStep: {e}") 