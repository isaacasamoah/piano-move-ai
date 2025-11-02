# Agent Evaluation Framework

Systematic testing for conversational AI agents based on constitutional principles.

## Overview

This eval framework tests:
1. **Extraction Accuracy** - Does the agent extract data correctly?
2. **Constitutional Compliance** - Does it follow core principles?
3. **Efficiency** - Response length, turn count
4. **Edge Cases** - Handles complexity, transfers appropriately

## Quick Start

```bash
# Run all evals
python -m evals.run_evals

# Expected output:
# ✅ EVAL SUITE PASSED (pass rate >= 90%)
# or
# ❌ EVAL SUITE FAILED (pass rate < 90%)
```

## Test Coverage

### Constitutional Principles Tested

1. **Respect Customer Time**
   - Response length (under 3 sentences)
   - Conversation efficiency (min turns)
   - Batch information extraction

2. **Build Trust Through Transparency**
   - No assumptions (Richmond ≠ Richmond VIC)
   - Asks for clarification when ambiguous
   - Confirms critical information

3. **Enable Business Success**
   - Extraction accuracy (100% target)
   - Data quality (complete addresses)
   - Professional representation

4. **Human-Centric Service**
   - Transfers complex questions to human
   - Handles corrections gracefully
   - Fails gracefully (doesn't loop forever)

### Test Scenarios

| Scenario | Count | Tests |
|----------|-------|-------|
| Happy Path | 1 | Linear conversation flow |
| Batch Information | 1 | Efficient extraction |
| Ambiguous Input | 2 | No assumptions |
| Backtracking | 1 | Handle corrections |
| Complex Questions | 2 | Transfer to human |
| Graceful Failure | 1 | Don't loop forever |
| Efficiency | 1 | Response length |
| Edge Cases | 3 | Multi-piano, international, urgent |

**Total: 12 test cases**

## Test Case Structure

Each test case includes:

```json
{
  "test_id": "unique_id",
  "name": "Human readable name",
  "scenario_type": "happy_path | batch_info | ambiguous | ...",
  "tests_principle": "respect_time | build_trust | ...",
  "description": "What this test verifies",
  "conversation": [
    {
      "role": "user",
      "content": "User input",
      "expected_extraction": {
        "field": "value"
      }
    }
  ],
  "pass_criteria": {
    "extraction_accuracy": 1.0,
    "max_turns": 6,
    "constitutional_compliance": [...]
  }
}
```

## Pass Criteria

### Overall Suite
- **Pass threshold:** 90% of tests must pass
- **Score calculation:** Average of all test scores

### Individual Tests
Tests pass if they meet **all** pass criteria:
- Extraction accuracy >= 90%
- Constitutional compliance: all principles followed
- Scenario-specific criteria met

## Eval Metrics

For each test:
```python
{
  "total_turns": 6,
  "extraction_accuracy": 1.0,  # 100%
  "constitutional_compliance": 0.95,  # 95%
  "avg_response_length": 2.3  # sentences
}
```

## Adding New Tests

### 1. Add to test_cases.json

```json
{
  "test_id": "your_test_001",
  "name": "Your Test Name",
  "scenario_type": "happy_path",
  "tests_principle": "respect_customer_time",
  "description": "What you're testing",
  "conversation": [
    {
      "role": "user",
      "content": "User says this",
      "expected_extraction": {
        "piano_type": "upright"
      }
    }
  ],
  "pass_criteria": {
    "extraction_accuracy": 1.0
  }
}
```

### 2. Run evals

```bash
python -m evals.run_evals
```

## Integration with CI/CD

Add to GitHub Actions:

```yaml
name: Agent Evals

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run evals
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python -m evals.run_evals
```

## Eval Report Example

```
============================================================
AGENT EVALUATION REPORT
============================================================

Total Tests: 12
Passed: 11
Failed: 1
Pass Rate: 91.7%
Average Score: 93.2%

------------------------------------------------------------
CONSTITUTIONAL PRINCIPLE SCORES
------------------------------------------------------------
respect_customer_time: 95.0% ✅ PASS
build_trust_through_transparency: 100.0% ✅ PASS
enable_business_success: 90.0% ✅ PASS
human_centric_service: 88.0% ❌ FAIL

------------------------------------------------------------
INDIVIDUAL TEST RESULTS
------------------------------------------------------------

Happy Path - Linear Conversation (happy_path)
  Score: 100.0% ✅ PASS
  Metrics: {
    "total_turns": 6,
    "extraction_accuracy": 1.0,
    "constitutional_compliance": 1.0,
    "avg_response_length": 2.1
  }

Batch Information - Efficient Customer (batch_information)
  Score: 100.0% ✅ PASS
  Metrics: {
    "total_turns": 1,
    "extraction_accuracy": 1.0,
    "constitutional_compliance": 1.0,
    "avg_response_length": 2.5
  }

...
```

## Continuous Improvement

### After Each Iteration

1. Run evals: `python -m evals.run_evals`
2. Check failures
3. Update prompt if needed
4. Re-run evals
5. Repeat until pass rate >= 90%

### Adding Domain Tests

When adding new business type (e.g., house cleaning):

1. Create `test_cases_house_cleaning.json`
2. Define domain-specific tests
3. Run: `python -m evals.run_evals --domain house_cleaning`

## Philosophy

**Evals are experiments, not bureaucracy.**

- Quick to run (~2 minutes for 12 tests)
- Easy to add new tests
- Focus on constitutional principles, not nitpicking
- Pass/fail is clear
- Guides prompt improvement

## Next Steps

1. **Run baseline:** `python -m evals.run_evals`
2. **Fix failures:** Update agent prompt
3. **Add domain tests:** When expanding to new business types
4. **Automate:** Add to CI/CD pipeline

---

Built with constitutional AI principles. Test behavior, not just extraction.
