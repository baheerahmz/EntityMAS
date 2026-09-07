"""LangGraph workflow definition for the Entity Multi-Agent System."""
#describe the LangGraph workflow for the multi-agent system

from langgraph.graph import StateGraph, END
#import StateGraph to create the workflow and END to stop the workflow

from state import MASState
#import the shared state structure

from router import route_incident
#import the incident routing function

from agents import (
    audio_agent,
    video_agent,
    network_agent,
    strategy_agent,
    evaluator_agent,
    overall_risk_agent,
)
#import all agent functions used in the workflow

from fallback import create_fallback_response
#import the fallback response function


# =========================================================
# WORKFLOW NODES
# =========================================================
#define the workflow nodes


def router_node(state: MASState) -> MASState:
#run the Router node

    """
    Run the Router and store its routing decision.

    Args:
        state: Current MAS shared state.

    Returns:
        Updated Router result or captured error.
    """
    #describe the Router node

    try:
    #try to run the Router

        user_input = state["user_input"]
        #get the incident description from the shared state

        result = route_incident(user_input)
        #send the incident to the Router

        return {
            "router_result": result
        }
        #store the Router result in the shared state

    except KeyError as error:
    #handle missing state values

        # Human modification 1:
        # Missing state values are captured instead of
        # allowing the workflow to terminate unexpectedly.
        #handle missing state values safely

        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Missing required state value: {error}"
                ]
        }
        #store the error in the shared state


def audio_node(state: MASState) -> MASState:
#run the Audio Agent node

    """
    Run the Audio Deepfake Analysis Agent.

    Args:
        state: Current MAS shared state.

    Returns:
        Audio analysis result or captured error.
    """
    #describe the Audio Agent node

    try:
    #try to run the Audio Agent

        result = audio_agent(
            state["user_input"]
        )
        #send the incident to the Audio Agent

        return {
            "audio_result": result
        }
        #store the Audio Agent result

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:
    #handle possible Audio Agent errors

        # Human modification 2:
        # Audio-agent failures are stored in shared state
        # so LangGraph can activate the fallback route.
        #save Audio Agent errors for fallback

        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Audio Agent failure: {error}"
                ]
        }
        #add the Audio Agent error to the error list


def video_node(state: MASState) -> MASState:
#run the Video Agent node

    """
    Run the Video Manipulation Analysis Agent.

    Args:
        state: Current MAS shared state.

    Returns:
        Video analysis result or captured error.
    """
    #describe the Video Agent node

    try:
    #try to run the Video Agent

        result = video_agent(
            state["user_input"]
        )
        #send the incident to the Video Agent

        return {
            "video_result": result
        }
        #store the Video Agent result

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:
    #handle possible Video Agent errors

        # Human modification 3:
        # A failed Video Agent does not destroy results
        # already produced by earlier specialist agents.
        #keep previous successful results if Video fails

        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Video Agent failure: {error}"
                ]
        }
        #add the Video Agent error to the error list


def network_node(state: MASState) -> MASState:
#run the Network Agent node

    """
    Run the Network Intrusion Analysis Agent.

    This node also supports a deliberate simulated
    failure for testing the fallback mechanism.

    Args:
        state: Current MAS shared state.

    Returns:
        Network analysis result or captured error.
    """
    #describe the Network Agent node

    try:
    #try to run the Network Agent

        result = network_agent(
            state["user_input"],
            state.get(
                "simulate_failure",
                False
            )
        )
        #send the incident and failure setting to the Network Agent

        return {
            "network_result": result
        }
        #store the Network Agent result

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:
    #handle Network Agent errors

        # Human modification 4:
        # Network failures, including the deliberate
        # test failure, are redirected to fallback.
        #send Network Agent failures to fallback

        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Network Agent failure: {error}"
                ]
        }
        #save the Network Agent error


def risk_node(state: MASState) -> MASState:
#calculate the overall risk score

    """
    Calculate the overall multi-vector threat score.

    Args:
        state: Current MAS shared state.

    Returns:
        Overall threat score or captured error.
    """
    #describe the risk calculation node

    try:
    #try to calculate the risk score

        score = overall_risk_agent(
            state.get("audio_result", {}),
            state.get("video_result", {}),
            state.get("network_result", {})
        )
        #calculate risk using the available specialist results

        return {
            "overall_threat_score": score
        }
        #store the overall threat score

    except (
        TypeError,
        ValueError,
        KeyError
    ) as error:
    #handle risk calculation errors

        # Human modification 5:
        # Risk-calculation problems are handled safely
        # rather than producing an uncontrolled crash.
        #handle risk calculation errors safely

        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Risk calculation failure: {error}"
                ]
        }
        #save the risk calculation error


def strategy_node(state: MASState) -> MASState:
#run the Strategic Agent

    """
    Run the Strategic Response Agent for
    sufficiently high-risk incidents.

    Args:
        state: Current MAS shared state.

    Returns:
        Strategic response or captured error.
    """
    #describe the Strategic Agent node

    try:
    #try to run the Strategic Agent

        result = strategy_agent(
            state.get("audio_result", {}),
            state.get("video_result", {}),
            state.get("network_result", {})
        )
        #send specialist results to the Strategic Agent

        score = state.get(
            "overall_threat_score",
            0
        )
        #get the calculated overall risk score

        # Human modification 6:
        # Ensure that the qualitative risk level is
        # consistent with the deterministic threat score.
        #make the risk level match the numerical score

        if score >= 85:
        #check if the score is critical

            result["overall_risk"] = "CRITICAL"
            #set the strategic risk level to critical

        elif score >= 70:
        #check if the score is high

            result["overall_risk"] = "HIGH"
            #set the strategic risk level to high

        elif score >= 30:
        #check if the score is medium

            result["overall_risk"] = "MEDIUM"
            #set the strategic risk level to medium

        else:
        #handle low scores

            result["overall_risk"] = "LOW"
            #set the strategic risk level to low

        return {
            "strategy_result": result
        }
        #store the Strategic Agent result

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:
    #handle Strategic Agent errors

        # Strategy failures are routed to fallback instead
        # of allowing an incomplete workflow to continue.
        #send strategy errors to fallback

        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Strategy Agent failure: {error}"
                ]
        }
        #save the strategy error


def evaluator_node(state: MASState) -> MASState:
#run the Self-Evaluation Agent

    """
    Run the Self-Evaluation Agent.

    The evaluator checks only threat categories selected
    by the Router.

    Args:
        state: Current MAS shared state.

    Returns:
        Evaluation result or captured error.
    """
    #describe the evaluation node

    try:
    #try to run the Evaluator Agent

        result = evaluator_agent(
            state["user_input"],
            state.get("router_result", {}),
            state.get("audio_result", {}),
            state.get("video_result", {}),
            state.get("network_result", {}),
            state.get("strategy_result", {})
        )
        #send the incident and all relevant results to the Evaluator

        return {
            "evaluation_result": result
        }
        #store the evaluation result

    except (
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError
    ) as error:
    #handle Evaluator errors

        # Human modification 7:
        # Evaluation failure is also recoverable through
        # the common fallback mechanism.
        #allow evaluation failure to use fallback

        return {
            "errors":
                state.get("errors", [])
                + [
                    f"Evaluator Agent failure: {error}"
                ]
        }
        #save the Evaluator error


def fallback_node(state: MASState) -> MASState:
#run the fallback node

    """
    Generate a safe partial response after a
    recoverable component failure.

    Args:
        state: Current MAS shared state.

    Returns:
        Structured fallback response.
    """
    #describe the fallback node

    result = create_fallback_response(
        state.get("errors", []),
        state.get("audio_result", {}),
        state.get("video_result", {}),
        state.get("network_result", {})
    )
    #create a safe partial response using available results

    return {
        "fallback_result": result
    }
    #store the fallback result


# =========================================================
# CONDITIONAL ROUTING FUNCTIONS
# =========================================================
#define functions that decide the next workflow step


def route_after_router(state: MASState) -> str:
#decide which specialist runs after the Router

    """
    Decide which specialist agent should run first.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """
    #describe the Router routing decision

    if state.get("errors"):
    #check if an error already exists

        return "fallback"
        #go directly to fallback

    route = state.get(
        "router_result",
        {}
    )
    #get the Router result

    if route.get("audio"):
    #check if Audio Agent is required

        return "audio"
        #run the Audio Agent first

    if route.get("video"):
    #check if Video Agent is required

        return "video"
        #run the Video Agent

    if route.get("network"):
    #check if Network Agent is required

        return "network"
        #run the Network Agent

    return "evaluate"
    #go directly to evaluation if no specialist is selected


def route_after_audio(state: MASState) -> str:
#decide what happens after the Audio Agent

    """
    Decide the next workflow step after
    the Audio Agent.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """
    #describe the Audio routing decision

    if state.get("errors"):
    #check for errors

        return "fallback"
        #go to fallback if an error happened

    route = state.get(
        "router_result",
        {}
    )
    #get the Router decision

    if route.get("video"):
    #check if Video Agent is selected

        return "video"
        #run Video Agent next

    if route.get("network"):
    #check if Network Agent is selected

        return "network"
        #run Network Agent next

    return "risk"
    #calculate risk when all selected specialists are completed


def route_after_video(state: MASState) -> str:
#decide what happens after the Video Agent

    """
    Decide the next workflow step after
    the Video Agent.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """
    #describe the Video routing decision

    if state.get("errors"):
    #check for errors

        return "fallback"
        #go to fallback if an error happened

    route = state.get(
        "router_result",
        {}
    )
    #get the Router decision

    if route.get("network"):
    #check if Network Agent is selected

        return "network"
        #run Network Agent next

    return "risk"
    #calculate risk after the selected agents finish


def route_after_network(state: MASState) -> str:
#decide what happens after the Network Agent

    """
    Continue to risk calculation or activate fallback.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """
    #describe the Network routing decision

    if state.get("errors"):
    #check if the Network Agent created an error

        return "fallback"
        #go to fallback if an error happened

    return "risk"
    #continue to overall risk calculation


def route_after_risk(state: MASState) -> str:
#decide if Strategic Agent is needed

    """
    Route high-risk incidents to the Strategic Agent.

    Incidents with a threat score of 70 or greater
    receive strategic analysis.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """
    #describe the risk-based routing

    if state.get("errors"):
    #check if risk calculation created an error

        return "fallback"
        #go to fallback if there is an error

    score = state.get(
        "overall_threat_score",
        0
    )
    #get the overall threat score

    # Human modification 8:
    # A deterministic threshold controls whether the
    # expensive Strategic Agent is required.
    #use a fixed score threshold for Strategic Agent

    if score >= 70:
    #check if score is 70 or higher

        return "strategy"
        #activate the Strategic Agent

    return "evaluate"
    #skip Strategic Agent when score is below 70


def route_after_strategy(state: MASState) -> str:
#decide what happens after the Strategic Agent

    """
    Continue to evaluation after successful strategy
    generation or activate fallback after failure.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """
    #describe the strategy routing

    if state.get("errors"):
    #check if strategy created an error

        return "fallback"
        #go to fallback if strategy failed

    return "evaluate"
    #continue to self-evaluation


def route_after_evaluator(state: MASState) -> str:
#decide what happens after self-evaluation

    """
    End successful execution or activate fallback
    if evaluation failed.

    Args:
        state: Current MAS shared state.

    Returns:
        Name of the next workflow node.
    """
    #describe the evaluation routing

    if state.get("errors"):
    #check if evaluation created an error

        return "fallback"
        #go to fallback if evaluation failed

    return "end"
    #finish the workflow successfully


# =========================================================
# BUILD LANGGRAPH WORKFLOW
# =========================================================
#build the complete LangGraph workflow


def build_workflow():
#build and compile the workflow

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
    #describe the complete workflow

    workflow = StateGraph(
        MASState
    )
    #create the LangGraph using the shared MAS state

    # Add all workflow nodes.
    #add all nodes to the workflow

    workflow.add_node(
        "router",
        router_node
    )
    #add the Router node

    workflow.add_node(
        "audio",
        audio_node
    )
    #add the Audio Agent node

    workflow.add_node(
        "video",
        video_node
    )
    #add the Video Agent node

    workflow.add_node(
        "network",
        network_node
    )
    #add the Network Agent node

    workflow.add_node(
        "risk",
        risk_node
    )
    #add the risk calculation node

    workflow.add_node(
        "strategy",
        strategy_node
    )
    #add the Strategic Agent node

    workflow.add_node(
        "evaluate",
        evaluator_node
    )
    #add the Self-Evaluation Agent node

    workflow.add_node(
        "fallback",
        fallback_node
    )
    #add the fallback node

    workflow.set_entry_point(
        "router"
    )
    #start the workflow from the Router

    # -----------------------------------------------------
    # Conditional Route 1:
    # Router selects the required specialist agents.
    # -----------------------------------------------------
    #define the first conditional routing stage

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
    #connect Router to the correct next node

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
    #connect Audio Agent to the next step

    workflow.add_conditional_edges(
        "video",
        route_after_video,
        {
            "network": "network",
            "risk": "risk",
            "fallback": "fallback"
        }
    )
    #connect Video Agent to the next step

    workflow.add_conditional_edges(
        "network",
        route_after_network,
        {
            "risk": "risk",
            "fallback": "fallback"
        }
    )
    #connect Network Agent to risk or fallback

    # -----------------------------------------------------
    # Conditional Route 2:
    # Threat score determines strategic escalation.
    # -----------------------------------------------------
    #use the threat score to decide if strategy is needed

    workflow.add_conditional_edges(
        "risk",
        route_after_risk,
        {
            "strategy": "strategy",
            "evaluate": "evaluate",
            "fallback": "fallback"
        }
    )
    #connect risk calculation to strategy, evaluation or fallback

    # Strategy may succeed and continue to evaluation,
    # or fail and activate fallback.
    #handle the next step after strategy

    workflow.add_conditional_edges(
        "strategy",
        route_after_strategy,
        {
            "evaluate": "evaluate",
            "fallback": "fallback"
        }
    )
    #connect Strategy Agent to evaluation or fallback

    # Evaluation normally ends the workflow.
    # An evaluator failure is instead handled by fallback.
    #handle the final evaluation routing

    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluator,
        {
            "end": END,
            "fallback": "fallback"
        }
    )
    #finish the workflow or use fallback if evaluation fails

    workflow.add_edge(
        "fallback",
        END
    )
    #end the workflow after fallback

    return workflow.compile()
    #compile the workflow so it can be executed