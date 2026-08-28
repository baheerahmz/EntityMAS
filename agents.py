"""Specialist agent implementations for the Entity Multi-Agent System."""

from typing import Dict, Any

from tools import (
    calculate_overall_risk,
    calculate_network_threat_score,
    extract_incident_indicators
)

from prompts import (
    AUDIO_PROMPT,
    VIDEO_PROMPT,
    NETWORK_PROMPT,
    STRATEGY_PROMPT,
    EVALUATOR_PROMPT
)

from llm_client import call_llm


def audio_agent(
    user_input: str
) -> Dict[str, Any]:
    """
    Analyse only audio-related evidence.

    Args:
        user_input: Original incident description.

    Returns:
        Structured Audio Agent result.
    """

    evidence = extract_incident_indicators(
        user_input
    )

    audio_input = f"""
AUDIO EVIDENCE:
{evidence["audio_evidence"]}

DETECTED AUDIO INDICATORS:
{evidence["audio_indicators"]}

IMPORTANT:
Analyse only the evidence above.
Do not use video or network information.
"""

    # Human modification 1:
    # Only audio-specific evidence is supplied to reduce
    # cross-domain hallucination.
    result = call_llm(
        system_prompt=AUDIO_PROMPT,
        user_input=audio_input,
        agent_type="audio"
    )

    if not result.get("analysis_result"):
        result["analysis_result"] = (
            "A suspicious audio message was reported, "
            "but insufficient acoustic evidence was supplied "
            "to confirm synthetic manipulation."
        )

    return result


def video_agent(
    user_input: str
) -> Dict[str, Any]:
    """
    Analyse only video-related evidence.

    Args:
        user_input: Original incident description.

    Returns:
        Structured Video Agent result.
    """

    evidence = extract_incident_indicators(
        user_input
    )

    video_input = f"""
VIDEO EVIDENCE:
{evidence["video_evidence"]}

DETECTED VIDEO INDICATORS:
{evidence["video_indicators"]}

IMPORTANT:
Analyse only the evidence above.
Do not use audio or network information.
"""

    # Human modification 2:
    # Video Agent receives only video-related evidence.
    result = call_llm(
        system_prompt=VIDEO_PROMPT,
        user_input=video_input,
        agent_type="video"
    )

    if not result.get("analysis_result"):
        result["analysis_result"] = (
            "Manipulated video footage was reported, "
            "but no specific forensic visual indicators were supplied "
            "to independently verify the manipulation."
        )

    return result


def network_agent(
    user_input: str,
    simulate_failure: bool = False
) -> Dict[str, Any]:
    """
    Analyse only network-related evidence.

    Args:
        user_input: Original incident description.
        simulate_failure: Trigger controlled fallback testing.

    Returns:
        Structured Network Agent result.

    Raises:
        ConnectionError: When simulated failure is enabled.
    """

    if simulate_failure:
        raise ConnectionError(
            "Simulated Network Agent failure."
        )

    evidence = extract_incident_indicators(
        user_input
    )

    network_indicators = evidence[
        "network_indicators"
    ]

    # Human modification 3:
    # Threat score is calculated deterministically rather
    # than allowing the LLM to invent a number.
    calculated_score = calculate_network_threat_score(
        network_indicators
    )

    network_input = f"""
NETWORK EVIDENCE:
{evidence["network_evidence"]}

DETECTED NETWORK INDICATORS:
{network_indicators}

DETERMINISTIC THREAT SCORE:
{calculated_score}

IMPORTANT:
The numerical threat score was calculated by a trusted
local Python tool.

Do not modify the score.
Do not invent additional network evidence.
"""

    result = call_llm(
        system_prompt=NETWORK_PROMPT,
        user_input=network_input,
        agent_type="network"
    )

    # Human modification 4:
    # Tool-generated threat score remains authoritative.
    result["threat_score"] = calculated_score

    if not result.get("attack_vector"):
        result["attack_vector"] = (
            "Reported network intrusion "
            "(specific attack vector unknown)"
        )

    if not result.get("recommended_actions"):
        result["recommended_actions"] = [
            "Preserve relevant network and security logs",
            "Increase monitoring for anomalous activity",
            "Review authentication and access records",
            "Escalate the incident for technical investigation"
        ]

    return result


def strategy_agent(
    audio_result: Dict[str, Any],
    video_result: Dict[str, Any],
    network_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Combine available specialist findings into
    an overall defensive strategy.

    Args:
        audio_result: Audio Agent result.
        video_result: Video Agent result.
        network_result: Network Agent result.

    Returns:
        Structured Strategic Agent result.
    """

    combined_input = f"""
AVAILABLE AUDIO RESULT:
{audio_result}

AVAILABLE VIDEO RESULT:
{video_result}

AVAILABLE NETWORK RESULT:
{network_result}

IMPORTANT:
Empty dictionaries mean that the corresponding
specialist was not required or was not executed.

Do not invent missing specialist findings.
"""

    # Human modification 5:
    # Strategic Agent receives specialist outputs rather
    # than re-analysing raw evidence.
    result = call_llm(
        system_prompt=STRATEGY_PROMPT,
        user_input=combined_input,
        agent_type="strategy"
    )

    if not result.get("attack_objective"):
        result["attack_objective"] = (
            "The exact attack objective is unclear "
            "from the available evidence."
        )

    if not result.get("likely_next_move"):
        result["likely_next_move"] = (
            "Further malicious activity is possible, "
            "but there is insufficient evidence to "
            "predict a specific next action."
        )

    if not result.get("strategy"):
        result["strategy"] = [
            "Preserve available evidence",
            "Investigate the reported threat",
            "Apply proportionate precautionary controls"
        ]

    return result


def evaluator_agent(
    user_input: str,
    router_result: Dict[str, Any],
    audio_result: Dict[str, Any],
    video_result: Dict[str, Any],
    network_result: Dict[str, Any],
    strategy_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate whether all Router-selected threat categories
    were correctly handled.

    Args:
        user_input: Original incident description.
        router_result: Router's selected threat categories.
        audio_result: Audio Agent result.
        video_result: Video Agent result.
        network_result: Network Agent result.
        strategy_result: Strategic Agent result.

    Returns:
        Structured evaluation result.
    """

    combined_input = f"""
ORIGINAL INCIDENT:
{user_input}

ROUTER RESULT:
{router_result}

AUDIO RESULT:
{audio_result}

VIDEO RESULT:
{video_result}

NETWORK RESULT:
{network_result}

STRATEGY RESULT:
{strategy_result}

IMPORTANT:
Only evaluate threat categories marked True
in the ROUTER RESULT.

Do not penalise the system for intentionally
skipping agents whose Router value is False.
"""

    result = call_llm(
        system_prompt=EVALUATOR_PROMPT,
        user_input=combined_input,
        agent_type="evaluator"
    )

    # Human modification 6:
    # Some local-model responses return PASS but leave
    # final_summary blank. Generate a grounded summary
    # from the actual Router-selected results.
    if not result.get("final_summary"):

        selected = []

        if router_result.get("audio"):
            selected.append("audio")

        if router_result.get("video"):
            selected.append("video")

        if router_result.get("network"):
            selected.append("network")

        selected_text = ", ".join(selected)

        result["final_summary"] = (
            f"The system successfully evaluated the "
            f"Router-selected threat category/categories: "
            f"{selected_text}. "
            f"Unselected specialist agents were intentionally skipped, "
            f"and the available evidence was handled with appropriate "
            f"uncertainty."
        )

    return result


def overall_risk_agent(
    audio_result: Dict[str, Any],
    video_result: Dict[str, Any],
    network_result: Dict[str, Any]
) -> int:
    """
    Calculate overall coordinated-attack risk.

    Args:
        audio_result: Audio Agent result.
        video_result: Video Agent result.
        network_result: Network Agent result.

    Returns:
        Integer risk score between 0 and 100.
    """

    # Human modification 7:
    # Overall escalation uses deterministic logic
    # instead of an LLM-only decision.
    score = calculate_overall_risk(
        audio_result,
        video_result,
        network_result
    )

    return score