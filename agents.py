"""Specialist agent implementations for the Entity Multi-Agent System."""

from typing import Dict, Any #import typing tools

from tools import ( #import the required analysis tools
    calculate_overall_risk, #import overall risk calculation
    calculate_network_threat_score, #import network threat score calculation
    extract_incident_indicators #import incident indicator extraction
)

from prompts import ( #import the agent prompts
    AUDIO_PROMPT, #import Audio Agent prompt
    VIDEO_PROMPT, #import Video Agent prompt
    NETWORK_PROMPT, #import Network Agent prompt
    STRATEGY_PROMPT, #import Strategy Agent prompt
    EVALUATOR_PROMPT #import Evaluator Agent prompt
)

from llm_client import call_llm #import the LLM calling function


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

    evidence = extract_incident_indicators( #extract threat indicators
        user_input #use the incident description
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

    #Human modification 1:
    #Only audio-specific evidence is supplied to reduce
    #cross-domain hallucination.
    result = call_llm( #call the LLM for audio analysis
        system_prompt=AUDIO_PROMPT, #use the Audio Agent prompt
        user_input=audio_input, #send audio evidence to the LLM
        agent_type="audio" #identify the agent type
    )

    if not result.get("analysis_result"): #check if analysis result is missing
        result["analysis_result"] = ( #add a safe default analysis
            "A suspicious audio message was reported, "
            "but insufficient acoustic evidence was supplied "
            "to confirm synthetic manipulation."
        )

    return result #return the Audio Agent result


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

    evidence = extract_incident_indicators( #extract threat indicators
        user_input #use the incident description
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

    #Human modification 2:
    #Video Agent receives only video-related evidence.
    result = call_llm( #call the LLM for video analysis
        system_prompt=VIDEO_PROMPT, #use the Video Agent prompt
        user_input=video_input, #send video evidence to the LLM
        agent_type="video" #identify the agent type
    )

    if not result.get("analysis_result"): #check if analysis result is missing
        result["analysis_result"] = ( #add a safe default analysis
            "Manipulated video footage was reported, "
            "but no specific forensic visual indicators were supplied "
            "to independently verify the manipulation."
        )

    return result #return the Video Agent result


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

    if simulate_failure: #check if failure simulation is enabled
        raise ConnectionError( #raise a controlled error
            "Simulated Network Agent failure."
        )

    evidence = extract_incident_indicators( #extract threat indicators
        user_input #use the incident description
    )

    network_indicators = evidence[ #get the network indicators
        "network_indicators"
    ]

    #Human modification 3:
    #Threat score is calculated deterministically rather
    #than allowing the LLM to invent a number.
    calculated_score = calculate_network_threat_score( #calculate the network score
        network_indicators #use detected network indicators
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

    result = call_llm( #call the LLM for network analysis
        system_prompt=NETWORK_PROMPT, #use the Network Agent prompt
        user_input=network_input, #send network evidence to the LLM
        agent_type="network" #identify the agent type
    )

    #Human modification 4:
    #Tool-generated threat score remains authoritative.
    result["threat_score"] = calculated_score #keep the calculated score

    if not result.get("attack_vector"): #check if attack vector is missing
        result["attack_vector"] = ( #add a safe default attack vector
            "Reported network intrusion "
            "(specific attack vector unknown)"
        )

    if not result.get("recommended_actions"): #check if actions are missing
        result["recommended_actions"] = [ #add default recommended actions
            "Preserve relevant network and security logs",
            "Increase monitoring for anomalous activity",
            "Review authentication and access records",
            "Escalate the incident for technical investigation"
        ]

    return result #return the Network Agent result


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

    #Human modification 5:
    #Strategic Agent receives specialist outputs rather
    #than re-analysing raw evidence.
    result = call_llm( #call the LLM for strategic analysis
        system_prompt=STRATEGY_PROMPT, #use the Strategy Agent prompt
        user_input=combined_input, #send specialist results
        agent_type="strategy" #identify the agent type
    )

    if not result.get("attack_objective"): #check if attack objective is missing
        result["attack_objective"] = ( #add a safe default objective
            "The exact attack objective is unclear "
            "from the available evidence."
        )

    if not result.get("likely_next_move"): #check if next move is missing
        result["likely_next_move"] = ( #add an uncertain prediction
            "Further malicious activity is possible, "
            "but there is insufficient evidence to "
            "predict a specific next action."
        )

    if not result.get("strategy"): #check if strategy is missing
        result["strategy"] = [ #add default defensive strategies
            "Preserve available evidence",
            "Investigate the reported threat",
            "Apply proportionate precautionary controls"
        ]

    return result #return the Strategy Agent result


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

    result = call_llm( #call the LLM for evaluation
        system_prompt=EVALUATOR_PROMPT, #use the Evaluator prompt
        user_input=combined_input, #send all relevant results
        agent_type="evaluator" #identify the agent type
    )

    #Human modification 6:
    #Some local-model responses return PASS but leave
    #final_summary blank. Generate a grounded summary
    #from the actual Router-selected results.
    if not result.get("final_summary"): #check if final summary is missing

        selected = [] #create a list for selected categories

        if router_result.get("audio"): #check if Audio was selected
            selected.append("audio") #add audio to the list

        if router_result.get("video"): #check if Video was selected
            selected.append("video") #add video to the list

        if router_result.get("network"): #check if Network was selected
            selected.append("network") #add network to the list

        selected_text = ", ".join(selected) #combine selected categories

        result["final_summary"] = ( #create a grounded final summary
            f"The system successfully evaluated the "
            f"Router-selected threat category/categories: "
            f"{selected_text}. "
            f"Unselected specialist agents were intentionally skipped, "
            f"and the available evidence was handled with appropriate "
            f"uncertainty."
        )

    return result #return the evaluation result


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

    #Human modification 7:
    #Overall escalation uses deterministic logic
    #instead of an LLM-only decision.
    score = calculate_overall_risk( #calculate the overall risk score
        audio_result, #use the Audio result
        video_result, #use the Video result
        network_result #use the Network result
    )

    return score #return the final risk score