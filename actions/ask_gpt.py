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
        # Retrospective behavior to contextualize the query.
        reflection_prompt = f"To best answer the question: {question}, and considering the results from the previous steps {past_steps}, please leveraging the previous results to rewrite the original query {self.query} to provide a more focused and accurate query. Notice that there might be placeholders in the original query, so please replace them with the actual values."
        reflection_response = lf.query(
            reflection_prompt,
            lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY")),
            response_type=str # Expect a string answer
        )
        print(f"reflection_response: {reflection_response}")

        prompt = "{{specific_query}}"

        response = lf.query(
            prompt,
            specific_query=reflection_response,
            # main_question=question, # Optional: include main question context
            # past_steps=past_steps, # Optional: include past steps context
            lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY")),
            response_type=str # Expect a string answer
        )
        return str(response) 