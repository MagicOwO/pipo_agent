"""Result class for storing execution outputs."""

from typing import Any, Dict, List, Optional, Union

import langfun as lf
import pyglove as pg

class Result(pg.Object):
    """Container for execution results."""
    
    summary: str = pg.Field(
        Union[str, dict], Union[str, dict],
        description="Natural language summary of the results"
    )
    raw_outputs: Dict[str, Any] = pg.Field(
        Dict[str, Any], Dict[str, Any],
        default={},
        description="Raw outputs from each execution step"
    )
    error: Optional[str] = pg.Field(
        Optional[str], Optional[str],
        default=None,
        description="Error message if execution failed"
    )
    metadata: Dict[str, Any] = pg.Field(
        Dict[str, Any], Dict[str, Any],
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
            
        # Handle summary that might be a string or dict
        summary_text = self.summary
        if isinstance(self.summary, dict):
            summary_text = self.summary.get("summary", str(self.summary))
            
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
            summary=summary_text,
            outputs=self.raw_outputs,
            metadata=self.metadata
        ) 