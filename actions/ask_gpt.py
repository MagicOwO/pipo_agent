import langfun as lf
import os
from .base import Action
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..naive_demo import StepResult

class AskGPT(Action):
    """Action to query GPT for specific information. This action has medium time consumption and provides medium-detail responses."""
    query: str
    description = "Asks GPT a specific question to get information."
    estimated_duration_seconds = 5.0 # LLM calls take time

    def __call__(self, question: str, past_steps: list['StepResult']) -> str:
        """Uses GPT to answer the specific query based on the overall question and past steps."""
        # Contextualize the query if helpful
        # prompt = f"Regarding the main question \"{{main_question}}\", and considering the previous steps {{past_steps}}, please answer the following specific query: {{specific_query}}"

        # Simpler approach: Just ask the specific query directly
        prompt = "{{specific_query}}"

        response = lf.query(
            prompt,
            specific_query=self.query,
            # main_question=question, # Optional: include main question context
            # past_steps=past_steps, # Optional: include past steps context
            lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY")),
            response_type=str # Expect a string answer
        )
        return str(response) 