"""Unit tests for static incident routing."""

from router import route_incident


def test_route_all_threat_categories():
    """Route a combined incident to all specialist agents."""
    incident = (
        "The Entity used a suspicious audio message, "
        "manipulated video footage, and a network intrusion."
    )

    result = route_incident(incident)

    assert result["audio"] is True
    assert result["video"] is True
    assert result["network"] is True


def test_route_audio_only():
    """Route an audio-only incident to the Audio Agent."""
    incident = (
        "A suspicious voice recording was received."
    )

    result = route_incident(incident)

    assert result["audio"] is True
    assert result["video"] is False
    assert result["network"] is False


def test_route_video_only():
    """Route a video-only incident to the Video Agent."""
    incident = (
        "Manipulated footage was discovered."
    )

    result = route_incident(incident)

    assert result["audio"] is False
    assert result["video"] is True
    assert result["network"] is False


def test_route_network_only():
    """Route a network-only incident to the Network Agent."""
    incident = (
        "An unauthorized network intrusion was detected."
    )

    result = route_incident(incident)

    assert result["audio"] is False
    assert result["video"] is False
    assert result["network"] is True


def test_route_no_detected_threat():
    """Do not activate specialists when no keywords are detected."""
    incident = (
        "A routine operational report was submitted."
    )

    result = route_incident(incident)

    assert result["audio"] is False
    assert result["video"] is False
    assert result["network"] is False


def test_routing_is_case_insensitive():
    """Detect threat indicators regardless of letter casing."""
    incident = (
        "AUDIO message and NETWORK INTRUSION were reported."
    )

    result = route_incident(incident)

    assert result["audio"] is True
    assert result["video"] is False
    assert result["network"] is True