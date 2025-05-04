import pyglove as pg
from .base import Action
import requests
import os
import openai
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..naive_demo import StepResult

class AskPerplexity(Action):
    """Action to query the Perplexity AI service. Time consumption for this action is high."""
    query: str
    description = "Queries the Perplexity AI online model (e.g., llama-3-sonar-large-32k-online) to answer a question or retrieve up-to-date information."
    estimated_duration_seconds = 15.0 # Online models can take longer

    # Add model parameter if you want to easily switch between pplx models
    model = "llama-3-sonar-large-32k-online"

    def __call__(self, question: str, past_steps: list['StepResult'], *args, **kwargs):
        """Executes the Perplexity query using the pplx-api (openai v0.27.2 compatible)."""
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
                {"role": "user", "content": self.query}
            ],
            "temperature": 0.2,
            "max_tokens": 100
        }

        # Make the POST request to the API
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data['choices'][0]['message']['content']