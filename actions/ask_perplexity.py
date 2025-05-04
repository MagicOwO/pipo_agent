import pyglove as pg
from .base import Action
import os
import openai
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..naive_demo import StepResult

class AskPerplexity(Action):
    """Action to query the Perplexity AI service. Time consumption for this action is high."""
    query: str
    description = "Queries the Perplexity AI online model (e.g., llama-3-sonar-small-32k-online) to answer a question or retrieve up-to-date information."
    estimated_duration_seconds = 15.0 # Online models can take longer

    # Add model parameter if you want to easily switch between pplx models
    model = pg.typing.Str(default="llama-3-sonar-small-32k-online")

    def __call__(self, question: str, past_steps: list['StepResult'], *args, **kwargs):
        """Executes the Perplexity query using the pplx-api (openai v0.27.2 compatible)."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set.")

        # Configure openai for Perplexity API (v0.27.2 style)
        openai.api_key = api_key
        openai.api_base = "https://api.perplexity.ai"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant accessing up-to-date information. "
                    "Provide concise and accurate answers based on your online search capabilities."
                ),
            },
            {
                "role": "user",
                "content": self.query,
            },
        ]

        try:
            print(f"---> Calling Perplexity API (v0.27.2 style) for query: {self.query}")
            # Use openai.ChatCompletion.create (v0.27.2 style)
            response = openai.ChatCompletion.create(
                model=self.model, # Use the model attribute
                messages=messages,
            )
            # Extract the response content
            answer = response['choices'][0]['message']['content']
            print(f"---> Perplexity Response Received.")
            # Reset API base and key if other actions use default openai
            openai.api_base = "https://api.openai.com/v1" # Or your default
            openai.api_key = os.getenv("OPENAI_API_KEY")
            return answer
        except openai.error.APIConnectionError as e:
            # Reset API base and key even on error
            openai.api_base = "https://api.openai.com/v1"
            openai.api_key = os.getenv("OPENAI_API_KEY")
            return f"Perplexity API Connection Error: {e}"
        except openai.error.RateLimitError as e:
            openai.api_base = "https://api.openai.com/v1"
            openai.api_key = os.getenv("OPENAI_API_KEY")
            return f"Perplexity API Rate Limit Error: {e}"
        except openai.error.APIError as e: # Catch generic API errors
            openai.api_base = "https://api.openai.com/v1"
            openai.api_key = os.getenv("OPENAI_API_KEY")
            return f"Perplexity API Error: {e} (Status code: {e.http_status})"
        except Exception as e:
            # Reset API base and key for any other unexpected errors
            openai.api_base = "https://api.openai.com/v1"
            openai.api_key = os.getenv("OPENAI_API_KEY")
            return f"An unexpected error occurred while calling Perplexity API: {e}" 