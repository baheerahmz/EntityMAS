"""Tests for fallback routing and safe partial responses."""

import llm_client

from fallback import create_fallback_response
from workflow import build_workflow


def enable_mock_mode(monkeypatch):
    """Enable predictable mock responses for workflow testing."""
    monkeypatch.setattr(
        llm_client,
        "MOCK_MODE",
        True
    )


def test_network_failure_activates_fallback(monkeypatch):
    """Route a simulated Network Agent failure to fallback."""
    enable_mock_mode(monkeypatch)

    app = build_workflow()

    initial_state = {
        "user_input": (
            "The Entity launched a coordinated attack "
            "involving a suspicious audio message, "
            "manipulated video footage, "
            "and a network intrusion."
        ),
        "errors": [],
        "simulate_failure": True
    }

    result = app.invoke(initial_state)

    fallback = result["fallback_result"]

    assert fallback["status"] == "PARTIAL"

    assert fallback["risk_warning"] == (
        "Fallback activated because a system component failed."
    )

    assert result["errors"]

    assert "Network Agent failure" in result["errors"][0]
    assert "Simulated Network Agent failure" in result["errors"][0]

    assert "Audio analysis completed." in fallback["available_results"]
    assert "Video analysis completed." in fallback["available_results"]

    assert fallback["fallback_execution_time"] < 5

    # The workflow must stop before strategy and evaluation.
    assert result.get("strategy_result", {}) == {}
    assert result.get("evaluation_result", {}) == {}


def test_fallback_preserves_available_result():
    """Report any successful specialist result during fallback."""
    fallback = create_fallback_response(
        errors=[
            "Video Agent failure: simulated error."
        ],
        audio_result={
            "risk_level": "MEDIUM"
        },
        video_result={},
        network_result={}
    )

    assert fallback["status"] == "PARTIAL"
    assert fallback["errors"]

    assert fallback["available_results"] == [
        "Audio analysis completed."
    ]

    assert fallback["fallback_execution_time"] < 5


def test_fallback_handles_no_completed_agents():
    """Return a safe warning when every specialist is unavailable."""
    fallback = create_fallback_response(
        errors=[
            "All specialist agents were unavailable."
        ],
        audio_result={},
        video_result={},
        network_result={}
    )

    assert fallback["status"] == "PARTIAL"

    assert fallback["available_results"] == [
        "No specialist analysis was successfully completed."
    ]

    assert fallback["recommendation"]
    assert fallback["fallback_execution_time"] < 5