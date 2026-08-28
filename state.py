"""Shared LangGraph state definition for the multi-agent workflow."""

from typing import TypedDict, Dict, Any, List


class MASState(TypedDict, total=False):
    """
    Shared state passed between all agents in the
    Entity Multi-Agent System.
    """

    user_input: str

    router_result: Dict[str, Any]

    audio_result: Dict[str, Any]
    video_result: Dict[str, Any]
    network_result: Dict[str, Any]

    overall_threat_score: int

    strategy_result: Dict[str, Any]
    evaluation_result: Dict[str, Any]

    errors: List[str]

    simulate_failure: bool

    fallback_result: Dict[str, Any]