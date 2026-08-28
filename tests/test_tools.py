"""Unit tests for the deterministic threat-analysis tools."""

from tools import (
    extract_incident_indicators,
    calculate_network_threat_score,
    calculate_overall_risk
)


def test_audio_detection():
    """Test whether an audio-only incident is detected correctly."""

    result = extract_incident_indicators(
        "A suspicious audio message was received."
    )

    assert result["audio_detected"] is True
    assert result["video_detected"] is False
    assert result["network_detected"] is False


def test_network_score():
    """Test the deterministic network threat scoring tool."""

    score = calculate_network_threat_score(
        ["network", "intrusion"]
    )

    assert score == 50


def test_overall_risk():
    """Test the overall multi-vector risk calculation."""

    audio = {
        "risk_level": "MEDIUM"
    }

    video = {
        "risk_level": "MEDIUM"
    }

    network = {
        "risk_level": "MEDIUM",
        "threat_score": 50
    }

    score = calculate_overall_risk(
        audio,
        video,
        network
    )

    assert score == 90