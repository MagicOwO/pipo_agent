import pyglove as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..naive_demo import StepResult

class Action(pg.Object):
    """Base class for all actions an agent can perform."""
    description = "No description provided."
    estimated_duration_seconds = 1.0

    def __call__(self, answer: str, past_steps: list['StepResult'], *args, **kwargs):
        """Executes the action."""
        raise NotImplementedError()

    def get_description_for_llm(self) -> str:
        """Returns a description suitable for the LLM planner."""
        # Example: "GoogleSearch(query: str) - Performs a Google search. Estimated time: 2.0s"
        # This might need refinement based on how pg.Object serializes.
        # We might need to inspect the signature of the specific action subclass.
        # For now, let's keep it simple.
        return f"{self.__class__.__name__} - {self.description}" 