"""Result class for structured representation of agent outputs."""

from typing import Any, Dict, List, Optional

import langfun as lf
import pyglove as pg

class Result(pg.Object):
    """Structured representation of agent execution results."""
    
    summary: str = pg.field(description="Natural language summary of the results")
    raw_outputs: Dict[str, Any] = pg.field(
        description="Raw outputs from each execution step"
    )
    error: Optional[str] = pg.field(
        default=None,
        description="Error message if execution failed"
    )
    metadata: Dict[str, Any] = pg.field(
        default={},
        description="Additional metadata about the execution"
    )
    
    def to_text(self, lm: lf.LanguageModel) -> str:
        """Generates a detailed natural language description of the results.
        
        Args:
            lm: Language model to use for text generation
            
        Returns:
            Formatted text description of results
        """
        if self.error:
            return f"Error: {self.error}"
            
        prompt = """
        Generate a detailed natural language description of these execution results.
        Focus on the key findings and insights, while maintaining a professional tone.
        
        Summary: {{summary}}
        
        Raw Outputs: {{outputs}}
        
        Additional Context: {{metadata}}
        """.strip()
        
        return lf.query(
            prompt,
            str,
            lm=lm,
            summary=self.summary,
            outputs=self.raw_outputs,
            metadata=self.metadata
        ) 