"""Core components of the PIPO (Program In Program Out) agent framework.

These components provide the foundation for creating agents that transform
input programs into output programs through structured object-oriented execution.
"""

from core.action import Action, register_action, get_registered_actions
from core.agent import Agent
from core.plan import Plan, PlanStep
from core.request import UserRequest
from core.result import Result

__all__ = [
    'Action',
    'Agent',
    'Plan',
    'PlanStep',
    'Result',
    'UserRequest',
    'register_action',
    'get_registered_actions',
] 