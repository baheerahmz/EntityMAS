"""Fallback-response generation for recoverable system failures."""

import time #import the time module
from typing import Dict, Any, List #import typing tools


def create_fallback_response(
    errors: List[str], #receive the error messages
    audio_result: Dict[str, Any], #receive the Audio Agent result
    video_result: Dict[str, Any], #receive the Video Agent result
    network_result: Dict[str, Any] #receive the Network Agent result
) -> Dict[str, Any]:
    """
    Create a safe partial response when one or more
    Multi-Agent System components fail.

    Args:
        errors: List of captured error messages.
        audio_result: Available Audio Agent result.
        video_result: Available Video Agent result.
        network_result: Available Network Agent result.

    Returns:
        A dictionary containing the fallback status,
        risk warning, available specialist results,
        recommendation, errors, and execution time.
    """

    start_time = time.time() #record the starting time

    completed = [] #create a list for completed agents

    if audio_result: #check if Audio Agent completed
        completed.append("Audio analysis completed.") #add Audio result

    if video_result: #check if Video Agent completed
        completed.append("Video analysis completed.") #add Video result

    if network_result: #check if Network Agent completed
        completed.append("Network analysis completed.") #add Network result

    if not completed: #check if no agent completed
        completed.append( #add a message when no result is available
            "No specialist analysis was successfully completed."
        )

    elapsed_time = time.time() - start_time #calculate the execution time

    return { #return the fallback response
        "status": "PARTIAL", #set the status as partial

        "risk_warning": #add a warning about the system failure
            "Fallback activated because a system component failed.",

        "errors": errors, #include the captured errors

        "available_results": completed, #include the available results

        "recommendation": #provide a safe recommendation
            "Treat the incident as high risk, preserve available evidence, "
            "contain affected systems, and escalate for manual review.",

        "fallback_execution_time": #include the fallback execution time
            round(elapsed_time, 4) #round the time to 4 decimal places
    }