#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

import os
import shutil

import engineering_team.patch # noga:F401 - applies CreAI MCP monkey-patch on imports
from engineering_team.crew import EngineeringTeam
from .tools.sandbox_tools import SANDBOX_DIR, reset_sandbox
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

requirements = """
A simple account management system for a trading simulation platform.
The system should allow users to create an account, deposit funds, and withdraw funds.
The system should allow users to record that they have bought or sold shares, providing a quantity.
The system should calculate the total value of the user's portfolio, and the profit or loss from the initial deposit.
The system should be able to report the holdings of the user at any point in time.
The system should be able to list the transactions that the user made over time.
The system should prevent the user from withdrawing funds that would leave them with a negative balance, or
from buying more shares than they can afford, or selling shares that they dont have.
The system has access to a function get_share_price(symbol) which returns the current price of a share, and includes 
a test implementation that returns fixed prices for AAPL, TSLA, and GOOGL.
"""
def run() -> None:
    """
    Run the crew.
    """
    inputs = {
        'requirements': requirements
    }
    # Preserve generated files before agents can modify them
    if SANDBOX_DIR.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup_dir = (
            SANDBOX_DIR.parent / "sandbox_backups"/ timestamp
        )
        shutil.copytree(
            SANDBOX_DIR,
            backup_dir,
            ignore= shutil.ignore_patterns(
                ".venv",
                "__pycache__",
                ".git",
                "*.pyc"
            ),
        )
        print(f"Sandbox backed up to: {backup_dir}")

    # Reset only when explicitly requested
    if os.environ.get("RESET_SANDBOX") == "1":
        reset_sandbox()
    elif not (SANDBOX_DIR/ "pyproject.toml").is_file():
        raise RuntimeError(
            "Sandbox is not properly initialized. "
            "Run with RESET_SANDBOX=1 to initialize it properly. ")
    EngineeringTeam().crew().kickoff(inputs=inputs)



def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        EngineeringTeam().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        EngineeringTeam().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        EngineeringTeam().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = EngineeringTeam().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
