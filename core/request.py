"""UserRequest class for structured representation of user requests."""

from typing import List, Optional

import langfun as lf
import pyglove as pg

class UserRequest(pg.Object):
    """Structured representation of a user's request."""
    
    raw_text: str = pg.field(description="Original raw text of the request")
    goal: str = pg.field(description="Extracted primary goal/objective")
    subtasks: List[str] = pg.field(
        default=[],
        description="List of identified subtasks to achieve the goal"
    )
    constraints: List[str] = pg.field(
        default=[],
        description="List of identified constraints or requirements"
    )
    context: Optional[dict] = pg.field(
        default=None,
        description="Additional context or parameters extracted from the request"
    )
    
    @classmethod
    def from_text(cls, text: str, lm: lf.LanguageModel) -> 'UserRequest':
        """Creates a structured UserRequest from raw text using LLM.
        
        Args:
            text: Raw user request text
            lm: Language model to use for parsing
            
        Returns:
            Structured UserRequest object
        """
        prompt = """
        Parse the following user request into a structured format.
        Extract the main goal, any subtasks needed to achieve it,
        and any constraints or requirements mentioned.
        
        User Request: {{request}}
        
        Respond with a structured object matching this schema:
        {
            "raw_text": str,  # Original request text
            "goal": str,      # Primary objective
            "subtasks": List[str],  # Steps needed
            "constraints": List[str],  # Requirements/limitations
            "context": Optional[dict]  # Additional parameters
        }
        """.strip()
        
        return lf.query(
            prompt,
            cls,
            lm=lm,
            request=text
        ) 