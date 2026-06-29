"""Node functions for the LangGraph workflow.

Each function receives AgentState and returns a partial state update dict.
Do NOT mutate input state — return new values only.

LLM REQUIREMENT:
- classify_node MUST use a real LLM call (structured output for intent classification)
- answer_node MUST use a real LLM call (grounded response generation)
- evaluate_node SHOULD use LLM-as-judge (bonus points; heuristic acceptable for base score)
"""

from __future__ import annotations

from .state import AgentState, make_event


# ─── EXAMPLE: working node (provided for reference) ──────────────────
def intake_node(state: AgentState) -> dict:
    """Normalize raw query. This node is provided as a working example."""
    query = state.get("query", "").strip()
    return {
        "query": query,
        "messages": [f"intake:{query[:40]}"],
        "events": [make_event("intake", "completed", "query normalized")],
    }


# ─── TODO(student): implement ALL nodes below ────────────────────────

from typing import Literal
from pydantic import BaseModel
from .llm import get_llm


class ClassificationOutput(BaseModel):
    route: Literal["simple", "tool", "missing_info", "risky", "error"]


def classify_node(state: AgentState) -> dict:
    """Classify the query into a route using an LLM."""
    llm = get_llm().with_structured_output(ClassificationOutput)
    query = state.get("query", "")
    prompt = (
        "Classify the following support ticket query into exactly one of these categories:\n"
        "1. risky: Actions with side effects like refunds, deletions, sending emails, cancellations.\n"
        "2. tool: Information lookups like order status, tracking, search queries.\n"
        "3. missing_info: Vague or incomplete queries lacking actionable context.\n"
        "4. error: System failures, timeouts, crashes, service unavailable.\n"
        "5. simple: General questions answerable without tools or actions.\n"
        "Priority guide: risky > tool > missing_info > error > simple.\n\n"
        f"Query: {query}"
    )
    result = llm.invoke(prompt)
    route = result.route
    risk_level = "high" if route == "risky" else "low"
    
    return {
        "route": route,
        "risk_level": risk_level,
        "events": [make_event("classify", "completed", f"classified as {route} with risk {risk_level}")]
    }


def tool_node(state: AgentState) -> dict:
    """Execute a mock tool call."""
    attempt = state.get("attempt", 0)
    route = state.get("route", "")
    
    if route == "error" and attempt < 2:
        result_string = "ERROR: Mock transient failure"
    else:
        result_string = "SUCCESS: Mock tool execution succeeded"
        
    return {
        "tool_results": [result_string],
        "events": [make_event("tool", "completed", "executed mock tool")]
    }


class EvaluationOutput(BaseModel):
    eval_result: Literal["success", "needs_retry"]

def evaluate_node(state: AgentState) -> dict:
    """Evaluate tool results — the retry-loop gate."""
    tool_results = state.get("tool_results", [])
    latest_result = tool_results[-1] if tool_results else ""
    
    llm = get_llm().with_structured_output(EvaluationOutput)
    prompt = (
        "You are an evaluator judge. Analyze the following tool execution result and decide if it was successful "
        "or if it failed and needs a retry.\n"
        f"Tool Result: {latest_result}\n\n"
        "If the result indicates an error or failure, return 'needs_retry'. Otherwise, return 'success'."
    )
    result = llm.invoke(prompt)
    eval_result = result.eval_result
        
    return {
        "evaluation_result": eval_result,
        "events": [make_event("evaluate", "completed", f"evaluation result: {eval_result}")]
    }


def answer_node(state: AgentState) -> dict:
    """Generate a final response using an LLM."""
    llm = get_llm()
    query = state.get("query", "")
    tool_results = state.get("tool_results", [])
    approval = state.get("approval", {})
    
    prompt = f"Answer the user's query: '{query}'\n"
    if tool_results:
        prompt += f"Context from tools: {tool_results}\n"
    if approval:
        prompt += f"Approval decision: {approval}\n"
        
    prompt += "Provide a helpful and grounded response."
    
    result = llm.invoke(prompt)
    final_answer = result.content
    
    return {
        "final_answer": final_answer,
        "events": [make_event("answer", "completed", "generated final answer")]
    }


def ask_clarification_node(state: AgentState) -> dict:
    """Ask for missing information instead of hallucinating."""
    llm = get_llm()
    query = state.get("query", "")
    
    prompt = f"The user asked: '{query}', but it is vague or missing information. Ask a specific clarifying question."
    result = llm.invoke(prompt)
    clarification = result.content
    
    return {
        "pending_question": clarification,
        "final_answer": clarification,
        "events": [make_event("clarify", "completed", "asked clarification question")]
    }


def risky_action_node(state: AgentState) -> dict:
    """Prepare a risky action for human approval."""
    llm = get_llm()
    query = state.get("query", "")
    
    prompt = f"The user asked: '{query}'. Describe the proposed risky action and why it requires human approval."
    result = llm.invoke(prompt)
    proposed_action = result.content
    
    return {
        "proposed_action": proposed_action,
        "events": [make_event("risky_action", "completed", "prepared risky action for approval")]
    }


def approval_node(state: AgentState) -> dict:
    """Human-in-the-loop approval step."""
    import os
    from langgraph.types import interrupt
    
    if os.getenv("LANGGRAPH_INTERRUPT") == "true":
        # Wait for user input
        approval_decision = interrupt({"action_required": "Please approve or reject the risky action."})
    else:
        approval_decision = {"approved": True, "reviewer": "mock-reviewer", "comment": "Auto-approved"}
        
    return {
        "approval": approval_decision,
        "events": [make_event("approval", "completed", "approval processed")]
    }


def retry_or_fallback_node(state: AgentState) -> dict:
    """Record a retry attempt."""
    attempt = state.get("attempt", 0) + 1
    error_msg = f"Failed attempt {attempt}"
    
    return {
        "attempt": attempt,
        "errors": [error_msg],
        "events": [make_event("retry_or_fallback", "completed", "recorded retry attempt")]
    }


def dead_letter_node(state: AgentState) -> dict:
    """Handle unresolvable failures after max retries exceeded."""
    msg = "Request could not be completed after maximum retries."
    return {
        "final_answer": msg,
        "events": [make_event("dead_letter", "completed", msg)]
    }


def finalize_node(state: AgentState) -> dict:
    """Emit a final audit event. All routes must pass through here before END."""
    return {
        "events": [make_event("finalize", "completed", "workflow finished")]
    }
