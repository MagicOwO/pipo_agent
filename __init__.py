"""PIPO (Program In Program Out) Agent.

A modular and extensible AI agent framework built with Langfun that takes programs
as input and produces programs as output, using structured object-oriented design.
"""

from core.action import Action, register_action
from core.agent import Agent
from core.plan import Plan, PlanStep
from core.request import UserRequest
from core.result import Result

from actions import (
    WebSearch,
    FetchWebContent,
    ExtractEntities,
    SummarizeText,
    GenerateReport
)

from code_actions import (
    ParseCode,
    TransformCode,
    GenerateTests,
    OptimizeCode,
    GenerateDocumentation
)

__version__ = "0.1.0"

__all__ = [
    # Core components
    'Action',
    'Agent',
    'Plan',
    'PlanStep',
    'Result',
    'UserRequest',
    'register_action',
    
    # Research actions
    'WebSearch',
    'FetchWebContent',
    'ExtractEntities',
    'SummarizeText',
    'GenerateReport',
    
    # Code actions
    'ParseCode',
    'TransformCode',
    'GenerateTests',
    'OptimizeCode',
    'GenerateDocumentation',
] 