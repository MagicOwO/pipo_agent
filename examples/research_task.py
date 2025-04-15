"""Example of using PIPO for research tasks."""

import os
from dotenv import load_dotenv
import langfun as lf

from core.agent import Agent
from actions import WebSearch, FetchWebContent, ExtractEntities, GenerateReport

# Load environment variables (for API keys)
load_dotenv()

def main():
    # Initialize language model (using GPT-4 as an example)
    lm = lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Initialize PIPO agent
    agent = Agent(lm=lm)
    
    # Example: Research recent AI developments
    print("Researching recent AI developments...")
    
    # Step 1: Initial research request
    result = agent.process_request(
        """Research and create a report about AI product launches by major tech 
        companies in 2024. Focus on:
        - Product names and launch dates
        - Key features and capabilities
        - Market reception and impact
        """
    )
    
    # Print initial findings
    print("Initial Research Results:")
    print(result.to_text(lm))
    print("\n" + "="*80 + "\n")
    
    # Step 2: Deep dive into specific product
    print("Deep diving into most significant product...")
    result = agent.process_request(
        """Based on the previous findings, identify the most significant AI product 
        launch and create a detailed analysis of its:
        - Technical architecture
        - Market positioning
        - Competition
        - Future potential
        """
    )
    
    # Print detailed analysis
    print("Detailed Analysis:")
    print(result.to_text(lm))

if __name__ == "__main__":
    main() 