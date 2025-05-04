import pyglove as pg
from .base import Action
import os
import openai
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..naive_demo import StepResult

class AskPerplexity(Action):
    """Action to query the Perplexity AI service."""
    query: str
    description = "Queries the Perplexity AI online model (llama-3-sonar-small-32k-online) to answer a question or retrieve up-to-date information."
    estimated_duration_seconds = 6.0 # Online models can take longer

    # Add model parameter if you want to easily switch between pplx models
    # model: str = pg.typing.Str(default="llama-3-sonar-small-32k-online")

    def __call__(self, question: str, past_steps: list['StepResult'], *args, **kwargs):
        """Executes the Perplexity query using the pplx-api."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set.")

        client = openai.OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

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
            print(f"---> Calling Perplexity API for query: {self.query}")
            response = client.chat.completions.create(
                # Consider making the model configurable via class attribute
                model="llama-3-sonar-small-32k-online",
                messages=messages,
            )
            # Extract the response content
            answer = response.choices[0].message.content
            print(f"---> Perplexity Response Received.")
            return answer
        except openai.APIConnectionError as e:
            return f"Perplexity API Connection Error: {e}"
        except openai.RateLimitError as e:
            return f"Perplexity API Rate Limit Error: {e}"
        except openai.APIStatusError as e:
            return f"Perplexity API Status Error: {e} (Status code: {e.status_code})"
        except Exception as e:
            # Catch any other unexpected errors
            return f"An unexpected error occurred while calling Perplexity API: {e}" 