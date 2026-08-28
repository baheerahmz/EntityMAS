"""Deterministic tools for indicator extraction and threat scoring."""

from typing import Dict, List, Any


def extract_incident_indicators(
    text: str
) -> Dict[str, Any]:
    """
    Detect audio, video, and network-related indicators
    from the user's incident description.

    Args:
        text: Original incident description.

    Returns:
        Dictionary containing detected categories,
        relevant indicators, and supporting evidence
        for each category.
    """

    lowered_text = text.lower()

    audio_keywords = [
        "audio",
        "voice",
        "speech",
        "recording",
        "voicemail",
        "deepfake audio"
    ]

    video_keywords = [
        "video",
        "footage",
        "deepfake video",
        "manipulated video",
        "lip-sync",
        "frame"
    ]

    network_keywords = [
        "network",
        "intrusion",
        "login",
        "admin",
        "administrator",
        "account",
        "malware",
        "phishing",
        "password"
    ]

    audio_found = [
        word
        for word in audio_keywords
        if word in lowered_text
    ]

    video_found = [
        word
        for word in video_keywords
        if word in lowered_text
    ]

    network_found = [
        word
        for word in network_keywords
        if word in lowered_text
    ]

    return {
        "audio_detected": bool(audio_found),
        "video_detected": bool(video_found),
        "network_detected": bool(network_found),

        "audio_indicators": audio_found,
        "video_indicators": video_found,
        "network_indicators": network_found,

        "audio_evidence": (
            "A suspicious audio-related indicator was detected."
            if audio_found
            else ""
        ),

        "video_evidence": (
            "A suspicious video-related indicator was detected."
            if video_found
            else ""
        ),

        "network_evidence": (
            "A suspicious network-related indicator was detected."
            if network_found
            else ""
        )
    }


def calculate_network_threat_score(
    indicators: List[str]
) -> int:
    """
    Calculate a deterministic network threat score.

    Each detected network indicator contributes
    a predefined weight to the total threat score.

    Args:
        indicators: Detected network indicators.

    Returns:
        Integer score between 0 and 100.
    """

    weights = {
        "network": 20,
        "intrusion": 30,
        "login": 15,
        "admin": 25,
        "administrator": 25,
        "account": 15,
        "malware": 35,
        "phishing": 25,
        "password": 20
    }

    score = 0

    unique_indicators = set(
        indicators
    )

    for indicator in unique_indicators:
        score += weights.get(
            indicator,
            5
        )

    return min(
        score,
        100
    )


def calculate_overall_risk(
    audio_result: Dict[str, Any],
    video_result: Dict[str, Any],
    network_result: Dict[str, Any]
) -> int:
    """
    Calculate the overall coordinated-attack risk score.

    The calculation combines specialist-agent risk levels,
    part of the deterministic network threat score, and
    an additional coordination penalty when multiple threat
    categories are simultaneously active.

    Agents that were not selected contribute zero points.

    Args:
        audio_result: Audio Agent result.
        video_result: Video Agent result.
        network_result: Network Agent result.

    Returns:
        Integer overall risk score between 0 and 100.
    """

    score = 0

    audio_risk = audio_result.get(
        "risk_level"
    )

    video_risk = video_result.get(
        "risk_level"
    )

    network_risk = network_result.get(
        "risk_level"
    )

    network_score = network_result.get(
        "threat_score",
        0
    )

    risk_weights = {
        "LOW": 5,
        "MEDIUM": 20,
        "HIGH": 30
    }

    score += risk_weights.get(
        audio_risk,
        0
    )

    score += risk_weights.get(
        video_risk,
        0
    )

    score += risk_weights.get(
        network_risk,
        0
    )

    # Include 20% of the deterministic
    # network threat score.
    score += int(
        network_score * 0.2
    )

    active_threats = 0

    if audio_risk in [
        "MEDIUM",
        "HIGH"
    ]:
        active_threats += 1

    if video_risk in [
        "MEDIUM",
        "HIGH"
    ]:
        active_threats += 1

    if network_risk in [
        "MEDIUM",
        "HIGH"
    ]:
        active_threats += 1

    # Multiple simultaneous threats indicate a
    # potentially coordinated attack and therefore
    # increase the overall operational risk.
    if active_threats == 2:
        score += 10

    elif active_threats >= 3:
        score += 20

    return min(
        score,
        100
    )