# Lab Report

## 1. Metrics Summary
- Total Scenarios: 7
- Success Rate: 100.00%
- Total Retries: 0
- Interrupts: 2

## 2. Per-Scenario Results
| ID | Success | Expected Route | Actual Route | Nodes | Retries |
|---|---|---|---|---|---|
| S01_simple | True | simple | simple | 4 | 0 |
| S02_tool | True | tool | tool | 6 | 0 |
| S03_missing | True | missing_info | missing_info | 4 | 0 |
| S04_risky | True | risky | risky | 8 | 0 |
| S05_error | True | error | error | 10 | 0 |
| S06_delete | True | risky | risky | 8 | 0 |
| S07_dead_letter | True | error | error | 5 | 0 |

## 3. Architecture
The graph uses conditional edges to route user queries:

- `classify` uses an LLM to categorize intents (risky, missing_info, tool, simple, error).
- `tool` executes mock tools and loops back on errors via `evaluate` and `retry`.
- `risky_action` leads to `approval` which uses `interrupt` to prompt for HITL.

## 4. Failure Analysis

- **Unbounded Retry Loops**: Without bounded retries, system failures cause infinite loops. We added `attempt` counting and `dead_letter` to forcefully exit loops after max retries.
- **Classification Errors**: LLMs might misclassify if prompts are unclear. Using `.with_structured_output` guarantees we get a valid enum route.

## 5. Extensions Completed (Bonus)
We implemented multiple bonus extensions for the 90+ tier:

1. **LLM-as-Judge**: We upgraded `evaluate_node` to use an LLM structured output to actively analyze the tool result and determine if a retry is needed.
2. **Crash Recovery & Persistence**: We implemented the SQLite Checkpointer and wrote `test_resume.py` to successfully demonstrate state recovery after a simulated crash at the HITL approval node.
3. **Graph Diagram**: We created `export_graph.py` to successfully export the graph architecture into a Mermaid diagram.
