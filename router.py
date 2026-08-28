"""Static incident-routing logic for selecting specialist agents."""

from typing import Dict, Any

from tools import extract_incident_indicators


def route_incident(user_input: str) -> Dict[str, Any]:
    """
    Analyse an incident description and determine which
    specialist agents should be activated.

    The router uses deterministic indicator detection to
    identify whether the incident contains audio, video,
    or network-related evidence.

    Args:
        user_input: The original incident description.

    Returns:
        A dictionary containing routing decisions for the
        Audio, Video, and Network specialist agents.
    """

    if not isinstance(user_input, str):
        raise TypeError(
            "Incident description must be provided as a string."
        )

    incident_text = user_input.strip()

    if not incident_text:
        return {
            "audio": False,
            "video": False,
            "network": False,
            "reason": (
                "No incident indicators were detected because "
                "the incident description was empty."
            ),
        }

    indicators = extract_incident_indicators(
        incident_text
    )

    audio_detected = indicators.get(
        "audio_detected",
        False
    )

    video_detected = indicators.get(
        "video_detected",
        False
    )

    network_detected = indicators.get(
        "network_detected",
        False
    )

    detected_agents = []

    if audio_detected:
        detected_agents.append("Audio Agent")

    if video_detected:
        detected_agents.append("Video Agent")

    if network_detected:
        detected_agents.append("Network Agent")

    if detected_agents:
        reason = (
            "Routing decision based on detected incident "
            "indicators. Activated: "
            + ", ".join(detected_agents)
            + "."
        )
    else:
        reason = (
            "No recognised audio, video, or network "
            "indicators were detected."
        )

    return {
        "audio": audio_detected,
        "video": video_detected,
        "network": network_detected,
        "reason": reason,
    }