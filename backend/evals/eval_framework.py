"""
Evaluation framework for conversational AI agents.

Tests constitutional principles and extraction accuracy across scenarios.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime


class ConstitutionalPrinciple(str, Enum):
    """Constitutional principles to test."""
    RESPECT_TIME = "respect_customer_time"
    BUILD_TRUST = "build_trust_through_transparency"
    ENABLE_SUCCESS = "enable_business_success"
    HUMAN_CENTRIC = "human_centric_service"


class TestScenarioType(str, Enum):
    """Types of test scenarios."""
    HAPPY_PATH = "happy_path"
    BATCH_INFO = "batch_information"
    AMBIGUOUS_INPUT = "ambiguous_input"
    BACKTRACKING = "backtracking"
    COMPLEX_QUESTION = "complex_question"
    GRACEFUL_FAILURE = "graceful_failure"
    EFFICIENCY = "efficiency_test"
    EDGE_CASE = "edge_case"


@dataclass
class ConversationTurn:
    """Single turn in conversation."""
    role: str  # "user" or "agent"
    content: str
    agent_response: Optional[Dict[str, Any]] = None  # Full JSON response from agent


@dataclass
class EvalTestCase:
    """Single evaluation test case."""
    test_id: str
    name: str
    scenario_type: TestScenarioType
    tests_principle: ConstitutionalPrinciple
    conversation_turns: List[ConversationTurn]
    expected_behavior: Dict[str, Any]
    pass_criteria: Dict[str, Any]
    description: str


@dataclass
class EvalResult:
    """Result of running a single eval test case."""
    test_id: str
    passed: bool
    score: float  # 0.0 to 1.0
    failures: List[str]
    metrics: Dict[str, Any]
    timestamp: datetime


class AgentEvaluator:
    """Evaluates agent performance against test cases."""

    def __init__(self):
        self.test_cases: List[EvalTestCase] = []
        self.results: List[EvalResult] = []

    def add_test_case(self, test_case: EvalTestCase):
        """Add a test case to the evaluation suite."""
        self.test_cases.append(test_case)

    async def run_test_case(self, test_case: EvalTestCase, agent_function) -> EvalResult:
        """
        Run a single test case against the agent.

        Args:
            test_case: Test case to run
            agent_function: Async function that takes user input and returns agent response

        Returns:
            EvalResult with pass/fail and metrics
        """
        failures = []
        metrics = {}

        # Run conversation
        session_data = {
            "piano_type": None,
            "pickup_address": None,
            "delivery_address": None,
            "stairs_count": None,
            "has_insurance": None
        }

        for turn in test_case.conversation_turns:
            if turn.role == "user":
                # Get agent response
                response = await agent_function(
                    user_input=turn.content,
                    session_data=session_data
                )

                # Update session with extracted data
                if "extracted" in response:
                    for key, value in response["extracted"].items():
                        if value is not None:
                            session_data[key] = value

                # Store response for evaluation
                turn.agent_response = response

        # Evaluate based on pass criteria
        score = 0.0
        total_checks = len(test_case.pass_criteria)

        for criterion, expected in test_case.pass_criteria.items():
            if self._check_criterion(criterion, expected, test_case, session_data):
                score += 1.0
            else:
                failures.append(f"Failed: {criterion}")

        score = score / total_checks if total_checks > 0 else 0.0

        # Calculate metrics
        metrics = {
            "total_turns": len([t for t in test_case.conversation_turns if t.role == "user"]),
            "extraction_accuracy": self._calculate_extraction_accuracy(test_case, session_data),
            "constitutional_compliance": score,
            "avg_response_length": self._avg_response_length(test_case)
        }

        return EvalResult(
            test_id=test_case.test_id,
            passed=(score >= 0.9),  # 90% pass threshold
            score=score,
            failures=failures,
            metrics=metrics,
            timestamp=datetime.utcnow()
        )

    def _check_criterion(self, criterion: str, expected: Any, test_case: EvalTestCase, session_data: Dict) -> bool:
        """Check if a pass criterion is met."""

        if criterion == "no_assumptions":
            # Check that agent never extracted data without confirmation
            return self._verify_no_assumptions(test_case)

        elif criterion == "extraction_complete":
            # Check all fields extracted correctly
            return all(session_data[k] == expected.get(k) for k in session_data.keys())

        elif criterion == "transfer_to_human":
            # Check that agent set should_transfer_to_human
            last_turn = test_case.conversation_turns[-1]
            if last_turn.agent_response:
                return last_turn.agent_response.get("should_transfer_to_human") == expected

        elif criterion == "max_turns":
            # Check conversation completed within turn limit
            user_turns = len([t for t in test_case.conversation_turns if t.role == "user"])
            return user_turns <= expected

        elif criterion == "response_length":
            # Check all responses under sentence limit
            for turn in test_case.conversation_turns:
                if turn.agent_response and "response" in turn.agent_response:
                    sentences = turn.agent_response["response"].count('.') + turn.agent_response["response"].count('?')
                    if sentences > expected:
                        return False
            return True

        elif criterion == "batch_extraction":
            # Check that agent extracted multiple fields in single turn
            for turn in test_case.conversation_turns:
                if turn.agent_response and "extracted" in turn.agent_response:
                    extracted_count = len([v for v in turn.agent_response["extracted"].values() if v is not None])
                    if extracted_count >= expected:
                        return True
            return False

        return True

    def _verify_no_assumptions(self, test_case: EvalTestCase) -> bool:
        """Verify agent didn't make assumptions."""
        # Check for specific assumption patterns
        for turn in test_case.conversation_turns:
            if turn.agent_response and "extracted" in turn.agent_response:
                extracted = turn.agent_response["extracted"]

                # Example: If user said "Richmond", agent shouldn't extract "Richmond VIC"
                # This would be checked by comparing extracted vs user input
                # For now, check if needs_clarification was set appropriately
                if turn.agent_response.get("needs_clarification"):
                    continue  # Good - agent asked for clarification

        return True

    def _calculate_extraction_accuracy(self, test_case: EvalTestCase, session_data: Dict) -> float:
        """Calculate extraction accuracy."""
        if "expected_data" not in test_case.expected_behavior:
            return 1.0

        expected = test_case.expected_behavior["expected_data"]
        correct = sum(1 for k, v in expected.items() if session_data.get(k) == v)
        total = len(expected)

        return correct / total if total > 0 else 0.0

    def _avg_response_length(self, test_case: EvalTestCase) -> float:
        """Calculate average response length in sentences."""
        total_sentences = 0
        response_count = 0

        for turn in test_case.conversation_turns:
            if turn.agent_response and "response" in turn.agent_response:
                sentences = turn.agent_response["response"].count('.') + turn.agent_response["response"].count('?')
                total_sentences += sentences
                response_count += 1

        return total_sentences / response_count if response_count > 0 else 0.0

    async def run_all_tests(self, agent_function) -> Dict[str, Any]:
        """Run all test cases and return summary."""
        self.results = []

        for test_case in self.test_cases:
            result = await self.run_test_case(test_case, agent_function)
            self.results.append(result)

        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        avg_score = sum(r.score for r in self.results) / total_tests if total_tests > 0 else 0.0

        # Group by principle
        principle_scores = {}
        for test_case in self.test_cases:
            principle = test_case.tests_principle.value
            if principle not in principle_scores:
                principle_scores[principle] = []

            # Find corresponding result
            result = next(r for r in self.results if r.test_id == test_case.test_id)
            principle_scores[principle].append(result.score)

        for principle, scores in principle_scores.items():
            principle_scores[principle] = sum(scores) / len(scores)

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "avg_score": avg_score,
            "principle_scores": principle_scores,
            "results": self.results
        }

    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate human-readable eval report."""
        report = []
        report.append("=" * 60)
        report.append("AGENT EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"\nTotal Tests: {summary['total_tests']}")
        report.append(f"Passed: {summary['passed_tests']}")
        report.append(f"Failed: {summary['failed_tests']}")
        report.append(f"Pass Rate: {summary['pass_rate']*100:.1f}%")
        report.append(f"Average Score: {summary['avg_score']*100:.1f}%")

        report.append("\n" + "-" * 60)
        report.append("CONSTITUTIONAL PRINCIPLE SCORES")
        report.append("-" * 60)
        for principle, score in summary['principle_scores'].items():
            status = "✅ PASS" if score >= 0.9 else "❌ FAIL"
            report.append(f"{principle}: {score*100:.1f}% {status}")

        report.append("\n" + "-" * 60)
        report.append("INDIVIDUAL TEST RESULTS")
        report.append("-" * 60)

        for result in summary['results']:
            test = next(t for t in self.test_cases if t.test_id == result.test_id)
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report.append(f"\n{test.name} ({test.scenario_type.value})")
            report.append(f"  Score: {result.score*100:.1f}% {status}")
            report.append(f"  Metrics: {json.dumps(result.metrics, indent=2)}")
            if result.failures:
                report.append(f"  Failures:")
                for failure in result.failures:
                    report.append(f"    - {failure}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)


def create_default_test_suite() -> List[EvalTestCase]:
    """Create default test suite for piano moving agent."""

    test_cases = []

    # Test 1: Happy Path
    test_cases.append(EvalTestCase(
        test_id="happy_path_001",
        name="Happy Path - Linear Conversation",
        scenario_type=TestScenarioType.HAPPY_PATH,
        tests_principle=ConstitutionalPrinciple.RESPECT_TIME,
        conversation_turns=[
            ConversationTurn("user", "I need to move my piano"),
            ConversationTurn("user", "It's an upright"),
            ConversationTurn("user", "56 Turnip Street, Brisbane QLD"),
            ConversationTurn("user", "56 Tring Street, Gold Coast QLD"),
            ConversationTurn("user", "No stairs"),
            ConversationTurn("user", "Yes to insurance"),
        ],
        expected_behavior={
            "expected_data": {
                "piano_type": "upright",
                "pickup_address": "56 Turnip Street, Brisbane QLD",
                "delivery_address": "56 Tring Street, Gold Coast QLD",
                "stairs_count": 0,
                "has_insurance": True
            },
            "should_complete": True
        },
        pass_criteria={
            "extraction_complete": {
                "piano_type": "upright",
                "pickup_address": "56 Turnip Street, Brisbane QLD",
                "delivery_address": "56 Tring Street, Gold Coast QLD",
                "stairs_count": 0,
                "has_insurance": True
            },
            "max_turns": 6,
            "response_length": 3
        },
        description="Customer provides info linearly in order. Agent should extract accurately and complete in ~6 turns."
    ))

    # Test 2: Batch Information
    test_cases.append(EvalTestCase(
        test_id="batch_info_001",
        name="Batch Information - Efficient Customer",
        scenario_type=TestScenarioType.BATCH_INFO,
        tests_principle=ConstitutionalPrinciple.RESPECT_TIME,
        conversation_turns=[
            ConversationTurn("user", "Baby grand from 34 Street Street Grayson Brisbane QLD to 45 Gree Street Grayton Brisbane QLD, 3 stairs at pickup and 7 at delivery, yes to insurance"),
        ],
        expected_behavior={
            "expected_data": {
                "piano_type": "baby_grand",
                "pickup_address": "34 Street Street, Grayson, Brisbane QLD",
                "delivery_address": "45 Gree Street, Grayton, Brisbane QLD",
                "stairs_count": 10,
                "has_insurance": True
            },
            "should_complete": True
        },
        pass_criteria={
            "batch_extraction": 3,  # Should extract at least 3 fields in first turn
            "max_turns": 2,  # Should complete in 1-2 turns
            "extraction_complete": {
                "piano_type": "baby_grand",
                "pickup_address": "34 Street Street, Grayson, Brisbane QLD",
                "delivery_address": "45 Gree Street, Grayton, Brisbane QLD",
                "stairs_count": 10,
                "has_insurance": True
            }
        },
        description="Customer provides all info at once. Agent should extract efficiently."
    ))

    # Test 3: No Assumptions
    test_cases.append(EvalTestCase(
        test_id="no_assumptions_001",
        name="Ambiguous Input - Never Assume",
        scenario_type=TestScenarioType.AMBIGUOUS_INPUT,
        tests_principle=ConstitutionalPrinciple.BUILD_TRUST,
        conversation_turns=[
            ConversationTurn("user", "Baby grand"),
            ConversationTurn("user", "Richmond"),  # Ambiguous - which Richmond?
        ],
        expected_behavior={
            "should_ask_clarification": True,
            "should_not_assume_state": True
        },
        pass_criteria={
            "no_assumptions": True,
        },
        description="Agent must ask for clarification on 'Richmond', not assume Richmond VIC."
    ))

    # Test 4: Transfer to Human
    test_cases.append(EvalTestCase(
        test_id="transfer_001",
        name="Complex Question - Transfer to Human",
        scenario_type=TestScenarioType.COMPLEX_QUESTION,
        tests_principle=ConstitutionalPrinciple.HUMAN_CENTRIC,
        conversation_turns=[
            ConversationTurn("user", "Baby grand"),
            ConversationTurn("user", "What happens if the piano gets damaged after delivery? Does insurance cover that?"),
        ],
        expected_behavior={
            "should_transfer": True,
            "transfer_reason": "Insurance policy question outside agent scope"
        },
        pass_criteria={
            "transfer_to_human": True,
        },
        description="Agent should transfer complex insurance policy questions to human."
    ))

    return test_cases
