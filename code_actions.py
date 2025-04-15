"""Code-focused actions for the PIPO (Program In Program Out) framework."""

from typing import List, Optional, Dict
import ast
import textwrap

import langfun as lf
import pyglove as pg

from core.action import Action, register_action

@register_action()
class ParseCode(Action):
    """Parse and analyze input code."""
    
    code: str = pg.field(description="Source code to parse")
    analysis_type: str = pg.field(
        default="basic",
        description="Type of analysis to perform (basic, detailed, security)"
    )
    
    def execute(self, **kwargs) -> Dict:
        """Parse and analyze the code.
        
        Returns:
            Dict containing analysis results:
            - ast: AST representation
            - imports: List of imports
            - functions: List of function definitions
            - classes: List of class definitions
            - complexity: Code complexity metrics
        """
        tree = ast.parse(self.code)
        
        # Basic analysis
        analysis = {
            "imports": [],
            "functions": [],
            "classes": [],
            "complexity": {
                "lines": len(self.code.splitlines()),
                "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            }
        }
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    analysis["imports"].append(name.name)
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    analysis["imports"].append(f"{node.module}.{name.name}")
                    
        # Extract function and class names
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append(node.name)
                
        return analysis

@register_action()
class TransformCode(Action):
    """Transform input code according to specified rules."""
    
    code: str = pg.field(description="Source code to transform")
    transformation_type: str = pg.field(
        description="Type of transformation to apply"
    )
    parameters: Dict = pg.field(
        default={},
        description="Parameters for the transformation"
    )
    
    def execute(self, **kwargs) -> str:
        """Transform the code using LLM.
        
        Returns:
            Transformed code as string.
        """
        prompt = """
        Transform the following code according to these rules:
        Type: {{transformation_type}}
        Parameters: {{parameters}}
        
        Original Code:
        ```python
        {{code}}
        ```
        
        Return only the transformed code, maintaining correct Python syntax.
        """.strip()
        
        return lf.query(
            prompt,
            str,
            lm=kwargs.get('lm'),
            code=self.code,
            transformation_type=self.transformation_type,
            parameters=self.parameters
        )

@register_action()
class GenerateTests(Action):
    """Generate unit tests for input code."""
    
    code: str = pg.field(description="Source code to generate tests for")
    test_framework: str = pg.field(
        default="pytest",
        description="Test framework to use"
    )
    coverage_targets: List[str] = pg.field(
        default=["functions", "classes"],
        description="What to generate tests for"
    )
    
    def execute(self, **kwargs) -> str:
        """Generate unit tests using LLM.
        
        Returns:
            Generated test code as string.
        """
        prompt = """
        Generate {{test_framework}} tests for the following code.
        Generate tests for: {{coverage_targets}}
        
        Code to test:
        ```python
        {{code}}
        ```
        
        Return only the test code, following {{test_framework}} conventions.
        Include necessary imports and test class/function structure.
        """.strip()
        
        return lf.query(
            prompt,
            str,
            lm=kwargs.get('lm'),
            code=self.code,
            test_framework=self.test_framework,
            coverage_targets=self.coverage_targets
        )

@register_action()
class OptimizeCode(Action):
    """Optimize input code for better performance or readability."""
    
    code: str = pg.field(description="Source code to optimize")
    optimization_goals: List[str] = pg.field(
        default=["performance", "readability"],
        description="Optimization objectives"
    )
    constraints: Dict[str, Any] = pg.field(
        default={},
        description="Optimization constraints"
    )
    
    def execute(self, **kwargs) -> Dict[str, str]:
        """Optimize code using LLM.
        
        Returns:
            Dict containing:
            - optimized_code: The optimized code
            - changes: Description of optimizations made
            - metrics: Metrics about the optimization
        """
        prompt = """
        Optimize the following code for {{optimization_goals}}.
        Apply these constraints: {{constraints}}
        
        Original Code:
        ```python
        {{code}}
        ```
        
        Return a JSON object with:
        - optimized_code: The optimized code
        - changes: List of changes made
        - metrics: Relevant metrics
        """.strip()
        
        return lf.query(
            prompt,
            Dict[str, str],
            lm=kwargs.get('lm'),
            code=self.code,
            optimization_goals=self.optimization_goals,
            constraints=self.constraints
        )

@register_action()
class GenerateDocumentation(Action):
    """Generate documentation for input code."""
    
    code: str = pg.field(description="Source code to document")
    doc_format: str = pg.field(
        default="google",
        description="Documentation style (google, numpy, sphinx)"
    )
    doc_sections: List[str] = pg.field(
        default=["module", "classes", "functions"],
        description="Sections to document"
    )
    
    def execute(self, **kwargs) -> str:
        """Generate documentation using LLM.
        
        Returns:
            Generated documentation as string.
        """
        prompt = """
        Generate {{doc_format}} style documentation for this code.
        Include documentation for: {{doc_sections}}
        
        Code to document:
        ```python
        {{code}}
        ```
        
        Return the code with added documentation comments.
        Follow {{doc_format}} style guidelines strictly.
        """.strip()
        
        return lf.query(
            prompt,
            str,
            lm=kwargs.get('lm'),
            code=self.code,
            doc_format=self.doc_format,
            doc_sections=self.doc_sections
        ) 