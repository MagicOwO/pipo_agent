"""Result class for representing execution results."""

from typing import Any, Dict, Optional, Union

import pyglove as pg
import langfun as lf

@pg.members([
    ('summary', pg.typing.Union([pg.typing.Str(), 'Dict[str, Any]']), 'Summary of the execution result', {'default': {}}),
    ('raw_outputs', 'Dict[str, Any]', 'Raw outputs from each step', {'default': {}}),
    ('error', pg.typing.Union([pg.typing.Str(), type(None)]), 'Error message if execution failed', {'default': None}),
    ('metadata', 'Dict[str, Any]', 'Additional metadata about the execution', {'default': {}}),
])
class Result(pg.Object):
    """Result of executing a plan."""

    @property
    def success(self) -> bool:
        """Returns whether the execution was successful."""
        return self.error is None

    def __str__(self) -> str:
        """Returns a string representation of the result."""
        if not self.success:
            return f"Error: {self.error}"
        
        summary_str = ""
        if isinstance(self.summary, str):
            summary_str = self.summary
        elif isinstance(self.summary, dict):
            summary_str = ", ".join(f'{k}: {v}' for k, v in self.summary.items())
        else:
            summary_str = str(self.summary)
            
        return f"Success: {summary_str}"

    def to_text(self) -> str:
        """Returns a detailed natural language description of the results.
        
        (Currently returns a simple formatted string. Could be enhanced with lf.query).
        """
        if not self.success:
            return f"Execution failed: {self.error}"
            
        lines = ["Execution completed successfully."]
        
        # Format Summary
        lines.append("\nSummary:")
        if isinstance(self.summary, str):
            lines.append(f"  {self.summary}")
        elif isinstance(self.summary, dict):
            for key, value in self.summary.items():
                lines.append(f"  - {key}: {value}")
        else:
             lines.append(f"  {str(self.summary)}")
                
        # Format Raw Outputs (Optional - can be verbose)
        if self.raw_outputs:
            lines.append("\nRaw Step Outputs:")
            for key, value in self.raw_outputs.items():
                 # Basic representation, could be improved
                lines.append(f"  - {key}: {str(value)[:100]}...") 

        # Format Metadata
        if self.metadata:
            lines.append("\nMetadata:")
            for key, value in self.metadata.items():
                lines.append(f"  - {key}: {value}")
                
        return "\n".join(lines)
        
    # Potential future enhancement using Langfun for summarization:
    # def summarize_with_llm(self, lm: lf.LanguageModel | None = None) -> str:
    #     lm = lm or lf.get_lm()
    #     prompt = (
    #         f"Summarize the following execution result:\n"
    #         f"Success: {self.success}\n"
    #         f"Summary Data: {self.summary}\n"
    #         f"Error: {self.error}\n"
    #         # Consider adding excerpts from raw_outputs if needed
    #     )
    #     return lf.query(prompt, lm=lm) 