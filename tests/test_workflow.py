"""Integration tests for the complete LangGraph workflow."""

import llm_client

from workflow import build_workflow


def enable_mock_mode(monkeypatch):
    """Enable predictable mock LLM responses during testing."""
    monkeypatch.setattr(
        llm_client,
        "MOCK_MODE",
        True
    )


def test_complete_multivector_workflow(monkeypatch):
    """Execute all specialists for a combined incident."""
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
        "simulate_failure": False
    }

    result = app.invoke(initial_state)

    assert result["router_result"]["audio"] is True
    assert result["router_result"]["video"] is True
    assert result["router_result"]["network"] is True

    assert result["audio_result"]["risk_level"] == "HIGH"
    assert result["video_result"]["risk_level"] == "HIGH"
    assert result["network_result"]["risk_level"] == "HIGH"

    assert result["overall_threat_score"] == 100

    assert result["strategy_result"]["next_step"] == "evaluate"
    assert result["evaluation_result"]["status"] == "PASS"

    assert result["errors"] == []


def test_audio_only_workflow(monkeypatch):
    """Execute only the Audio Agent for an audio incident."""
    enable_mock_mode(monkeypatch)

    app = build_workflow()

    initial_state = {
        "user_input": (
            "A suspicious audio message was received."
        ),
        "errors": [],
        "simulate_failure": False
    }

    result = app.invoke(initial_state)

    assert result["router_result"]["audio"] is True
    assert result["router_result"]["video"] is False
    assert result["router_result"]["network"] is False

    assert result["audio_result"]["risk_level"] == "HIGH"

    assert result.get("video_result", {}) == {}
    assert result.get("network_result", {}) == {}

    assert result["overall_threat_score"] == 30

    # A score below 70 must skip the Strategic Agent.
    assert result.get("strategy_result", {}) == {}

    assert result["evaluation_result"]["status"] == "PASS"
    assert result["errors"] == []


def test_network_only_workflow(monkeypatch):
    """Execute only the Network Agent for a network incident."""
    enable_mock_mode(monkeypatch)

    app = build_workflow()

    initial_state = {
        "user_input": (
            "A network intrusion was reported."
        ),
        "errors": [],
        "simulate_failure": False
    }

    result = app.invoke(initial_state)

    assert result["router_result"]["audio"] is False
    assert result["router_result"]["video"] is False
    assert result["router_result"]["network"] is True

    assert result.get("audio_result", {}) == {}
    assert result.get("video_result", {}) == {}

    assert result["network_result"]["risk_level"] == "HIGH"
    assert result["network_result"]["threat_score"] == 50

    assert result["overall_threat_score"] == 40

    # A score below 70 must skip the Strategic Agent.
    assert result.get("strategy_result", {}) == {}

    assert result["evaluation_result"]["status"] == "PASS"
    assert result["errors"] == []