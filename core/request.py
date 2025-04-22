"""Request class for agent inputs."""

from typing import Any, Dict, Optional
import pyglove as pg
import langfun as lf

@pg.members([
    ('goal', pg.typing.Str(), 'Natural language goal to accomplish', {}),
    ('context', pg.typing.Dict(), 'Additional context for the request', {'default': {}}),
    ('metadata', pg.typing.Dict(), 'Additional metadata for the request', {'default': {}}),
])
class Request(pg.Object):
    """Container for agent execution request."""

    @classmethod
    def from_text(cls, text: str, lm: lf.LanguageModel | None = None) -> 'Request':
        """Creates a structured Request from raw text using LLM.
        
        Args:
            text: Raw input text to parse.
            lm: Language model to use for parsing. If None, the default LM is used.
            
        Returns:
            Structured Request object.
        """
        # Simple case: if the text is short and likely just the goal.
        # A more robust implementation might use LLM prompting for this too.
        if len(text.split()) < 100: # Heuristic threshold 
             return cls(goal=text, context={}, metadata={})

        # Use LLM to parse more complex text into the Request schema
        return lf.query(
            prompt=f"Parse the following user request into a structured Request object. Extract the main goal and any relevant context or metadata provided.\n\nUser Request: {text}",
            schema=cls,
            lm=lm or lf.get_lm() # Use provided LM or default
        ) 