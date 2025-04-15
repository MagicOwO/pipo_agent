"""Main Agent class that orchestrates the workflow."""

from typing import Any, Dict, List, Optional, Type

import langfun as lf
import pyglove as pg

from core.action import Action, get_registered_actions
from core.plan import Plan, PlanStep
from core.request import UserRequest
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
            # Parse request into structured format
            user_request = UserRequest.from_text(request, self.lm)
            
            # Generate execution plan
            plan = self._generate_plan(user_request)
            
            # Validate plan
            is_valid, error = plan.validate()
            if not is_valid:
                return Result(
                    summary="Plan validation failed",
                    raw_outputs={},
                    error=error
                )
            
            # Execute plan
            return self._execute_plan(plan)
            
        except Exception as e:
            return Result(
                summary="Request processing failed",
                raw_outputs={},
                error=str(e)
            )
            
    def _generate_plan(self, request: UserRequest) -> Plan:
        """Generate an execution plan for the request.
        
        Args:
            request: Structured user request
            
        Returns:
            Execution plan
        """
        # Get descriptions of all available actions
        action_descriptions = []
        for name, action_cls in get_registered_actions().items():
            action_descriptions.append(action_cls.get_description())
            
        prompt = """
        Generate a plan to fulfill the following request using only the available actions.
        Each step must use a valid action and specify how its inputs map to previous outputs.
        
        Request Goal: {{request.goal}}
        Subtasks: {{request.subtasks}}
        Constraints: {{request.constraints}}
        
        Available Actions:
        {{action_descriptions}}
        
        Generate a Plan object with the following schema:
        {
            "goal": str,  # Original goal
            "steps": List[PlanStep]  # Where PlanStep has:
                - action: Action configuration
                - description: str  # Natural language description
                - input_mapping: dict  # Maps params to previous outputs
                - output_key: Optional[str]  # Key to store output
        }
        """.strip()
        
        return lf.query(
            prompt,
            Plan,
            lm=self.lm,
            request=request,
            action_descriptions="\n\n".join(action_descriptions)
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
                # Map inputs from previous outputs
                inputs = {}
                for param, source in step.input_mapping.items():
                    inputs[param] = self._execution_context[source]
                    
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
                metadata={
                    "goal": plan.goal,
                    "num_steps": len(plan.steps)
                }
            )
            
        except Exception as e:
            return Result(
                summary="Plan execution failed",
                raw_outputs=outputs,
                error=str(e)
            ) 