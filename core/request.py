"""Request class for agent inputs."""

from typing import Any, Dict, Optional
import langfun as lf
import pyglove as pg

class Request(pg.Object):
    """Container for agent execution request."""
    
    goal: str = pg.Field(
        str, str,
        description="Natural language goal to accomplish"
    )
    context: Dict[str, Any] = pg.Field(
        Dict[str, Any], Dict[str, Any],
        default={},
        description="Additional context for execution"
    )
    metadata: Dict[str, Any] = pg.Field(
        Dict[str, Any], Dict[str, Any],
        default={},
        description="Additional metadata about the request"
    )

    @classmethod
    def from_text(cls, text: str, lm: lf.LanguageModel) -> 'Request':
        """Creates a structured Request from raw text using LLM.
        
        Args:
            text: Raw input text to parse
            lm: Language model to use for parsing
            
        Returns:
            Structured Request object
        """
        prompt = """
        Respond with a structured object matching this schema:
        {
            "goal": str,      # Primary objective
            "context": Dict[str, Any],  # Additional parameters
            "metadata": Dict[str, Any]  # Additional metadata
        }
        """.strip()
        
        return lf.query(
            prompt,
            cls,
            lm=lm,
            request=text
        ) 