from .base import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..naive_demo import StepResult

class GoogleSearch(Action):
    query: str
    description = "Performs a Google search to retrieve information related to the query."
    estimated_duration_seconds = 2.0

    def __call__(self, question: str, past_steps: list['StepResult']):
        # Mock implementation remains
        if 'Nvidia' in self.query:
            return 1000
        elif 'AMD' in self.query:
            return 100
        else:
            return 0 