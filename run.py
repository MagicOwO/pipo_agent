"""Script to run PIPO agent examples."""

import sys
import traceback
from pathlib import Path

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['code', 'research']:
        print("Usage: python run.py [code|research]")
        print("  code     - Run code transformation example")
        print("  research - Run research task example")
        sys.exit(1)

    # Check if environment is properly set up
    if not Path('.env').exists():
        print("Error: .env file not found. Please run setup script first.")
        sys.exit(1)
    
    if not Path('.venv').exists():
        print("Error: Virtual environment not found. Please run setup script first.")
        sys.exit(1)

    example_type = sys.argv[1]
    example_file = f"examples/{example_type}_transformation.py" if example_type == "code" else f"examples/{example_type}_task.py"

    if not Path(example_file).exists():
        print(f"Error: Example file {example_file} not found.")
        sys.exit(1)

    # Import and run the example
    try:
        if example_type == 'code':
            from examples.code_transformation import main as run_example
        else:
            from examples.research_task import main as run_example
        
        run_example()
    except Exception as e:
        print("\nError running example:")
        print("=" * 60)
        traceback.print_exc()
        print("\nError details:", str(e))
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main() 