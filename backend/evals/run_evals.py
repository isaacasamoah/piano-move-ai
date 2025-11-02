"""
Run evaluations against the agent.

Usage:
    python -m evals.run_evals
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evals.eval_framework import AgentEvaluator, create_default_test_suite
from app.llm import claude_agent_turn


async def mock_agent_function(user_input: str, session_data: dict):
    """
    Mock agent function for testing.

    In production, this calls your actual Claude agent.
    For testing, you can use this to simulate responses.
    """
    # Call your actual agent
    response = await claude_agent_turn(
        user_input=user_input,
        collected_data=session_data,
        transcript=[]  # Would include full transcript in production
    )

    return response


async def main():
    """Run all evals and print report."""

    print("🧬 Starting Agent Evaluation...")
    print("=" * 60)

    # Create evaluator
    evaluator = AgentEvaluator()

    # Load test suite
    test_cases = create_default_test_suite()
    for test_case in test_cases:
        evaluator.add_test_case(test_case)

    print(f"\n Loaded {len(test_cases)} test cases")
    print("\nRunning tests...\n")

    # Run all tests
    summary = await evaluator.run_all_tests(mock_agent_function)

    # Generate and print report
    report = evaluator.generate_report(summary)
    print(report)

    # Exit with code based on pass/fail
    if summary['pass_rate'] >= 0.9:
        print("\n✅ EVAL SUITE PASSED")
        sys.exit(0)
    else:
        print("\n❌ EVAL SUITE FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
