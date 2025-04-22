"""Main Agent class that orchestrates the workflow."""

from typing import Any, Dict, List, Optional, Type
import logging

import langfun as lf
import pyglove as pg

from core.action import Action, get_registered_actions
from core.plan import Plan, PlanStep
from core.request import Request
from core.result import Result

class Agent:
    """Main agent class that orchestrates the workflow."""
    
    def __init__(self, lm: lf.LanguageModel):
        """Initialize the agent.
        
        Args:
            lm: Language model to use for all LLM operations
        """
        self.lm = lm
        self._execution_context: Dict[str, Any] = {}
        
    def process_request(self, request: str) -> Result:
        """Process a natural language request.
        
        Args:
            request: Raw text request from user
            
        Returns:
            Structured Result object
        """
        try:
            print(f"Raw request: {request}")
            # Parse request into structured format
            structured_request = Request.from_text(request, self.lm)
            print(f"Structured request: {structured_request}")
            
            # Generate execution plan
            plan = self._generate_plan(structured_request)
            
            # Validate plan
            is_valid, error = plan.validate(lm=self.lm)
            if not is_valid:
                return Result(
                    summary="Plan validation failed",
                    raw_outputs={},
                    error=error,
                    metadata={"request": structured_request.goal}
                )
            
            # Execute plan
            return self._execute_plan(plan)
            
        except Exception as e:
            logging.exception("Error processing request")
            return Result(
                summary="Request processing failed",
                raw_outputs={},
                error=str(e),
                metadata={"request": request}
            )
            
    def _generate_plan(self, request: Request) -> Plan:
        """Generate an execution plan for the request.
        
        Args:
            request: Structured user request
            
        Returns:
            Execution plan
        """
        # Get all available actions with their descriptions
        actions = get_registered_actions()
        action_names = list(actions.keys())
        print(f"Available actions: {action_names}")
        
        action_descriptions = []
        for name, action_cls in actions.items():
            action_descriptions.append(action_cls.get_description())
            
        prompt = """
        Generate a plan to fulfill the following request using ONLY the available actions listed below.
        You MUST NOT include any actions that are not in the Available Actions list.
        
        Request Goal: {{request.goal}}
        Context: {{request.context}}
        
        Available Actions:
        {{action_descriptions}}
        
        VERY IMPORTANT: You can ONLY use these exact action names: {{action_names}}
        
        Respond with a Plan object with this schema:
        {
            "goal": str,  # Original goal
            "steps": [  # List of PlanStep objects
                {
                    "action": str,  # Action name (MUST be one of the available actions)
                    "description": str,  # Natural language description
                    "input_mapping": dict,  # Maps params to previous outputs
                    "output_key": str  # Key to store output (required)
                }
            ]
        }
        """.strip()
        
        # First get the plan as a dict to ensure proper parsing
        plan_dict = lf.query(
            prompt,
            dict,
            lm=self.lm,
            request=request,
            action_descriptions="\n\n".join(action_descriptions),
            action_names=", ".join(action_names)
        )
        
        # Convert action names to actual Action objects
        steps = []
        for step_dict in plan_dict["steps"]:
            action_name = step_dict["action"]
            if action_name not in actions:
                raise ValueError(f"Unknown action: {action_name}")
            
            # Create action instance based on its type
            action_cls = actions[action_name]
            
            if action_name == 'WebSearch':
                action = action_cls(query="", num_results=5)
            elif action_name == 'FetchWebContent':
                action = action_cls(url="")
            elif action_name == 'ExtractEntities':
                action = action_cls(text="")
            elif action_name == 'GenerateReport':
                action = action_cls(entities=[], style="formal")
            else:
                # Generic fallback (might not work for all actions)
                action_params = {}
                # Try to get required parameters from class properties
                for attr_name in dir(action_cls):
                    if attr_name.startswith('_') or attr_name.isupper() or not isinstance(getattr(action_cls, attr_name), property):
                        continue
                    # Provide empty default values
                    if isinstance(getattr(action_cls, attr_name), property):
                        # Set string parameters to empty string
                        action_params[attr_name] = ""
                action = action_cls(**action_params)
            
            step = PlanStep(
                action=action,
                description=step_dict["description"],
                input_mapping=step_dict["input_mapping"],
                output_key=step_dict["output_key"]
            )
            steps.append(step)
        
        return Plan(
            goal=plan_dict["goal"],
            steps=steps
        )
        
    def _execute_plan(self, plan: Plan) -> Result:
        """Execute a validated plan.
        
        Args:
            plan: Validated execution plan
            
        Returns:
            Execution results
        """
        outputs = {}
        self._execution_context = {}
        
        try:
            # Execute each step
            for i, step in enumerate(plan.steps):
                print(f"Executing step {i+1}: {step.description}")
                
                # Map inputs from previous outputs
                inputs = {}
                for param, source in step.input_mapping.items():
                    inputs[param] = self._execution_context[source]
                
                # Add language model to inputs
                inputs['lm'] = self.lm
                    
                # Execute action
                result = step.action.execute(**inputs)
                
                # Store output if key specified
                if step.output_key:
                    self._execution_context[step.output_key] = result
                    outputs[f"step_{i+1}"] = result
                    
            # Generate summary
            summary_prompt = """
            Summarize the results of executing this plan:
            
            Goal: {{plan.goal}}
            
            Outputs:
            {{outputs}}
            """.strip()
            
            summary = lf.query(
                summary_prompt,
                str,
                lm=self.lm,
                plan=plan,
                outputs=outputs
            )
            
            return Result(
                summary=summary,
                raw_outputs=outputs,
                error='',
                metadata={
                    "goal": plan.goal,
                    "num_steps": len(plan.steps)
                }
            )
            
        except Exception as e:
            logging.exception("Error executing plan")
            return Result(
                summary="Plan execution failed",
                raw_outputs=outputs,
                error=str(e),
                metadata={
                    "goal": plan.goal,
                    "completed_steps": len(outputs)
                }
            ) 