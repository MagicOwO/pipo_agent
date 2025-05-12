import os
import sys
from typing import Any, Type
import pyglove as pg
import langfun as lf
import importlib
import pkgutil
import inspect # Import inspect
from actions.final_answer import FinalAnswer

# Import base Action
from actions.base import Action
# Removed specific action imports - they will be discovered

# --- Action Discovery ---
def find_action_classes() -> list[Type[Action]]:
    """Dynamically finds all Action subclasses in the 'actions' directory."""
    action_classes = []
    actions_module_path = os.path.join(os.path.dirname(__file__), 'actions')

    # Iterate through modules in the 'actions' package
    for (_, module_name, _) in pkgutil.iter_modules([actions_module_path]):
        # Skip base module and __init__
        if module_name == 'base' or module_name.startswith('__'):
            continue

        try:
            module = importlib.import_module(f"actions.{module_name}")
            # Iterate through members of the module
            for name, obj in inspect.getmembers(module):
                # Check if it's a class, subclass of Action, and not Action itself
                if inspect.isclass(obj) and issubclass(obj, Action) and obj is not Action:
                    action_classes.append(obj)
        except ImportError as e:
            print(f"Warning: Could not import module actions.{module_name}: {e}")

    # print(f"Discovered actions: {[cls.__name__ for cls in action_classes]}")
    return action_classes

# Discover actions on script start
AVAILABLE_ACTIONS: list[Type[Action]] = find_action_classes()
# Manually add FinalAnswer if it wasn't found dynamically (needed for isinstance checks & type hints)
if not any(issubclass(cls, FinalAnswer) for cls in AVAILABLE_ACTIONS):
    try:
        if FinalAnswer not in AVAILABLE_ACTIONS:
            AVAILABLE_ACTIONS.append(FinalAnswer)
        print("Warning: FinalAnswer action added manually.")
    except NameError: # FinalAnswer might not be imported if file missing
        print("ERROR: Could not import FinalAnswer action!")
        sys.exit("Critical action FinalAnswer is missing.")

# TODO: (P1) better organize the code.
class Step(pg.Object):
    summary: str
    thought: str
    action: Action

class StepResult(pg.Object):
    step: Step
    result: Any

class Plan(pg.Object):
    steps: list[Step]
    thought: str

def dynamic_solve(questions: str, max_steps: int = 10) -> tuple[str | None, list[StepResult]]:
    # TODO: (P1) implement the dynamic solve process.
    past_steps = []

    for _ in range(max_steps):
        next_step = lf.query(
            f"""Given the question: {{{question}}}
            Past steps: {{past_steps}}

            What is the next step (thought and action) that may get us closer to the solution?
            The action must be one of the available Action types. Use FinalAnswer when the answer is found.""",
            Step,
            question=questions,
            past_steps=past_steps,
            lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY"))
        )
        # Check if the action is FinalAnswer
        if isinstance(next_step.action, FinalAnswer):
            return next_step.action.final_answer, past_steps
        result = next_step.action()
        past_steps.append(StepResult(step=next_step, result=result))
    return None, past_steps

def static_solve(questions: str) -> str:
    current_plan = None
    user_feedback = ""

    # TODO: (P0) add resource constraints to the plan generation process.
    while True: # Loop for plan refinement
        if current_plan:
            prompt = f"""Given the question: {{{question}}}
            The previous plan was:
            {{{current_plan}}}
            The user provided the following feedback for modification: {user_feedback}
            Generate a revised plan (sequence of steps with thought and action) based on the feedback. Only use the available actions.
            The final step's action must be FinalAnswer."""
        else:
            prompt = f"""Given the question: {{{question}}}
            What is the plan (sequence of steps with thought and action) to solve the question? Only use the available actions.
            The final step's action must be FinalAnswer."""

        plan = lf.query(
            prompt,
            Plan,
            question=questions,
            current_plan=current_plan,
            lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY"))
        )

        print("\n" + "-"*20 + " Proposed Plan " + "-"*20)
        # Display the plan more clearly
        for i, step in enumerate(plan.steps):
            action_repr = repr(step.action)
            print(f"  Step {i}: Action: {action_repr}")
            print(f"    Thought: {step.thought}")
            print(f"    Estimated Duration: {step.action.estimated_duration_seconds:.1f}s")

        total_estimated_time = sum(step.action.estimated_duration_seconds for step in plan.steps)
        print(f"Total Estimated Time: {total_estimated_time:.1f} seconds")
        print("-"*55)

        # Ask for user feedback
        print("\nOptions: [Y]es (execute plan), [N]o (stop), or provide feedback to refine the plan:")
        user_input = input("> ").strip()

        if user_input.lower() in ['y', 'yes']:
            print("Plan approved by user. Executing...")
            current_plan = plan # Store the approved plan
            break # Exit refinement loop
        elif user_input.lower() in ['n', 'no']:
            print("Plan rejected by user.")
            return "Plan rejected."
        else:
            # Assume any other input is modification feedback
            # TODO: (P0) improve the reliability of the plan revision process.
            user_feedback = user_input
            current_plan = plan # Store the plan that will be modified
            print("Revising plan based on feedback...")
            # Loop continues to regenerate the plan

    # --- Plan Execution (using approved current_plan) ---
    if not current_plan:
        # Should not happen if loop exited normally, but safety check
        return "No plan was approved for execution."

    print("\n" + "-"*20 + " Executing Plan " + "-"*20)
    past_steps = []

    for i, step in enumerate(current_plan.steps):
        print(f"Executing Step {i}: Action: {type(step.action).__name__}, Thought: {step.thought}")
        try:
            result = step.action(question=questions, past_steps=past_steps)
            past_steps.append(StepResult(step=step, result=result))
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  Error executing action {type(step.action).__name__}: {e}")
            return f"Execution failed at step {i}."

    if isinstance(current_plan.steps[-1].action, FinalAnswer):
        return past_steps[-1].result
    else:
        return "Plan completed without providing a final answer."

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['dynamic', 'static']:
        raise ValueError(f"Invalid run type: {sys.argv}")
    question = "Introduce AI product relese from big tech companies in 2021?"
    run_type = sys.argv[1]
    if run_type == "dynamic":
        answer, past_steps = dynamic_solve(question)
        print(f"Answer: {answer}")
        for i, step in enumerate(past_steps):
            print(f"Step {i}: {step.step.action}, thought: {step.step.thought}")
    elif run_type == "static":
        answer = static_solve(question)
        print(f"Answer: {answer}")
    else:
        raise ValueError(f"Invalid run type: {run_type}")
