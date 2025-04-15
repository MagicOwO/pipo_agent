"""Example of using PIPO for code transformation tasks."""

import os
from dotenv import load_dotenv
import langfun as lf

from core.agent import Agent
from code_actions import ParseCode, TransformCode, GenerateTests, OptimizeCode

# Load environment variables (for API keys)
load_dotenv()

def main():
    # Initialize language model (using GPT-4 as an example)
    lm = lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Initialize PIPO agent
    agent = Agent(lm=lm)
    
    # Example input code
    input_code = """
    def calculate_fibonacci(n):
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        return fib
    
    # Example usage
    result = calculate_fibonacci(10)
    print(result)
    """
    
    # Display input code
    print("Input Code:")
    print(input_code)
    print("\n" + "="*80 + "\n")
    
    # Example 1: Analyze code
    print("1. Analyzing code structure...")
    result = agent.process_request(
        f"Analyze this code and tell me about its structure and complexity:\n{input_code}"
    )
    print(result.to_text(lm))
    print("\n" + "="*80 + "\n")
    
    # Example 2: Transform code to use generators
    print("2. Transforming code to use generators...")
    result = agent.process_request(
        f"Transform this code to use a generator pattern for memory efficiency:\n{input_code}"
    )
    print(result.to_text(lm))
    print("\n" + "="*80 + "\n")
    
    # Example 3: Generate tests
    print("3. Generating unit tests...")
    result = agent.process_request(
        f"Generate comprehensive pytest unit tests for this code:\n{input_code}"
    )
    print(result.to_text(lm))
    print("\n" + "="*80 + "\n")
    
    # Example 4: Optimize code
    print("4. Optimizing code...")
    result = agent.process_request(
        f"Optimize this code for better performance and add type hints:\n{input_code}"
    )
    print(result.to_text(lm))

if __name__ == "__main__":
    main() 