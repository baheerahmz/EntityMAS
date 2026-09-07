"""Static incident-routing logic for selecting specialist agents."""

from typing import Dict, Any #import types for dictionaries and values

from tools import extract_incident_indicators #import the indicator detection tool


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

    if not isinstance(user_input, str): #check if the input is a string
        raise TypeError( #show an error for invalid input
            "Incident description must be provided as a string."
        )

    incident_text = user_input.strip() #remove extra spaces from the input

    if not incident_text: #check if the incident is empty
        return { #return all agents as false
            "audio": False, #audio agent is not activated
            "video": False, #video agent is not activated
            "network": False, #network agent is not activated
            "reason": ( #give the reason for no routing
                "No incident indicators were detected because "
                "the incident description was empty."
            ),
        }

    indicators = extract_incident_indicators( #detect threat indicators
        incident_text
    )

    audio_detected = indicators.get( #get the audio detection result
        "audio_detected",
        False #use false if no value is found
    )

    video_detected = indicators.get( #get the video detection result
        "video_detected",
        False #use false if no value is found
    )

    network_detected = indicators.get( #get the network detection result
        "network_detected",
        False #use false if no value is found
    )

    detected_agents = [] #create a list for activated agents

    if audio_detected: #check if audio threat is detected
        detected_agents.append("Audio Agent") #add Audio Agent to the list

    if video_detected: #check if video threat is detected
        detected_agents.append("Video Agent") #add Video Agent to the list

    if network_detected: #check if network threat is detected
        detected_agents.append("Network Agent") #add Network Agent to the list

    if detected_agents: #check if any agents were activated
        reason = ( #create the routing reason
            "Routing decision based on detected incident "
            "indicators. Activated: "
            + ", ".join(detected_agents) #join all activated agents
            + "."
        )
    else: #if no agents were activated
        reason = ( #create the reason for no detected threats
            "No recognised audio, video, or network "
            "indicators were detected."
        )

    return { #return the final routing decision
        "audio": audio_detected, #return audio routing result
        "video": video_detected, #return video routing result
        "network": network_detected, #return network routing result
        "reason": reason, #return the routing reason
    }