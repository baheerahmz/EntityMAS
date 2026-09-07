"""Unit tests for the deterministic threat-analysis tools."""

from tools import ( #import the threat analysis tools
    extract_incident_indicators, #import the incident indicator function
    calculate_network_threat_score, #import the network threat score function
    calculate_overall_risk #import the overall risk calculation function
)


def test_audio_detection():
    """Test whether an audio-only incident is detected correctly."""

    result = extract_incident_indicators( #check the incident indicators
        "A suspicious audio message was received." #enter an audio incident
    )

    assert result["audio_detected"] is True #check audio is detected
    assert result["video_detected"] is False #check video is not detected
    assert result["network_detected"] is False #check network is not detected


def test_network_score():
    """Test the deterministic network threat scoring tool."""

    score = calculate_network_threat_score( #calculate the network threat score
        ["network", "intrusion"] #provide network threat indicators
    )

    assert score == 50 #check the score is 50


def test_overall_risk():
    """Test the overall multi-vector risk calculation."""

    audio = { #create the audio result
        "risk_level": "MEDIUM" #set the audio risk level
    }

    video = { #create the video result
        "risk_level": "MEDIUM" #set the video risk level
    }

    network = { #create the network result
        "risk_level": "MEDIUM", #set the network risk level
        "threat_score": 50 #set the network threat score
    }

    score = calculate_overall_risk( #calculate the overall risk score
        audio, #use the audio result
        video, #use the video result
        network #use the network result
    )

    assert score == 90 #check the overall score is 90