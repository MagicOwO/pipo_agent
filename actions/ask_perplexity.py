import pyglove as pg
import langfun as lf
from .base import Action
import requests
import os
import openai
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..naive_demo import StepResult

class AskPerplexity(Action):
    """Action to query Perplexity for specific information. This action has high time consumption and provides highly detailed responses. Is able to search the web. Could get latest information."""
    query: str
    description = "Queries the Perplexity AI online model (e.g., llama-3-sonar-large-32k-online) to answer a question or retrieve up-to-date information."
    estimated_duration_seconds = 15.0 # Online models can take longer

    # Add model parameter if you want to easily switch between pplx models
    model = "llama-3-sonar-large-32k-online"

    def __call__(self, question: str, past_steps: list['StepResult'], *args, **kwargs):
        """Executes the Perplexity query."""
        # Retrospective behavior to contextualize the query.
        reflection_prompt = f"To best answer the question: {question}, and considering the results from the previous steps {past_steps}, please leveraging the previous results to rewrite the original query {self.query} to provide a more focused and accurate query. Notice that there might be placeholders in the original query, so please replace them with the actual values."
        reflection_response = lf.query(
            reflection_prompt,
            lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY")),
            response_type=str # Expect a string answer
        )
        print(f"reflection_response: {reflection_response}")

        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set.")

        url = "https://api.perplexity.ai/chat/completions"

        # Set up headers with the API key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Define the payload with model and messages
        payload = {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": "Be precise and concise."},
                {"role": "user", "content": reflection_response}
            ],
            "temperature": 0.2,
        }

        # Make the POST request to the API
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data['choices'][0]['message']['content']