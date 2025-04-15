"""Example actions for research task."""

from typing import Dict, List, Optional

import langfun as lf
import pyglove as pg

from core.action import Action

@pg.members([
    ('query', pg.typing.Str(), 'Search query'),
    ('num_results', pg.typing.Int(), 'Number of results to return', 5),
])
class WebSearch(Action):
    """Action to perform web search."""
    
    def run(self, lm: lf.LanguageModel) -> List[Dict[str, str]]:
        """Simulates web search by returning fake results."""
        return [
            {
                'title': 'Example Result 1',
                'url': 'https://example.com/1',
                'snippet': 'This is an example search result.'
            },
            {
                'title': 'Example Result 2', 
                'url': 'https://example.com/2',
                'snippet': 'Another example search result.'
            }
        ]

@pg.members([
    ('url', pg.typing.Str(), 'URL to fetch content from'),
])
class FetchWebContent(Action):
    """Action to fetch web content."""
    
    def run(self, lm: lf.LanguageModel) -> str:
        """Simulates fetching web content by returning fake content."""
        return "This is example web content that would be fetched from the URL."

@pg.members([
    ('text', pg.typing.Str(), 'Text to extract entities from'),
])
class ExtractEntities(Action):
    """Action to extract named entities."""
    
    def run(self, lm: lf.LanguageModel) -> List[Dict[str, str]]:
        """Simulates entity extraction by returning fake entities."""
        return [
            {'type': 'PERSON', 'text': 'John Smith'},
            {'type': 'ORG', 'text': 'Acme Corp'},
            {'type': 'LOC', 'text': 'New York'}
        ]

@pg.members([
    ('entities', pg.typing.List(pg.typing.Dict([pg.typing.Str(), pg.typing.Str()])), 'Entities to include in report'),
    ('style', pg.typing.Str(), 'Report style (formal/casual)', 'formal'),
])
class GenerateReport(Action):
    """Action to generate a report from entities."""
    
    def run(self, lm: lf.LanguageModel) -> str:
        """Simulates report generation by returning fake report."""
        return "This is an example report summarizing the extracted entities." 