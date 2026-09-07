"""Unit tests for static incident routing."""

from router import route_incident #import the incident routing function


def test_route_all_threat_categories():
    """Route a combined incident to all specialist agents."""
    incident = ( #enter an incident with all threat types
        "The Entity used a suspicious audio message, "
        "manipulated video footage, and a network intrusion."
    )

    result = route_incident(incident) #route the incident

    assert result["audio"] is True #check Audio Agent is activated
    assert result["video"] is True #check Video Agent is activated
    assert result["network"] is True #check Network Agent is activated


def test_route_audio_only():
    """Route an audio-only incident to the Audio Agent."""
    incident = ( #enter an audio-only incident
        "A suspicious voice recording was received."
    )

    result = route_incident(incident) #route the incident

    assert result["audio"] is True #check Audio Agent is activated
    assert result["video"] is False #check Video Agent is not activated
    assert result["network"] is False #check Network Agent is not activated


def test_route_video_only():
    """Route a video-only incident to the Video Agent."""
    incident = ( #enter a video-only incident
        "Manipulated footage was discovered."
    )

    result = route_incident(incident) #route the incident

    assert result["audio"] is False #check Audio Agent is not activated
    assert result["video"] is True #check Video Agent is activated
    assert result["network"] is False #check Network Agent is not activated


def test_route_network_only():
    """Route a network-only incident to the Network Agent."""
    incident = ( #enter a network-only incident
        "An unauthorized network intrusion was detected."
    )

    result = route_incident(incident) #route the incident

    assert result["audio"] is False #check Audio Agent is not activated
    assert result["video"] is False #check Video Agent is not activated
    assert result["network"] is True #check Network Agent is activated


def test_route_no_detected_threat():
    """Do not activate specialists when no keywords are detected."""
    incident = ( #enter an incident with no threat keywords
        "A routine operational report was submitted."
    )

    result = route_incident(incident) #route the incident

    assert result["audio"] is False #check Audio Agent is not activated
    assert result["video"] is False #check Video Agent is not activated
    assert result["network"] is False #check Network Agent is not activated


def test_routing_is_case_insensitive():
    """Detect threat indicators regardless of letter casing."""
    incident = ( #enter an incident with uppercase keywords
        "AUDIO message and NETWORK INTRUSION were reported."
    )

    result = route_incident(incident) #route the incident

    assert result["audio"] is True #check Audio Agent detects the keyword
    assert result["video"] is False #check Video Agent is not activated
    assert result["network"] is True #check Network Agent detects the keyword