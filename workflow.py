"""LangGraph workflow definition for the Entity Multi-Agent System."""

from langgraph.graph import StateGraph, END

from state import MASState
from router import route_incident

from agents import (
    audio_agent,
    video_agent,
    network_agent,
    strategy_agent,
    evaluator_agent,
    overall_risk_agent,
)

from fallback import create_fallback_response


# =========================================================
# WORKFLOW NODES
# =========================================================

def router_node(state: MASState) -> MASState:
    """
    Run the Router and store its routing decision.

    Args:
        state: Current MAS shared state.

    Returns:
        Updated Router result or captured error.
    """

    try:
        user_input = state["user_input"]

        result = route_incident(user_input)

        return {
            "router_result": result
        }

    except KeyError as error:

        # Human modification 1:
        # Missing state values are captured instead of
        # allowing the workflow to terminate unexpectedly.
        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Missing required state value: {error}"
                ]
        }


def audio_node(state: MASState) -> MASState:
    """
    Run the Audio Deepfake Analysis Agent.

    Args:
        state: Current MAS shared state.

    Returns:
        Audio analysis result or captured error.
    """

    try:
        result = audio_agent(
            state["user_input"]
        )

        return {
            "audio_result": result
        }

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:

        # Human modification 2:
        # Audio-agent failures are stored in shared state
        # so LangGraph can activate the fallback route.
        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Audio Agent failure: {error}"
                ]
        }


def video_node(state: MASState) -> MASState:
    """
    Run the Video Manipulation Analysis Agent.

    Args:
        state: Current MAS shared state.

    Returns:
        Video analysis result or captured error.
    """

    try:
        result = video_agent(
            state["user_input"]
        )

        return {
            "video_result": result
        }

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:

        # Human modification 3:
        # A failed Video Agent does not destroy results
        # already produced by earlier specialist agents.
        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Video Agent failure: {error}"
                ]
        }


def network_node(state: MASState) -> MASState:
    """
    Run the Network Intrusion Analysis Agent.

    This node also supports a deliberate simulated
    failure for testing the fallback mechanism.

    Args:
        state: Current MAS shared state.

    Returns:
        Network analysis result or captured error.
    """

    try:
        result = network_agent(
            state["user_input"],
            state.get(
                "simulate_failure",
                False
            )
        )

        return {
            "network_result": result
        }

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:

        # Human modification 4:
        # Network failures, including the deliberate
        # test failure, are redirected to fallback.
        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Network Agent failure: {error}"
                ]
        }


def risk_node(state: MASState) -> MASState:
    """
    Calculate the overall multi-vector threat score.

    Args:
        state: Current MAS shared state.

    Returns:
        Overall threat score or captured error.
    """

    try:
        score = overall_risk_agent(
            state.get("audio_result", {}),
            state.get("video_result", {}),
            state.get("network_result", {})
        )

        return {
            "overall_threat_score": score
        }

    except (
        TypeError,
        ValueError,
        KeyError
    ) as error:

        # Human modification 5:
        # Risk-calculation problems are handled safely
        # rather than producing an uncontrolled crash.
        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Risk calculation failure: {error}"
                ]
        }


def strategy_node(state: MASState) -> MASState:
    """
    Run the Strategic Response Agent for
    sufficiently high-risk incidents.

    Args:
        state: Current MAS shared state.

    Returns:
        Strategic response or captured error.
    """

    try:
        result = strategy_agent(
            state.get("audio_result", {}),
            state.get("video_result", {}),
            state.get("network_result", {})
        )

        score = state.get(
            "overall_threat_score",
            0
        )

        # Human modification 6:
        # Ensure that the qualitative risk level is
        # consistent with the deterministic threat score.
        if score >= 85:
            result["overall_risk"] = "CRITICAL"

        elif score >= 70:
            result["overall_risk"] = "HIGH"

        elif score >= 30:
            result["overall_risk"] = "MEDIUM"

        else:
            result["overall_risk"] = "LOW"

        return {
            "strategy_result": result
        }

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:

        # Strategy failures are routed to fallback instead
        # of allowing an incomplete workflow to continue.
        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Strategy Agent failure: {error}"
                ]
        }


def evaluator_node(state: MASState) -> MASState:
    """
    Run the Self-Evaluation Agent.

    The evaluator checks only threat categories selected
    by the Router.

    Args:
        state: Current MAS shared state.

    Returns:
        Evaluation result or captured error.
    """

    try:
        result = evaluator_agent(
            state["user_input"],
            state.get("router_result", {}),
            state.get("audio_result", {}),
            state.get("video_result", {}),
            state.get("network_result", {}),
            state.get("strategy_result", {})
        )

        return {
            "evaluation_result": result
        }

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:

        # Human modification 7:
        # Evaluation failure is also recoverable through
        # the common fallback mechanism.
        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Evaluator Agent failure: {error}"
                ]
        }


def fallback_node(state: MASState) -> MASState:
    """
    Generate a safe partial response after a
    recoverable component failure.

    Args:
        state: Current MAS shared state.

    Returns:
        Structured fallback response.
    """

    result = create_fallback_response(
        state.get("errors", []),
        state.get("audio_result", {}),
        state.get("video_result", {}),
        state.get("network_result", {})
    )

    return {
        "fallback_result": result
    }


# =========================================================
# CONDITIONAL ROUTING FUNCTIONS
# =========================================================

def route_after_router(state: MASState) -> str:
    """
    Decide which specialist agent should run first.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """

    if state.get("errors"):
        return "fallback"

    route = state.get(
        "router_result",
        {}
    )

    if route.get("audio"):
        return "audio"

    if route.get("video"):
        return "video"

    if route.get("network"):
        return "network"

    return "evaluate"


def route_after_audio(state: MASState) -> str:
    """
    Decide the next workflow step after
    the Audio Agent.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """

    if state.get("errors"):
        return "fallback"

    route = state.get(
        "router_result",
        {}
    )

    if route.get("video"):
        return "video"

    if route.get("network"):
        return "network"

    return "risk"


def route_after_video(state: MASState) -> str:
    """
    Decide the next workflow step after
    the Video Agent.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """

    if state.get("errors"):
        return "fallback"

    route = state.get(
        "router_result",
        {}
    )

    if route.get("network"):
        return "network"

    return "risk"


def route_after_network(state: MASState) -> str:
    """
    Continue to risk calculation or activate fallback.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """

    if state.get("errors"):
        return "fallback"

    return "risk"


def route_after_risk(state: MASState) -> str:
    """
    Route high-risk incidents to the Strategic Agent.

    Incidents with a threat score of 70 or greater
    receive strategic analysis.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """

    if state.get("errors"):
        return "fallback"

    score = state.get(
        "overall_threat_score",
        0
    )

    # Human modification 8:
    # A deterministic threshold controls whether the
    # expensive Strategic Agent is required.
    if score >= 70:
        return "strategy"

    return "evaluate"


def route_after_strategy(state: MASState) -> str:
    """
    Continue to evaluation after successful strategy
    generation or activate fallback after failure.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """

    if state.get("errors"):
        return "fallback"

    return "evaluate"


def route_after_evaluator(state: MASState) -> str:
    """
    End successful execution or activate fallback
    if evaluation failed.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """

    if state.get("errors"):
        return "fallback"

    return "end"


# =========================================================
# BUILD LANGGRAPH WORKFLOW
# =========================================================

def build_workflow():
    """
    Build and compile the Entity Multi-Agent System.

    The graph performs:
    Router
        -> selected specialist agents
        -> risk calculation
        -> optional Strategic Agent
        -> Evaluator
        -> END

    Component failures are redirected to the
    fallback mechanism.

    Returns:
        Compiled LangGraph workflow.
    """

    workflow = StateGraph(
        MASState
    )

    # Add all workflow nodes.
    workflow.add_node(
        "router",
        router_node
    )

    workflow.add_node(
        "audio",
        audio_node
    )

    workflow.add_node(
        "video",
        video_node
    )

    workflow.add_node(
        "network",
        network_node
    )

    workflow.add_node(
        "risk",
        risk_node
    )

    workflow.add_node(
        "strategy",
        strategy_node
    )

    workflow.add_node(
        "evaluate",
        evaluator_node
    )

    workflow.add_node(
        "fallback",
        fallback_node
    )

    workflow.set_entry_point(
        "router"
    )

    # -----------------------------------------------------
    # Conditional Route 1:
    # Router selects the required specialist agents.
    # -----------------------------------------------------

    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "audio": "audio",
            "video": "video",
            "network": "network",
            "evaluate": "evaluate",
            "fallback": "fallback"
        }
    )

    workflow.add_conditional_edges(
        "audio",
        route_after_audio,
        {
            "video": "video",
            "network": "network",
            "risk": "risk",
            "fallback": "fallback"
        }
    )

    workflow.add_conditional_edges(
        "video",
        route_after_video,
        {
            "network": "network",
            "risk": "risk",
            "fallback": "fallback"
        }
    )

    workflow.add_conditional_edges(
        "network",
        route_after_network,
        {
            "risk": "risk",
            "fallback": "fallback"
        }
    )

    # -----------------------------------------------------
    # Conditional Route 2:
    # Threat score determines strategic escalation.
    # -----------------------------------------------------

    workflow.add_conditional_edges(
        "risk",
        route_after_risk,
        {
            "strategy": "strategy",
            "evaluate": "evaluate",
            "fallback": "fallback"
        }
    )

    # Strategy may succeed and continue to evaluation,
    # or fail and activate fallback.
    workflow.add_conditional_edges(
        "strategy",
        route_after_strategy,
        {
            "evaluate": "evaluate",
            "fallback": "fallback"
        }
    )

    # Evaluation normally ends the workflow.
    # An evaluator failure is instead handled by fallback.
    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluator,
        {
            "end": END,
            "fallback": "fallback"
        }
    )

    workflow.add_edge(
        "fallback",
        END
    )

    return workflow.compile()