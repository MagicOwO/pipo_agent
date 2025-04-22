
import os
import sys
from typing import Any
import pyglove as pg
import langfun as lf

class GoogleSearch(pg.Object):
    query: str

    def __call__(self):
        if 'Nvidia' in self.query:
            return 1000
        elif 'AMD' in self.query:
            return 100
        else:
            return 0

class FinalAnswer(pg.Object):
    final_answer: str

    def __call__(self):
        return self.final_answer

class Step(pg.Object):
    thought: str
    action: GoogleSearch | FinalAnswer

class StepResult(pg.Object):
    step: Step
    result: Any

class Plan(pg.Object):
    steps: list[Step]
    thought: str

def dynamic_solve(questions: str, max_steps: int = 10) -> tuple[str | None, list[StepResult]]:
    past_steps = []
    for _ in range(max_steps):
        next_step = lf.query(
            "Given the question: {{question}} and the past steps: {{past_steps}}, what is next step that may get us closer to the solution?",
            Step,
            question=questions,
            past_steps=past_steps,
            lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY"))
        )
        if isinstance(next_step.action, FinalAnswer):
            return next_step.action.final_answer, past_steps
        result = next_step.action()
        past_steps.append(StepResult(step=next_step, result=result))
    return None, past_steps

def static_solve(questions: str) -> str:
    # Draw a static plan before execution.
    plan = lf.query(
        "Given the question: {{question}}, what is the plan to solve the question?",
        Plan,
        question=questions,
        lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY"))
    )
    print(f"Plan: {plan}")
    # Execute the plan.
    past_steps = []
    for i, step in enumerate(plan.steps):
        if isinstance(step.action, FinalAnswer):
            result = lf.query(
                "Given the question: {{question}} and the past steps: {{past_steps}}, what is the final answer?",
                FinalAnswer,
                question=questions,
                past_steps=past_steps,
                lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY"))
            )
            return result.final_answer
        result = step.action()
        past_steps.append(StepResult(step=step, result=result))
        print(f"Step {i}: action: {type(step.action).__name__}, result: {result}, thought: {step.thought}")
    return "No answer found."

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['dynamic', 'static']:
        raise ValueError(f"Invalid run type: {sys.argv}")
    question = "Compare Nvidia and AMD whose market valuation is higher?"
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
