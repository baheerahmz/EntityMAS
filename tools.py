"""Deterministic tools for indicator extraction and threat scoring."""

from typing import Dict, List, Any #import types for the functions


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

    lowered_text = text.lower() #convert the text to lowercase

    audio_keywords = [ #list of audio-related keywords
        "audio",
        "voice",
        "speech",
        "recording",
        "voicemail",
        "deepfake audio"
    ]

    video_keywords = [ #list of video-related keywords
        "video",
        "footage",
        "deepfake video",
        "manipulated video",
        "lip-sync",
        "frame"
    ]

    network_keywords = [ #list of network-related keywords
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

    audio_found = [ #find audio keywords in the incident
        word
        for word in audio_keywords
        if word in lowered_text
    ]

    video_found = [ #find video keywords in the incident
        word
        for word in video_keywords
        if word in lowered_text
    ]

    network_found = [ #find network keywords in the incident
        word
        for word in network_keywords
        if word in lowered_text
    ]

    return { #return all detected indicators
        "audio_detected": bool(audio_found), #check if audio was detected
        "video_detected": bool(video_found), #check if video was detected
        "network_detected": bool(network_found), #check if network was detected

        "audio_indicators": audio_found, #return audio indicators
        "video_indicators": video_found, #return video indicators
        "network_indicators": network_found, #return network indicators

        "audio_evidence": ( #create audio evidence message
            "A suspicious audio-related indicator was detected."
            if audio_found
            else ""
        ),

        "video_evidence": ( #create video evidence message
            "A suspicious video-related indicator was detected."
            if video_found
            else ""
        ),

        "network_evidence": ( #create network evidence message
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

    weights = { #assign a threat weight to each indicator
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

    score = 0 #start the threat score at zero

    unique_indicators = set( #remove duplicate indicators
        indicators
    )

    for indicator in unique_indicators: #check each unique indicator
        score += weights.get( #add the weight to the score
            indicator,
            5 #use 5 if the indicator is not in the weights
        )

    return min( #return the score without exceeding 100
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

    score = 0 #start the overall score at zero

    audio_risk = audio_result.get( #get the Audio Agent risk level
        "risk_level"
    )

    video_risk = video_result.get( #get the Video Agent risk level
        "risk_level"
    )

    network_risk = network_result.get( #get the Network Agent risk level
        "risk_level"
    )

    network_score = network_result.get( #get the network threat score
        "threat_score",
        0 #use zero if no network score exists
    )

    risk_weights = { #set points for each risk level
        "LOW": 5,
        "MEDIUM": 20,
        "HIGH": 30
    }

    score += risk_weights.get( #add Audio risk points
        audio_risk,
        0 #use zero if no risk level exists
    )

    score += risk_weights.get( #add Video risk points
        video_risk,
        0 #use zero if no risk level exists
    )

    score += risk_weights.get( #add Network risk points
        network_risk,
        0 #use zero if no risk level exists
    )

    #Include 20% of the deterministic
    #network threat score.
    score += int( #add part of the network threat score
        network_score * 0.2
    )

    active_threats = 0 #count the active threat categories

    if audio_risk in [ #check if Audio has an active risk
        "MEDIUM",
        "HIGH"
    ]:
        active_threats += 1 #increase the active threat count

    if video_risk in [ #check if Video has an active risk
        "MEDIUM",
        "HIGH"
    ]:
        active_threats += 1 #increase the active threat count

    if network_risk in [ #check if Network has an active risk
        "MEDIUM",
        "HIGH"
    ]:
        active_threats += 1 #increase the active threat count

    #Multiple simultaneous threats indicate a
    #potentially coordinated attack and therefore
    #increase the overall operational risk.
    if active_threats == 2: #check if two threats are active
        score += 10 #add a coordination penalty

    elif active_threats >= 3: #check if three or more threats are active
        score += 20 #add a higher coordination penalty

    return min( #return the final score without exceeding 100
        score,
        100
    )