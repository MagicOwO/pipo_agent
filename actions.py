"""Example actions for research tasks."""

import json
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import langfun as lf
import pyglove as pg

from core.action import Action, register_action

@register_action()
class WebSearch(Action):
    """Search the web for information."""
    
    query: str = pg.field(description="Search query")
    num_results: int = pg.field(
        default=5,
        description="Number of results to return"
    )
    
    def execute(self, **kwargs) -> List[dict]:
        """Execute a web search.
        
        Returns:
            List of search results, each containing url, title, and snippet.
        """
        # This is a mock implementation
        # In practice, you would use a real search API
        return [
            {
                "url": "https://example.com/1",
                "title": f"Result for: {self.query} (1)",
                "snippet": "Example search result 1"
            },
            {
                "url": "https://example.com/2",
                "title": f"Result for: {self.query} (2)",
                "snippet": "Example search result 2"
            }
        ]

@register_action()
class FetchWebContent(Action):
    """Fetch and extract content from a webpage."""
    
    url: str = pg.field(description="URL to fetch content from")
    
    def execute(self, **kwargs) -> str:
        """Fetch and extract main content from URL.
        
        Returns:
            Extracted text content.
        """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

@register_action()
class ExtractEntities(Action):
    """Extract named entities from text."""
    
    text: str = pg.field(description="Text to extract entities from")
    entity_types: List[str] = pg.field(
        default=["PRODUCT", "COMPANY", "DATE"],
        description="Types of entities to extract"
    )
    
    def execute(self, **kwargs) -> List[dict]:
        """Extract entities using LLM.
        
        Returns:
            List of extracted entities with type and value.
        """
        prompt = """
        Extract {{entity_types}} from the following text.
        Return a list of objects with 'type' and 'value' fields.
        
        Text: {{text}}
        """.strip()
        
        return lf.query(
            prompt,
            List[dict],
            lm=kwargs.get('lm'),
            text=self.text,
            entity_types=self.entity_types
        )

@register_action()
class SummarizeText(Action):
    """Generate a concise summary of text content."""
    
    text: str = pg.field(description="Text to summarize")
    max_length: int = pg.field(
        default=200,
        description="Maximum summary length in words"
    )
    focus_points: Optional[List[str]] = pg.field(
        default=None,
        description="Specific points to focus on in summary"
    )
    
    def execute(self, **kwargs) -> str:
        """Generate summary using LLM.
        
        Returns:
            Generated summary text.
        """
        prompt = """
        Summarize the following text in {{max_length}} words or less.
        {% if focus_points %}
        Focus on these points: {{focus_points}}
        {% endif %}
        
        Text: {{text}}
        """.strip()
        
        return lf.query(
            prompt,
            str,
            lm=kwargs.get('lm'),
            text=self.text,
            max_length=self.max_length,
            focus_points=self.focus_points
        )

@register_action()
class GenerateReport(Action):
    """Generate a structured report from research findings."""
    
    title: str = pg.field(description="Report title")
    findings: List[dict] = pg.field(description="Research findings to include")
    sections: List[str] = pg.field(
        default=["Overview", "Key Findings", "Analysis", "Conclusion"],
        description="Report sections"
    )
    
    def execute(self, **kwargs) -> dict:
        """Generate report using LLM.
        
        Returns:
            Dict containing report sections and content.
        """
        prompt = """
        Generate a professional report with the following sections:
        {{sections}}
        
        Title: {{title}}
        
        Use these findings:
        {{findings}}
        
        Return a dictionary where keys are section names and values are section content.
        """.strip()
        
        return lf.query(
            prompt,
            dict,
            lm=kwargs.get('lm'),
            title=self.title,
            findings=self.findings,
            sections=self.sections
        ) 