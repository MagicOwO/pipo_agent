"""Example actions for research task."""

from typing import Dict, List, Optional

import langfun as lf
import pyglove as pg

from core.action import Action, register_action

@register_action()
@pg.members([
    ('query', pg.typing.Str(), 'Search query', {'default': ''}),
    ('num_results', pg.typing.Int(), 'Number of results to return', {'default': 5}),
])
class WebSearch(Action):
    """Action to perform web search."""
    
    def run(self, lm: lf.LanguageModel) -> List[Dict[str, str]]:
        """Simulates web search by returning fake results."""
        print(f"Searching for: {self.query}")
        return [
            {
                'title': f'Example Result 1 for {self.query}',
                'url': 'https://example.com/1',
                'snippet': f'This is an example search result for {self.query}.'
            },
            {
                'title': f'Example Result 2 for {self.query}', 
                'url': 'https://example.com/2',
                'snippet': f'Another example search result for {self.query}.'
            }
        ]

@register_action()
@pg.members([
    ('url', pg.typing.Str(), 'URL to fetch content from', {'default': ''}),
])
class FetchWebContent(Action):
    """Action to fetch web content."""
    
    def run(self, lm: lf.LanguageModel) -> str:
        """Simulates fetching web content by returning fake content."""
        print(f"Fetching content from: {self.url}")
        return f"This is example web content that would be fetched from the URL: {self.url}"

@register_action()
@pg.members([
    ('text', pg.typing.Str(), 'Text to extract entities from', {'default': ''}),
])
class ExtractEntities(Action):
    """Action to extract named entities."""
    
    def run(self, lm: lf.LanguageModel) -> List[Dict[str, str]]:
        """Simulates entity extraction by returning fake entities."""
        print(f"Extracting entities from text of length: {len(self.text)}")
        return [
            {'type': 'PERSON', 'text': 'John Smith'},
            {'type': 'ORG', 'text': 'Acme Corp'},
            {'type': 'LOC', 'text': 'New York'}
        ]

@register_action()
@pg.members([
    ('entities', pg.typing.List(pg.typing.Dict()), 'Entities to include in report', {'default': []}),
    ('style', pg.typing.Str(), 'Report style (formal/casual)', {'default': 'formal'}),
])
class GenerateReport(Action):
    """Action to generate a report from entities."""
    
    def run(self, lm: lf.LanguageModel) -> str:
        """Simulates report generation by returning fake report."""
        print(f"Generating {self.style} report with {len(self.entities)} entities")
        return f"This is an example {self.style} report summarizing {len(self.entities)} extracted entities." 