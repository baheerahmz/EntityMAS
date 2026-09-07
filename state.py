"""Shared LangGraph state definition for the multi-agent workflow."""

from typing import TypedDict, Dict, Any, List #import types for the shared state


class MASState(TypedDict, total=False): #define the shared state structure
    """
    Shared state passed between all agents in the
    Entity Multi-Agent System.
    """

    user_input: str #store the original incident description

    router_result: Dict[str, Any] #store the Router decision

    audio_result: Dict[str, Any] #store the Audio Agent result
    video_result: Dict[str, Any] #store the Video Agent result
    network_result: Dict[str, Any] #store the Network Agent result

    overall_threat_score: int #store the calculated overall threat score

    strategy_result: Dict[str, Any] #store the Strategic Agent result
    evaluation_result: Dict[str, Any] #store the Self-Evaluation result

    errors: List[str] #store any errors during the workflow

    simulate_failure: bool #control whether failure simulation is enabled

    fallback_result: Dict[str, Any] #store the fallback response