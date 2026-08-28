"""Fallback-response generation for recoverable system failures."""

import time
from typing import Dict, Any, List


def create_fallback_response(
    errors: List[str],
    audio_result: Dict[str, Any],
    video_result: Dict[str, Any],
    network_result: Dict[str, Any]
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

    start_time = time.time()

    completed = []

    if audio_result:
        completed.append("Audio analysis completed.")

    if video_result:
        completed.append("Video analysis completed.")

    if network_result:
        completed.append("Network analysis completed.")

    if not completed:
        completed.append(
            "No specialist analysis was successfully completed."
        )

    elapsed_time = time.time() - start_time

    return {
        "status": "PARTIAL",

        "risk_warning":
            "Fallback activated because a system component failed.",

        "errors": errors,

        "available_results": completed,

        "recommendation":
            "Treat the incident as high risk, preserve available evidence, "
            "contain affected systems, and escalate for manual review.",

        "fallback_execution_time":
            round(elapsed_time, 4)
    }