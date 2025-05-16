import os
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import time
import re
import io
import sys
import builtins
from typing import Any, List, Dict, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import from naive_demo
from naive_demo import dynamic_solve, Plan, Step, StepResult, AVAILABLE_ACTIONS
import langfun as lf

# Set page config
st.set_page_config(
    page_title="AI Agent Planner",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .step-box {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
    }
    .thought-box {
        background-color: #e1f5fe;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .action-box {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .result-box {
        background-color: #fff3e0;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .header-box {
        background-color: #f1f1f1;
        padding: 5px 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .feedback-box {
        border: 1px solid #4caf50;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
        background-color: #f1f8e9;
    }
</style>
""", unsafe_allow_html=True)

# This function implements our own version of the static planning process
def generate_plan(question: str, feedback: str = "", current_plan: Optional[Plan] = None) -> Plan:
    """Generate a plan using the LLM, similar to static_solve but without execution."""
    if current_plan and feedback:
        prompt = f"""Given the question: {{{{question}}}}
        The previous plan was:
        {{{{current_plan}}}}
        The user provided the following feedback for modification: {feedback}
        Generate a revised plan (sequence of steps with thought and action) based on the feedback. Only use the available actions.
        The final step's action must be FinalAnswer."""
    else:
        prompt = """Given the question: {{question}}
        What is the plan (sequence of steps with thought and action) to solve the question? Feel free to use placeholders if it depends on results from previous steps. Only use the available actions.
        The final step's action must be FinalAnswer."""

    plan = lf.query(
        prompt,
        Plan,
        question=question,
        current_plan=current_plan,
        lm=lf.llms.Gpt4(api_key=os.getenv("OPENAI_API_KEY"))
    )
    
    return plan

# Function to execute a pre-approved plan
def execute_plan(question: str, plan: Plan) -> Tuple[str, List[StepResult]]:
    """Execute a pre-approved plan, similar to static_solve's execution phase."""
    past_steps = []

    for i, step in enumerate(plan.steps):
        try:
            result = step.action(question=question, past_steps=past_steps)
            past_steps.append(StepResult(step=step, result=result))
        except Exception as e:
            return f"Error executing step {i}: {e}", past_steps

    # Get the final answer
    if past_steps and hasattr(past_steps[-1].result, "strip"):
        return past_steps[-1].result, past_steps
    
    return "Execution completed but no final answer was found.", past_steps

# Calculate total estimated duration
def calculate_plan_duration(plan: Plan) -> float:
    """Calculate the total estimated duration for a plan."""
    return sum(step.action.estimated_duration_seconds for step in plan.steps)

# Function to display a plan in the UI
def display_plan(container, plan: Plan):
    """Display a plan in the Streamlit UI."""
    with container:
        total_duration = calculate_plan_duration(plan)
        st.info(f"**Total Estimated Duration:** {total_duration:.1f} seconds")
        
        for i, step in enumerate(plan.steps):
            st.markdown(f"""
            <div class="step-box">
                <h4>Step {i}</h4>
                <div class="action-box">
                    <strong>Action:</strong> {repr(step.action)}
                </div>
                <div class="thought-box">
                    <strong>Thought:</strong> {step.thought}
                </div>
                <p><strong>Est. Duration:</strong> {step.action.estimated_duration_seconds:.1f}s</p>
            </div>
            """, unsafe_allow_html=True)

# Function to display execution results
def display_execution(container, steps: List[StepResult]):
    """Display execution results in the Streamlit UI."""
    with container:
        for i, step_result in enumerate(steps):
            st.markdown(f"""
            <div class="step-box">
                <h4>Execution Step {i}</h4>
                <div class="action-box">
                    <strong>Action:</strong> {repr(step_result.step.action)}
                </div>
                <div class="thought-box">
                    <strong>Thought:</strong> {step_result.step.thought}
                </div>
                <div class="result-box">
                    <strong>Result:</strong> {step_result.result}
                </div>
            </div>
            """, unsafe_allow_html=True)

def main():
    st.title("AI Agent Planner Visualization")
    
    with st.sidebar:
        st.title("⚙️ Configuration")
        # Replace API key input with a simple status indicator
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.success("✅ OpenAI API Key loaded from environment")
        else:
            st.error("❌ OpenAI API Key not found in environment")
            
        st.markdown("### Available Actions")
        for action_class in AVAILABLE_ACTIONS:
            with st.expander(f"{action_class.__name__}"):
                st.write(f"**Description:** {action_class.description}")
                st.write(f"**Est. Duration:** {action_class.estimated_duration_seconds:.1f}s")
        
        st.markdown("### About")
        st.info("This app visualizes AI agent planning and execution.")

    # Initialize session state
    if 'workflow_stage' not in st.session_state:
        st.session_state.workflow_stage = 'input'  # Stages: input, planning, feedback, executing, completed
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ''
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
    if 'execution_results' not in st.session_state:
        st.session_state.execution_results = []
    if 'final_answer' not in st.session_state:
        st.session_state.final_answer = ''
    if 'user_feedback' not in st.session_state:
        st.session_state.user_feedback = ''
    
    # Main content area
    st.markdown('<div class="header-box"><h2>🧠 AI Agent Input</h2></div>', unsafe_allow_html=True)
    
    # Input section (always visible)
    if st.session_state.workflow_stage == 'input':
        query = st.text_area("Enter your question:", "Introduce AI product release from big tech companies in 2021?", height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            static_button = st.button("Generate Plan", type="primary", use_container_width=True)
        
        with col2:
            dynamic_button = st.button("Run Dynamic Planning", use_container_width=True)
        
        if static_button:
            if not os.getenv("OPENAI_API_KEY"):
                st.error("OpenAI API Key not found in environment. Please add it to your .env file.")
            else:
                # Update state and transition to planning stage
                st.session_state.current_query = query
                st.session_state.workflow_stage = 'planning'
                st.rerun()
        
        if dynamic_button:
            if not os.getenv("OPENAI_API_KEY"):
                st.error("OpenAI API Key not found in environment. Please add it to your .env file.")
            else:
                st.session_state.current_query = query
                st.session_state.workflow_stage = 'dynamic'
                st.rerun()
    
    # Planning stage - Generate the initial plan
    if st.session_state.workflow_stage == 'planning':
        st.markdown('<div class="header-box"><h2>🔍 Generating Plan</h2></div>', unsafe_allow_html=True)
        
        with st.spinner("Generating plan..."):
            # Create containers for the plan and feedback
            plan_container = st.container()
            
            # Generate the plan using LLM
            generated_plan = generate_plan(st.session_state.current_query)
            st.session_state.current_plan = generated_plan
            
            # Display the plan
            display_plan(plan_container, generated_plan)
            
            # Update state and move to feedback stage
            st.session_state.workflow_stage = 'feedback'
            st.rerun()
    
    # Feedback stage - Allow user to provide feedback on the plan
    if st.session_state.workflow_stage == 'feedback':
        st.markdown('<div class="header-box"><h2>🔍 Generated Plan</h2></div>', unsafe_allow_html=True)
        
        # Display the current plan
        plan_container = st.container()
        display_plan(plan_container, st.session_state.current_plan)
        
        # Feedback section
        st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
        st.subheader("Plan Feedback")
        st.write("Would you like to approve this plan or provide feedback to refine it?")
        
        # Options for feedback
        col1, col2 = st.columns(2)
        with col1:
            approve_button = st.button("✅ Approve Plan", use_container_width=True)
        with col2:
            reject_button = st.button("❌ Reject Plan", use_container_width=True)
        
        feedback = st.text_area("Provide feedback to refine the plan:", 
                               placeholder="e.g., Add a step to check social media sources, or reduce the number of steps...",
                               key="feedback_input")
        
        submit_feedback = st.button("🔄 Submit Feedback", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle feedback options
        if approve_button:
            st.session_state.workflow_stage = 'executing'
            st.rerun()
        elif reject_button:
            # Reset back to input stage
            st.session_state.workflow_stage = 'input'
            st.session_state.current_plan = None
            st.session_state.user_feedback = ''
            st.rerun()
        elif submit_feedback and feedback:
            # Save feedback and regenerate plan
            st.session_state.user_feedback = feedback
            
            with st.spinner("Updating plan based on feedback..."):
                # Generate a new plan using the feedback
                new_plan = generate_plan(
                    st.session_state.current_query, 
                    feedback, 
                    st.session_state.current_plan
                )
                st.session_state.current_plan = new_plan
            
            # Stay in feedback stage to show the updated plan
            st.rerun()
    
    # Execution stage - Execute the approved plan
    if st.session_state.workflow_stage == 'executing':
        st.markdown('<div class="header-box"><h2>⚙️ Executing Plan</h2></div>', unsafe_allow_html=True)
        
        # First, show the approved plan
        plan_container = st.container()
        display_plan(plan_container, st.session_state.current_plan)
        
        with st.spinner("Executing plan..."):
            # Execute the plan
            answer, results = execute_plan(
                st.session_state.current_query, 
                st.session_state.current_plan
            )
            
            # Save results to session state
            st.session_state.execution_results = results
            st.session_state.final_answer = answer
            st.session_state.workflow_stage = 'completed'
            st.rerun()
    
    # Completed stage - Show execution results and final answer
    if st.session_state.workflow_stage == 'completed':
        st.markdown('<div class="header-box"><h2>🎯 Execution Results</h2></div>', unsafe_allow_html=True)
        
        # Display execution results
        execution_container = st.container()
        display_execution(execution_container, st.session_state.execution_results)
        
        # Display final answer
        st.markdown('<div class="header-box"><h3>🎯 Final Answer</h3></div>', unsafe_allow_html=True)
        st.success(st.session_state.final_answer)
        
        # Option to start over
        if st.button("Start Over", use_container_width=True):
            # Reset all state
            st.session_state.workflow_stage = 'input'
            st.session_state.current_query = ''
            st.session_state.current_plan = None
            st.session_state.execution_results = []
            st.session_state.final_answer = ''
            st.session_state.user_feedback = ''
            st.rerun()
    
    # Dynamic planning section
    if st.session_state.workflow_stage == 'dynamic':
        st.markdown('<div class="header-box"><h2>🔄 Dynamic Planning Results</h2></div>', unsafe_allow_html=True)
        
        with st.spinner("Running dynamic planning..."):
            # Create main container
            dynamic_container = st.container()
            
            # Run dynamic solve
            answer, past_steps = dynamic_solve(st.session_state.current_query, max_steps=10)
            
            with dynamic_container:
                # Display each step
                for i, step_result in enumerate(past_steps):
                    st.markdown(f"""
                    <div class="step-box">
                        <h4>Step {i+1} of {len(past_steps)}</h4>
                        <div class="thought-box">
                            <strong>Thought:</strong> {step_result.step.thought}
                        </div>
                        <div class="action-box">
                            <strong>Action:</strong> {type(step_result.step.action).__name__}
                        </div>
                        <div class="result-box">
                            <strong>Result:</strong> {step_result.result}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.3)  # Brief pause for visual effect
                
                # Display final answer
                st.markdown('<div class="header-box"><h3>🎯 Final Answer</h3></div>', unsafe_allow_html=True)
                st.success(answer)
            
            # Store results and update state
            st.session_state.final_answer = answer
            st.session_state.execution_results = past_steps
            st.session_state.workflow_stage = 'completed'
            
            # Option to start over
            if st.button("Start Over", use_container_width=True):
                # Reset all state
                st.session_state.workflow_stage = 'input'
                st.session_state.current_query = ''
                st.session_state.current_plan = None
                st.session_state.execution_results = []
                st.session_state.final_answer = ''
                st.session_state.user_feedback = ''
                st.rerun()

if __name__ == "__main__":
    main() 